"""Curriculum-Agent — RAG over teacher's curriculum data.

Searches curriculum_chunks by keyword matching (Phase 1).
pgvector embedding search comes in Phase 2.
"""

import logging
from app import db

logger = logging.getLogger(__name__)


async def curriculum_search(teacher_id: str, query: str) -> str:
    """Search curriculum data for the given teacher.
    
    Phase 1: Simple text search over curriculum content.
    Phase 2: pgvector embedding similarity search.
    """
    # Check if teacher has any curricula
    curricula = await db.select(
        "user_curricula",
        columns="id, fach, jahrgang, content_md, wissenskarte",
        filters={"user_id": teacher_id},
    )

    if not curricula or not isinstance(curricula, list) or len(curricula) == 0:
        return "Die Lehrkraft hat noch keine Lehrpläne hochgeladen. Bitte empfehle den PDF-Upload im Profil."

    # Simple keyword search in content_md
    results: list[str] = []
    query_lower = query.lower()

    for c in curricula:
        content = (c.get("content_md") or "").lower()
        if query_lower in content or any(
            word in content for word in query_lower.split()
        ):
            # Extract relevant section (±500 chars around match)
            idx = content.find(query_lower)
            if idx == -1:
                for word in query_lower.split():
                    idx = content.find(word)
                    if idx != -1:
                        break

            if idx != -1:
                start = max(0, idx - 500)
                end = min(len(content), idx + 500)
                snippet = c.get("content_md", "")[start:end]
                results.append(
                    f"**{c.get('fach', '?')} {c.get('jahrgang', '?')}:**\n{snippet}"
                )
            else:
                # Return wissenskarte summary
                wk = c.get("wissenskarte")
                if wk:
                    results.append(
                        f"**{c.get('fach', '?')} {c.get('jahrgang', '?')} (Übersicht):**\n{wk}"
                    )

    if not results:
        return f"Keine Lehrplaninhalte zu '{query}' gefunden. Die Lehrkraft hat {len(curricula)} Curriculum/Curricula hochgeladen, aber keins enthält passende Inhalte."

    return "\n\n".join(results[:3])  # Max 3 results
