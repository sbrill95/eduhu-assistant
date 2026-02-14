import { getSupabase, json, type Env } from '../../lib/supabase';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const teacherId = url.searchParams.get('teacher_id');

  if (!teacherId) {
    return json([]);
  }

  const db = getSupabase(context.env);

  const { data } = await db.select<{ id: string; title: string | null; updated_at: string }[]>(
    'conversations',
    {
      columns: 'id, title, updated_at',
      filters: { user_id: teacherId },
      order: { col: 'updated_at', asc: false },
      limit: 20,
    },
  );

  return json(
    (data ?? []).map((c) => ({
      id: c.id,
      title: c.title,
      updated_at: c.updated_at,
    })),
  );
};
