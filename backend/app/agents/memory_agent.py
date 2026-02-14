"""Memory-Agent — async post-processing after each response.

Analyzes conversation context, extracts memories into Scope×Category buckets,
updates class summaries and wissenskarte.
"""

import json
import logging
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic import BaseModel

from app.config import get_settings
from app import db

logger = logging.getLogger(__name__)

MEMORY_SYSTEM = """Du bist der Memory-Agent von eduhu. Analysiere den Gesprächskontext und extrahiere relevante Informationen.

## Scopes
- **self**: Über die Lehrkraft (Präferenzen, Stil, Gewohnheiten)
- **class**: Über Klassen (Fortschritt, Dynamik, Themen)
- **school**: Über die Schule (Regeln, Organisation)

## Regeln
1. Nur wirklich relevante Dinge extrahieren — nicht jedes Wort speichern
2. importance: 0.0-1.0 (explizit = hoch, inferiert = niedriger)
3. source: "explicit" wenn direkt gesagt, "inferred" wenn abgeleitet
4. Erstelle auch eine kurze Session-Summary (1-2 Sätze)

Antworte als JSON:
{
  "memories": [{"scope":"self|class|school","category":"string","key":"string","value":"string","importance":0.8,"source":"explicit|inferred"}],
  "session_summary": "Kurze Zusammenfassung"
}

Wenn nichts speicherwürdig: {"memories":[],"session_summary":"..."}"""


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

    import os
    settings = get_settings()
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
    model = AnthropicModel("claude-3-5-haiku-20241022")

    agent = Agent(
        model,
        instructions=MEMORY_SYSTEM,
        output_type=str,
    )

    try:
        result = await agent.run(context)
        text = result.output
        # Parse JSON
        cleaned = text.replace("```json", "").replace("```", "").strip()
        extraction = json.loads(cleaned)

        # Store memories
        for m in extraction.get("memories", []):
            try:
                await db.upsert(
                    "user_memories",
                    {
                        "user_id": teacher_id,
                        "scope": m["scope"],
                        "category": m["category"],
                        "key": m["key"],
                        "value": m["value"],
                        "importance": m.get("importance", 0.5),
                        "source": m.get("source", "inferred"),
                    },
                    on_conflict="user_id,scope,category,key",
                )
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
            f"Memory agent: {len(extraction.get('memories', []))} memories extracted"
        )

    except Exception as e:
        logger.error(f"Memory agent failed: {e}")
