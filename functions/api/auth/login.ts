import { getSupabase, json, error, type Env } from '../../lib/supabase';

interface LoginRequest {
  password: string;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = (await context.request.json()) as LoginRequest;

  if (!body.password?.trim()) {
    return error('Passwort fehlt');
  }

  const db = getSupabase(context.env);

  const { data: teacher, error: dbErr } = await db.select<{ id: string; name: string }>(
    'teachers',
    { columns: 'id, name', filters: { password: body.password.trim() }, single: true },
  );

  if (dbErr || !teacher) {
    return error('Falsches Passwort', 401);
  }

  // Ensure user_profiles exists
  await db.upsert('user_profiles', { id: teacher.id, name: teacher.name }, 'id');

  return json({ teacher_id: teacher.id, name: teacher.name });
};
