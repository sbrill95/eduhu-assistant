import { getSupabase, json, error, type Env } from '../../lib/supabase';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const conversationId = url.searchParams.get('conversation_id');

  if (!conversationId) {
    return error('conversation_id fehlt');
  }

  const supabase = getSupabase(context.env);

  const { data: messages } = await supabase
    .from('messages')
    .select('id, role, content, created_at')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: true });

  return json({
    messages: (messages ?? []).map((m: { id: string; role: string; content: string; created_at: string }) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      timestamp: m.created_at,
    })),
  });
};
