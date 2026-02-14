import { getSupabase, json, error, type Env } from '../../lib/supabase';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const conversationId = url.searchParams.get('conversation_id');

  if (!conversationId) {
    return error('conversation_id fehlt');
  }

  const db = getSupabase(context.env);

  const { data } = await db.select<{ id: string; role: string; content: string; created_at: string }[]>(
    'messages',
    {
      columns: 'id, role, content, created_at',
      filters: { conversation_id: conversationId },
      order: { col: 'created_at', asc: true },
    },
  );

  return json({
    messages: (data ?? []).map((m) => ({
      id: m.id,
      role: m.role,
      content: m.content,
      timestamp: m.created_at,
    })),
  });
};
