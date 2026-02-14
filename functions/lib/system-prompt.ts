interface SupabaseDB {
  from(table: string): any;
}

interface TeacherProfile {
  id: string;
  name: string;
  bundesland?: string;
  schulform?: string;
  faecher?: string[];
  jahrgaenge?: number[];
  class_summary?: Record<string, unknown>;
  preferences?: Record<string, unknown>;
}

interface Memory {
  scope: string;
  category: string;
  key: string;
  value: string;
}

interface SessionLog {
  summary: string;
  created_at: string;
}

/**
 * Build the system prompt using the 3-zone model.
 * Zone 1 (always-on): loaded at session start.
 */
export async function buildSystemPrompt(
  supabase: SupabaseDB,
  teacherId: string,
): Promise<string> {
  // --- Block 1: Identity (static) ---
  const identity = `Du bist eduhu 🦉, ein proaktiver, warmer KI-Unterrichtsassistent.
Du hilfst Lehrkräften bei Planung, Materialerstellung, Differenzierung und Organisation.
Du sprichst Deutsch, bist professionell aber nahbar, und nutzt gerne Emojis.
Du merkst dir Dinge über die Lehrkraft, ihre Klassen und Präferenzen.
Wenn du etwas nicht weißt, fragst du nach — aber nie technisch, immer natürlich.`;

  // --- Block 2: Tools (static) ---
  const tools = `Du hast folgende Fähigkeiten:
- Arbeitsblätter, Quizze und Übungen erstellen
- Unterrichtsstunden planen und strukturieren
- Texte differenzieren (verschiedene Niveaus)
- Elternbriefe und Formulare verfassen
- Bei Fragen zum Lehrplan helfen (wenn Curriculum hochgeladen)
- Dinge merken, die die Lehrkraft erwähnt`;

  // --- Block 3: Dynamic Context (Zone 1) ---
  let dynamicContext = '';

  // Load teacher profile
  const { data: profile } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('id', teacherId)
    .single();

  if (profile) {
    const p = profile as TeacherProfile;
    dynamicContext += `\n## Lehrkraft-Profil
Name: ${p.name}`;
    if (p.bundesland) dynamicContext += `\nBundesland: ${p.bundesland}`;
    if (p.schulform) dynamicContext += `\nSchulform: ${p.schulform}`;
    if (p.faecher?.length) dynamicContext += `\nFächer: ${p.faecher.join(', ')}`;
    if (p.jahrgaenge?.length) dynamicContext += `\nJahrgänge: ${p.jahrgaenge.join(', ')}`;
    if (p.class_summary) {
      dynamicContext += `\n\n## Klassen-Summary\n${JSON.stringify(p.class_summary, null, 2)}`;
    }
    if (p.preferences) {
      dynamicContext += `\n\n## Präferenzen\n${JSON.stringify(p.preferences, null, 2)}`;
    }
  }

  // Load memories (scope: self)
  const { data: memories } = await supabase
    .from('user_memories')
    .select('scope, category, key, value')
    .eq('user_id', teacherId)
    .order('importance', { ascending: false })
    .limit(30);

  if (memories && memories.length > 0) {
    dynamicContext += '\n\n## Was du über diese Lehrkraft weißt';
    for (const m of memories as Memory[]) {
      dynamicContext += `\n- [${m.scope}/${m.category}] ${m.key}: ${m.value}`;
    }
  }

  // Load recent session summaries
  const { data: sessions } = await supabase
    .from('session_logs')
    .select('summary, created_at')
    .eq('user_id', teacherId)
    .order('created_at', { ascending: false })
    .limit(5);

  if (sessions && sessions.length > 0) {
    dynamicContext += '\n\n## Letzte Gespräche';
    for (const s of sessions as SessionLog[]) {
      const date = new Date(s.created_at).toLocaleDateString('de-DE');
      dynamicContext += `\n- ${date}: ${s.summary}`;
    }
  }

  // --- Block 4: Conversation summary (injected per-request, not here) ---

  return `${identity}\n\n${tools}\n\n${dynamicContext}`.trim();
}
