import { getSupabase, json, error, type Env } from '../../lib/supabase';

interface LoginRequest {
  password: string;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const body = (await context.request.json()) as LoginRequest;

  if (!body.password?.trim()) {
    return error('Passwort fehlt');
  }

  const supabase = getSupabase(context.env);

  const { data: teacher, error: dbError } = await supabase
    .from('teachers')
    .select('id, name')
    .eq('password', body.password.trim())
    .single();

  if (dbError || !teacher) {
    return error('Falsches Passwort', 401);
  }

  // Ensure user_profiles exists
  await supabase.from('user_profiles').upsert(
    { id: teacher.id, name: teacher.name },
    { onConflict: 'id' },
  );

  return json({
    teacher_id: teacher.id,
    name: teacher.name,
  });
};
