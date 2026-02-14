import { getSupabase, json, error, type Env } from '../../lib/supabase';
import { chatWithClaude } from '../../lib/claude';
import { buildSystemPrompt } from '../../lib/system-prompt';
import { extractMemories, storeMemories } from '../../lib/memory-agent';

interface SendRequest {
  message: string;
  conversation_id: string | null;
  teacher_id: string;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = (await context.request.json()) as SendRequest;

  if (!body.message?.trim()) {
    return error('Nachricht fehlt');
  }
  if (!body.teacher_id) {
    return error('Nicht angemeldet', 401);
  }

  const supabase = getSupabase(context.env);
  const teacherId = body.teacher_id;
  let conversationId = body.conversation_id;

  // Create conversation if new
  if (!conversationId) {
    const convResult = await supabase
      .from('conversations')
      .insert({ user_id: teacherId, title: body.message.slice(0, 80) });

    const conv = (convResult.data as { id: string }[] | null)?.[0];
    if (convResult.error || !conv) {
      return error('Konversation konnte nicht erstellt werden', 500);
    }
    conversationId = conv.id;
  }

  // Store user message
  await supabase.from('messages').insert({
    conversation_id: conversationId,
    role: 'user',
    content: body.message,
  });

  // Load conversation history (last 20 messages)
  const historyResult = await supabase
    .from('messages')
    .select('role, content, created_at')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: true })
    .limit(20);

  const history = (historyResult.data ?? []) as { role: string; content: string }[];
  const messages = history.map((m) => ({
    role: m.role as 'user' | 'assistant',
    content: m.content,
  }));

  // Build system prompt (Zone 1)
  const systemPrompt = await buildSystemPrompt(supabase, teacherId);

  // Call Claude
  let assistantText: string;
  try {
    const result = await chatWithClaude(context.env, systemPrompt, messages);
    assistantText = result.text;
  } catch (err) {
    console.error('Claude error:', err);
    return error('KI-Antwort fehlgeschlagen', 500);
  }

  // Store assistant message
  const saveResult = await supabase
    .from('messages')
    .insert({
      conversation_id: conversationId,
      role: 'assistant',
      content: assistantText,
    });

  const savedMsg = ((saveResult.data as { id: string; created_at: string }[] | null) ?? [])[0];

  // Async: Run memory agent (fire-and-forget via waitUntil)
  const conversationContext = messages
    .slice(-6)
    .map((m) => `${m.role}: ${m.content}`)
    .join('\n');

  context.waitUntil(
    extractMemories(context.env, conversationContext).then((result) =>
      storeMemories(supabase, teacherId, result, conversationId!),
    ).catch((err) => console.error('Memory agent error:', err)),
  );

  return json({
    conversation_id: conversationId,
    message: {
      id: savedMsg?.id ?? `msg-${Date.now()}`,
      role: 'assistant',
      content: assistantText,
      timestamp: savedMsg?.created_at ?? new Date().toISOString(),
    },
  });
};
