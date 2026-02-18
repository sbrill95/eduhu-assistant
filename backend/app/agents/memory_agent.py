"""Memory-Agent — async post-processing after each response.

Analyzes conversation context, extracts memories into fixed categories,
updates session summaries.
"""

import json
import logging
from pydantic_ai import Agent
from pydantic import BaseModel

from app.agents.llm import get_haiku
from app import db
from app.constants import MEMORY_CATEGORIES_LIST, MEMORY_CATEGORY_DESCRIPTIONS

logger = logging.getLogger(__name__)


def _build_memory_system() -> str:
    cat_lines = "\n".join(
        f"- **{k}**: {v}" for k, v in MEMORY_CATEGORY_DESCRIPTIONS.items()
    )
    return f"""Du bist der Memory-Agent von eduhu. Analysiere den Gesprächskontext und extrahiere relevante Informationen.

## Feste Kategorien (NUR diese verwenden!)
{cat_lines}

## Scopes
- **self**: Über die Lehrkraft (Präferenzen, Stil, Gewohnheiten)
- **class**: Über Klassen (Fortschritt, Dynamik, Themen)
- **school**: Über die Schule (Regeln, Organisation)

## Regeln
1. Nur wirklich relevante Dinge extrahieren — nicht jedes Wort speichern
2. category MUSS eine der obigen 8 Kategorien sein. Keine anderen!
3. importance: 0.0-1.0 (explizit = hoch, inferiert = niedriger)
4. source: "explicit" wenn direkt gesagt, "inferred" wenn abgeleitet
5. Prüfe ob eine ähnliche Info schon in den bestehenden Memories existiert — wenn ja, NICHT nochmal speichern
6. Erstelle auch eine kurze Session-Summary (1-2 Sätze)

Antworte als JSON:
{{"memories": [{{"scope":"self|class|school","category":"<eine der 8 festen Kategorien>","key":"string","value":"string","importance":0.8,"source":"explicit|inferred"}}],"session_summary":"Kurze Zusammenfassung"}}

Wenn nichts speicherwürdig: {{"memories":[],"session_summary":"..."}}"""


MEMORY_SYSTEM = _build_memory_system()


class MemoryExtraction(BaseModel):
    memories: list[dict]
    session_summary: str = ""


async def run_memory_agent(
    teacher_id: str,
    conversation_id: str,
    recent_messages: list[dict[str, str]],
) -> None:
    """Extract and store memories from recent conversation context."""
    if not recent_messages:
        return

    context = "\n".join(
        f"{m['role']}: {m['content']}" for m in recent_messages[-6:]
    )

    # Fetch existing memories for duplicate prevention context
    existing = await db.select(
        "user_memories",
        filters={"user_id": teacher_id},
        order="importance.desc,updated_at.desc",
        limit=30,
    )
    existing_context = ""
    if existing and isinstance(existing, list):
        lines = [f"- [{m['category']}] {m['key']}: {m['value']}" for m in existing]
        existing_context = "\n\n## Bestehende Memories (NICHT duplizieren!):\n" + "\n".join(lines)

    agent = Agent(
        get_haiku(),
        instructions=MEMORY_SYSTEM,
        output_type=str,
    )

    try:
        result = await agent.run(context + existing_context)
        text = result.output
        # Parse JSON
        cleaned = text.replace("```json", "").replace("```", "").strip()
        extraction = json.loads(cleaned)

        stored = 0
        # Store memories
        for m in extraction.get("memories", []):
            # Validate category
            if m.get("category") not in MEMORY_CATEGORIES_LIST:
                logger.warning(
                    f"Invalid category '{m.get('category')}', skipping memory: {m.get('key')}"
                )
                continue

            try:
                await db.upsert(
                    "user_memories",
                    {
                        "user_id": teacher_id,
                        "scope": m.get("scope", "self"),
                        "category": m["category"],
                        "key": m["key"],
                        "value": m["value"],
                        "importance": m.get("importance", 0.5),
                        "source": m.get("source", "inferred"),
                    },
                    on_conflict="user_id,scope,category,key",
                )
                stored += 1
            except Exception as e:
                logger.warning(f"Memory upsert failed: {e}")

        # Store session summary
        summary = extraction.get("session_summary", "")
        if summary:
            await db.upsert(
                "session_logs",
                {
                    "conversation_id": conversation_id,
                    "user_id": teacher_id,
                    "summary": summary,
                },
                on_conflict="conversation_id",
            )

        logger.info(
            f"Memory agent: {stored}/{len(extraction.get('memories', []))} memories stored"
        )

    except Exception as e:
        logger.error(f"Memory agent failed: {e}")
