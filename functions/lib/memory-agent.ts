import type { Env, SupabaseDB } from './supabase';
import { chatWithClaude } from './claude';

interface ExtractedMemory {
  scope: 'self' | 'class' | 'school';
  category: string;
  key: string;
  value: string;
  importance: number;
  source: 'explicit' | 'inferred';
}

interface MemoryExtractionResult {
  memories: ExtractedMemory[];
  session_summary?: string;
}

const MEMORY_SYSTEM_PROMPT = `Du bist der Memory-Agent von eduhu. Deine Aufgabe: Analysiere den Gesprächskontext und extrahiere relevante Informationen.

## Scopes
- **self**: Über die Lehrkraft (Präferenzen, Stil, Gewohnheiten)
- **class**: Über Klassen (Fortschritt, Dynamik, Themen)
- **school**: Über die Schule (Regeln, Organisation)

## Regeln
1. Nur wirklich relevante Dinge extrahieren — nicht jedes Wort speichern
2. importance: 0.0-1.0 (explizit erwähnt = hoch, inferiert = niedriger)
3. source: "explicit" wenn die Lehrkraft es direkt gesagt hat, "inferred" wenn abgeleitet
4. Erstelle auch eine kurze Session-Summary (1-2 Sätze)

Antworte ausschließlich als JSON:
{
  "memories": [
    { "scope": "self|class|school", "category": "string", "key": "string", "value": "string", "importance": 0.8, "source": "explicit|inferred" }
  ],
  "session_summary": "Kurze Zusammenfassung des Gesprächs"
}

Wenn nichts speicherwürdig ist: { "memories": [], "session_summary": "..." }`;

export async function extractMemories(
  env: Env,
  conversationContext: string,
): Promise<MemoryExtractionResult> {
  const { text } = await chatWithClaude(
    env,
    MEMORY_SYSTEM_PROMPT,
    [{ role: 'user', content: conversationContext }],
    'claude-sonnet-4-20250514',
    2048,
  );

  const cleaned = text.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();
  try {
    return JSON.parse(cleaned) as MemoryExtractionResult;
  } catch {
    return { memories: [], session_summary: undefined };
  }
}

export async function storeMemories(
  db: SupabaseDB,
  teacherId: string,
  result: MemoryExtractionResult,
  conversationId: string,
): Promise<void> {
  // Store memories
  for (const m of result.memories) {
    await db.upsert(
      'user_memories',
      {
        user_id: teacherId,
        scope: m.scope,
        category: m.category,
        key: m.key,
        value: m.value,
        importance: m.importance,
        source: m.source,
      },
      'user_id,scope,category,key',
    );
  }

  // Update session log
  if (result.session_summary) {
    await db.upsert(
      'session_logs',
      {
        conversation_id: conversationId,
        user_id: teacherId,
        summary: result.session_summary,
      },
      'conversation_id',
    );
  }
}
