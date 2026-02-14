import type { SupabaseDB } from './supabase';

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
  db: SupabaseDB,
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
  const { data: profile } = await db.select<TeacherProfile>(
    'user_profiles',
    { filters: { id: teacherId }, single: true },
  );

  if (profile) {
    dynamicContext += `\n## Lehrkraft-Profil\nName: ${profile.name}`;
    if (profile.bundesland) dynamicContext += `\nBundesland: ${profile.bundesland}`;
    if (profile.schulform) dynamicContext += `\nSchulform: ${profile.schulform}`;
    if (profile.faecher?.length) dynamicContext += `\nFächer: ${profile.faecher.join(', ')}`;
    if (profile.jahrgaenge?.length) dynamicContext += `\nJahrgänge: ${profile.jahrgaenge.join(', ')}`;
    if (profile.class_summary && Object.keys(profile.class_summary).length > 0) {
      dynamicContext += `\n\n## Klassen-Summary\n${JSON.stringify(profile.class_summary, null, 2)}`;
    }
    if (profile.preferences && Object.keys(profile.preferences).length > 0) {
      dynamicContext += `\n\n## Präferenzen\n${JSON.stringify(profile.preferences, null, 2)}`;
    }
  }

  // Load memories (scope: self)
  const { data: memories } = await db.select<Memory[]>(
    'user_memories',
    {
      columns: 'scope, category, key, value',
      filters: { user_id: teacherId },
      order: { col: 'importance', asc: false },
      limit: 30,
    },
  );

  if (memories && memories.length > 0) {
    dynamicContext += '\n\n## Was du über diese Lehrkraft weißt';
    for (const m of memories) {
      dynamicContext += `\n- [${m.scope}/${m.category}] ${m.key}: ${m.value}`;
    }
  }

  // Load recent session summaries
  const { data: sessions } = await db.select<SessionLog[]>(
    'session_logs',
    {
      columns: 'summary, created_at',
      filters: { user_id: teacherId },
      order: { col: 'created_at', asc: false },
      limit: 5,
    },
  );

  if (sessions && sessions.length > 0) {
    dynamicContext += '\n\n## Letzte Gespräche';
    for (const s of sessions) {
      const date = new Date(s.created_at).toLocaleDateString('de-DE');
      dynamicContext += `\n- ${date}: ${s.summary}`;
    }
  }

  return `${identity}\n\n${tools}\n\n${dynamicContext}`.trim();
}
