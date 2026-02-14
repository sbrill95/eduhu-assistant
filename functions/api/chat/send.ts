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

  const db = getSupabase(context.env);
  const teacherId = body.teacher_id;
  let conversationId = body.conversation_id;

  // Create conversation if new
  if (!conversationId) {
    const { data, error: convErr } = await db.insert<{ id: string }[]>(
      'conversations',
      { user_id: teacherId, title: body.message.slice(0, 80) },
    );
    const conv = Array.isArray(data) ? data[0] : data;
    if (convErr || !conv) {
      return error('Konversation konnte nicht erstellt werden', 500);
    }
    conversationId = conv.id;
  }

  // Store user message
  await db.insert('messages', {
    conversation_id: conversationId,
    role: 'user',
    content: body.message,
  });

  // Load conversation history (last 20 messages)
  const { data: history } = await db.select<{ role: string; content: string }[]>(
    'messages',
    {
      columns: 'role, content',
      filters: { conversation_id: conversationId },
      order: { col: 'created_at', asc: true },
      limit: 20,
    },
  );

  const messages = (history ?? []).map((m) => ({
    role: m.role as 'user' | 'assistant',
    content: m.content,
  }));

  // Build system prompt (Zone 1)
  const systemPrompt = await buildSystemPrompt(db, teacherId);

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
  const { data: savedMsgs } = await db.insert<{ id: string; created_at: string }[]>(
    'messages',
    {
      conversation_id: conversationId,
      role: 'assistant',
      content: assistantText,
    },
  );
  const savedMsg = Array.isArray(savedMsgs) ? savedMsgs[0] : savedMsgs;

  // Async: Run memory agent (fire-and-forget via waitUntil)
  const conversationContext = messages
    .slice(-6)
    .map((m) => `${m.role}: ${m.content}`)
    .join('\n');

  context.waitUntil(
    extractMemories(context.env, conversationContext).then((result) =>
      storeMemories(db, teacherId, result, conversationId!),
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
