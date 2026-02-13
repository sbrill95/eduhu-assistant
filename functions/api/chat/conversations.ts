import { getSupabase, json, type Env } from '../../lib/supabase';

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const teacherId = url.searchParams.get('teacher_id');

  if (!teacherId) {
    return new Response(JSON.stringify([]), {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const supabase = getSupabase(context.env);

  const { data } = await supabase
    .from('conversations')
    .select('id, title, updated_at')
    .eq('user_id', teacherId)
    .order('updated_at', { ascending: false })
    .limit(20);

  return json(
    (data ?? []).map((c: { id: string; title: string | null; updated_at: string }) => ({
      id: c.id,
      title: c.title,
      updated_at: c.updated_at,
    })),
  );
};
