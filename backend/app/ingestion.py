"""Curriculum ingestion — PDF → text → chunks → embeddings → Supabase.

Flexible chunking with configurable size/overlap.
Embeddings via OpenAI text-embedding-3-small.
"""

import io
import json
import logging
import re
from typing import Any

import httpx

from app.config import get_settings
from app import db

logger = logging.getLogger(__name__)


# ══════════════════════════════════════
# PDF → Text
# ══════════════════════════════════════

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber (sync, wrapped)."""
    import pdfplumber
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n\n".join(text_parts)


# ══════════════════════════════════════
# Chunking
# ══════════════════════════════════════

def chunk_text(
    text: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[dict[str, Any]]:
    """Split text into overlapping chunks.
    
    Strategy: Split by paragraphs first, then merge into chunks of ~chunk_size chars.
    Each chunk gets metadata (index, char offsets).
    """
    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[dict[str, Any]] = []
    current_text = ""
    current_start = 0
    char_offset = 0

    for para in paragraphs:
        if len(current_text) + len(para) + 2 > chunk_size and current_text:
            # Emit chunk
            chunks.append({
                "index": len(chunks),
                "text": current_text.strip(),
                "char_start": current_start,
                "char_end": char_offset,
            })
            # Overlap: keep last `chunk_overlap` chars
            if chunk_overlap > 0 and len(current_text) > chunk_overlap:
                overlap_text = current_text[-chunk_overlap:]
                current_text = overlap_text + "\n\n" + para
                current_start = char_offset - chunk_overlap
            else:
                current_text = para
                current_start = char_offset
        else:
            if current_text:
                current_text += "\n\n" + para
            else:
                current_text = para
                current_start = char_offset

        char_offset += len(para) + 2  # +2 for paragraph separator

    # Last chunk
    if current_text.strip():
        chunks.append({
            "index": len(chunks),
            "text": current_text.strip(),
            "char_start": current_start,
            "char_end": char_offset,
        })

    return chunks


# ══════════════════════════════════════
# Embeddings (OpenAI)
# ══════════════════════════════════════

async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings from OpenAI text-embedding-3-small.
    
    Batches up to 100 texts per request.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY nicht konfiguriert")

    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.openai.com/v1/embeddings",
                json={
                    "model": "text-embedding-3-small",
                    "input": batch,
                },
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
            r.raise_for_status()
            data = r.json()

        # Sort by index to maintain order
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        all_embeddings.extend([d["embedding"] for d in sorted_data])

    return all_embeddings


# ══════════════════════════════════════
# Full Ingestion Pipeline
# ══════════════════════════════════════

async def ingest_curriculum(
    teacher_id: str,
    fach: str,
    jahrgang: str,
    bundesland: str,
    pdf_bytes: bytes,
    filename: str = "",
) -> dict[str, Any]:
    """Full pipeline: PDF → text → chunks → embeddings → store.
    
    Returns summary of what was ingested.
    """
    settings = get_settings()
    logger.info(f"Ingesting {filename or fach} for teacher {teacher_id}")

    # 1. Extract text
    full_text = await extract_text_from_pdf(pdf_bytes)
    if not full_text.strip():
        raise ValueError("PDF enthält keinen extrahierbaren Text")
    logger.info(f"Extracted {len(full_text)} chars from PDF")

    # 2. Chunk
    chunks = chunk_text(full_text, settings.chunk_size, settings.chunk_overlap)
    logger.info(f"Created {len(chunks)} chunks")

    # 3. Generate wissenskarte (summary of curriculum structure)
    wissenskarte = _extract_wissenskarte(full_text)

    # 4. Create/update user_curricula entry
    curriculum = await db.upsert(
        "user_curricula",
        {
            "user_id": teacher_id,
            "fach": fach,
            "jahrgang": jahrgang,
            "bundesland": bundesland,
            "status": "processing",
            "content_md": full_text[:50000],  # Store first 50K chars as searchable text
            "wissenskarte": wissenskarte,
            "filename": filename,
        },
        on_conflict="user_id,fach,jahrgang",
    )
    curriculum_id = curriculum[0]["id"] if isinstance(curriculum, list) else curriculum["id"]
    logger.info(f"Curriculum record: {curriculum_id}")

    # 5. Get embeddings
    chunk_texts = [c["text"] for c in chunks]
    embeddings = await get_embeddings(chunk_texts)
    logger.info(f"Got {len(embeddings)} embeddings")

    # 6. Store chunks in curriculum_chunks
    # First delete old chunks for this curriculum
    await _delete_old_chunks(curriculum_id)

    # Insert new chunks (single batch request instead of N individual inserts)
    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
        rows.append({
            "curriculum_id": curriculum_id,
            "section_path": f"chunk_{chunk['index']}",
            "chunk_text": chunk["text"],
            "embedding": embedding_str,
            "metadata": json.dumps({
                "char_start": chunk["char_start"],
                "char_end": chunk["char_end"],
                "fach": fach,
                "jahrgang": jahrgang,
                "bundesland": bundesland,
            }),
        })
    await db.insert_batch("curriculum_chunks", rows)
    logger.info(f"Inserted {len(rows)} chunks in single batch")

    # 7. Mark as active
    await db.update(
        "user_curricula",
        {"status": "active"},
        filters={"id": curriculum_id},
    )

    return {
        "curriculum_id": curriculum_id,
        "fach": fach,
        "jahrgang": jahrgang,
        "bundesland": bundesland,
        "text_chars": len(full_text),
        "chunks": len(chunks),
        "status": "active",
        "wissenskarte": wissenskarte,
    }


def _extract_wissenskarte(text: str) -> dict[str, Any]:
    """Extract a simple overview (wissenskarte) from curriculum text.
    
    Looks for headings, numbered sections, and key terms.
    """
    lines = text.split("\n")
    topics: list[str] = []
    
    for line in lines:
        stripped = line.strip()
        # Heuristic: lines that look like section headers
        if stripped and len(stripped) < 120:
            # Numbered sections
            if re.match(r"^\d+[\.\)]\s+\w", stripped):
                topics.append(stripped)
            # ALL CAPS or title-like
            elif stripped.isupper() and len(stripped) > 5:
                topics.append(stripped)
            # Lines ending with no period that start with capital
            elif (
                stripped[0].isupper()
                and not stripped.endswith(".")
                and not stripped.endswith(",")
                and len(stripped) > 10
                and len(stripped) < 80
            ):
                # Likely a heading
                if any(kw in stripped.lower() for kw in [
                    "kompetenz", "lernbereich", "thema", "modul", "einheit",
                    "ziel", "inhalt", "bereich", "stufe", "phase",
                ]):
                    topics.append(stripped)

    return {
        "topics_count": len(topics),
        "topics": topics[:30],  # Max 30 topics for overview
        "text_length": len(text),
    }


async def _delete_old_chunks(curriculum_id: str) -> None:
    """Delete existing chunks for a curriculum (before re-ingestion)."""
    settings = get_settings()
    url = f"{settings.supabase_url}/rest/v1/curriculum_chunks?curriculum_id=eq.{curriculum_id}"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    async with httpx.AsyncClient() as client:
        await client.delete(url, headers=headers)
