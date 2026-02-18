"""Curriculum-Agent — RAG over teacher's curriculum data.

Uses pgvector similarity search via direct SQL.
Falls back to keyword search if embedding fails.
"""

import logging

from app import db
from app.ingestion import get_embeddings

logger = logging.getLogger(__name__)


async def curriculum_search(teacher_id: str, query: str) -> str:
    """Search curriculum chunks using embedding similarity."""
    # 1. Get teacher's curriculum IDs
    curricula = await db.select(
        "user_curricula",
        columns="id, fach, jahrgang, bundesland",
        filters={"user_id": teacher_id},
    )

    if not curricula or not isinstance(curricula, list) or len(curricula) == 0:
        return "Die Lehrkraft hat noch keine Lehrpläne hochgeladen. Bitte empfehle den PDF-Upload im Profil."

    curriculum_ids = [str(c["id"]) for c in curricula]
    curriculum_map = {c["id"]: c for c in curricula}

    # 2. Try embedding-based search first
    try:
        return await _embedding_search(query, curriculum_ids, curriculum_map)
    except Exception as e:
        logger.warning(f"Embedding search failed, falling back to keyword: {e}")
        return await _keyword_search(query, curriculum_ids, curriculum_map)


async def _embedding_search(
    query: str,
    curriculum_ids: list[str],
    curriculum_map: dict,
) -> str:
    """Similarity search via pgvector."""
    # Get query embedding
    embeddings = await get_embeddings([query])
    query_embedding = embeddings[0]

    # Direct pgvector query
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    results = await db.raw_fetch(
        """
        SELECT id, curriculum_id, chunk_text, section_path,
               1 - (embedding <=> $1::vector) as similarity
        FROM curriculum_chunks
        WHERE curriculum_id::text = ANY($2)
          AND 1 - (embedding <=> $1::vector) > $3
        ORDER BY embedding <=> $1::vector
        LIMIT $4
        """,
        embedding_str,
        curriculum_ids,
        0.25,
        5,
    )

    if not results:
        return f"Keine passenden Lehrplaninhalte zu '{query}' gefunden."

    formatted: list[str] = []
    for chunk in results:
        cid = chunk["curriculum_id"]
        info = curriculum_map.get(cid, {})
        label = f"{info.get('fach', '?')} ({info.get('bundesland', '?')})"
        sim = chunk.get("similarity", 0)
        text = chunk["chunk_text"][:1000]  # Limit per chunk
        formatted.append(f"**{label}** (Relevanz: {sim:.0%}):\n{text}")

    sources = set()
    for chunk in results:
        cid = chunk["curriculum_id"]
        info = curriculum_map.get(cid, {})
        sources.add(f"{info.get('fach', '?')} {info.get('jahrgang', '')} ({info.get('bundesland', '?')})")
    source_line = "\U0001f4d6 **Quelle: Rahmenlehrplan " + ", ".join(sources) + "**"
    return source_line + "\n\n" + "\n\n---\n\n".join(formatted)


async def _keyword_search(
    query: str,
    curriculum_ids: list[str],
    curriculum_map: dict,
) -> str:
    """Fallback: ilike keyword search over chunk_text."""
    results: list[str] = []
    query_words = [w for w in query.lower().split() if len(w) > 2][:3]

    for cid in curriculum_ids:
        for word in query_words:
            chunks = await db.raw_fetch(
                """
                SELECT chunk_text, section_path
                FROM curriculum_chunks
                WHERE curriculum_id::text = $1
                  AND chunk_text ILIKE $2
                LIMIT 3
                """,
                cid,
                f"%{word}%",
            )
            info = curriculum_map.get(cid, {})
            if not info:
                # Try UUID lookup
                for k, v in curriculum_map.items():
                    if str(k) == cid:
                        info = v
                        break
            label = f"{info.get('fach', '?')} ({info.get('bundesland', '?')})"
            for chunk in chunks:
                text = chunk["chunk_text"]
                idx = text.lower().find(word)
                start = max(0, idx - 400) if idx != -1 else 0
                end = min(len(text), (idx if idx != -1 else 0) + 400)
                snippet = text[start:end] if idx != -1 else text[:800]
                results.append(f"**{label}:**\n{snippet}")

    if not results:
        return f"Keine Lehrplaninhalte zu '{query}' gefunden."

    seen = set()
    unique = [r for r in results if r[:200] not in seen and not seen.add(r[:200])]  # type: ignore
    # Add source header
    source_labels = set()
    for c in curriculum_map.values():
        source_labels.add(f"{c.get('fach', '?')} {c.get('jahrgang', '')} ({c.get('bundesland', '?')})")
    source_line = "\U0001f4d6 **Quelle: Rahmenlehrplan " + ", ".join(source_labels) + "**"
    return source_line + "\n\n" + "\n\n---\n\n".join(unique[:5])
