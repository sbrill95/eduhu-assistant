"""Knowledge layer — Wissenskarte + Lazy-Loading tools for sub-agents.

This is the core module that connects sub-agents to the agent_knowledge table.
Every sub-agent uses these functions to access:
- Wissenskarte (compact summary for system prompt)
- Good Practices (pgvector similarity search)
- Full Context (conversation summary)
- Teacher Preferences (direct DB lookup)
"""

import logging
from typing import Any

from app import db
from app.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Wissenskarte — compact summary injected into sub-agent system prompts
# ---------------------------------------------------------------------------

async def build_wissenskarte(teacher_id: str, agent_type: str, fach: str) -> str:
    """Build a compact Wissenskarte (~100-200 tokens) for a sub-agent.
    
    Aggregates:
    - Generic profile for this agent_type + fach
    - Count of good practices available
    - Teacher preferences (if any)
    - Count of examples uploaded
    """
    parts = []

    # 1. Generic profile
    try:
        generic = await db.select(
            "agent_knowledge",
            filters={
                "agent_type": agent_type,
                "fach": fach,
                "knowledge_type": "generic",
                "source": "system",
            },
            limit=1,
            single=True,
        )
        if generic and generic.get("content"):
            content = generic["content"]
            if isinstance(content, dict):
                desc = content.get("beschreibung", "")
                if desc:
                    parts.append(f"## Fach-Profil\n{desc}")
                # Extract key quality criteria
                kriterien = content.get("qualitaetskriterien", [])
                if kriterien:
                    parts.append("Qualitätskriterien: " + ", ".join(kriterien[:5]))
    except Exception as e:
        logger.debug(f"No generic profile: {e}")

    # 2. Teacher preferences
    try:
        prefs = await db.select(
            "agent_knowledge",
            filters={
                "teacher_id": teacher_id,
                "agent_type": agent_type,
                "knowledge_type": "preference",
            },
            order="updated_at.desc",
            limit=5,
        )
        if prefs and isinstance(prefs, list) and len(prefs) > 0:
            pref_items = []
            for p in prefs:
                desc = p.get("description", "")
                if desc:
                    pref_items.append(f"- {desc}")
            if pref_items:
                parts.append("## Lehrkraft-Präferenzen\n" + "\n".join(pref_items))
    except Exception as e:
        logger.debug(f"No preferences: {e}")

    # 3. Counts
    try:
        good_practices = await db.select(
            "agent_knowledge",
            columns="id",
            filters={
                "teacher_id": teacher_id,
                "agent_type": agent_type,
                "knowledge_type": "good_practice",
            },
        )
        gp_count = len(good_practices) if isinstance(good_practices, list) else 0

        examples = await db.select(
            "agent_knowledge",
            columns="id",
            filters={
                "teacher_id": teacher_id,
                "agent_type": agent_type,
                "knowledge_type": "example",
            },
        )
        ex_count = len(examples) if isinstance(examples, list) else 0

        if gp_count > 0 or ex_count > 0:
            parts.append(f"Verfügbar: {gp_count} Good Practices, {ex_count} Beispiele (via Tools abrufbar)")
    except Exception as e:
        logger.debug(f"Count query failed: {e}")

    if not parts:
        return ""

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Lazy-Loading Tools — called by sub-agents via Pydantic AI tools
# ---------------------------------------------------------------------------

async def get_good_practices(
    teacher_id: str,
    agent_type: str,
    fach: str,
    thema: str | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Get good practice materials, ordered by quality score.
    
    TODO: When embeddings are populated, use pgvector similarity search on thema.
    For now, uses fach + agent_type filter with quality ordering.
    """
    try:
        filters: dict[str, str] = {
            "agent_type": agent_type,
            "knowledge_type": "good_practice",
        }
        # Include both teacher-specific and global good practices
        # Supabase REST doesn't support OR easily, so we do two queries
        results = []
        
        # Teacher's own good practices
        teacher_filters = {**filters, "teacher_id": teacher_id, "fach": fach}
        teacher_gp = await db.select(
            "agent_knowledge",
            filters=teacher_filters,
            order="quality_score.desc",
            limit=limit,
        )
        if isinstance(teacher_gp, list):
            results.extend(teacher_gp)

        # Global good practices (if we need more)
        if len(results) < limit:
            # Note: teacher_id=NULL needs special handling in Supabase REST
            # Using a raw filter approach
            remaining = limit - len(results)
            global_gp = await db.select(
                "agent_knowledge",
                filters={**filters, "fach": fach, "source": "system"},
                order="quality_score.desc",
                limit=remaining,
            )
            if isinstance(global_gp, list):
                results.extend(global_gp)

        return results[:limit]
    except Exception as e:
        logger.error(f"get_good_practices failed: {e}")
        return []


async def get_teacher_preferences(
    teacher_id: str,
    agent_type: str,
    fach: str | None = None,
) -> list[dict[str, Any]]:
    """Get teacher preferences for a specific agent type."""
    try:
        filters: dict[str, str] = {
            "teacher_id": teacher_id,
            "agent_type": agent_type,
            "knowledge_type": "preference",
        }
        if fach:
            filters["fach"] = fach
        
        prefs = await db.select(
            "agent_knowledge",
            filters=filters,
            order="updated_at.desc",
            limit=10,
        )
        return prefs if isinstance(prefs, list) else []
    except Exception as e:
        logger.error(f"get_teacher_preferences failed: {e}")
        return []


async def get_full_context(conversation_id: str, max_messages: int = 10) -> str:
    """Get a summary of the conversation context for sub-agents.
    
    Returns a compact summary (not raw messages) to keep sub-agent context efficient.
    """
    try:
        messages = await db.select(
            "messages",
            columns="role,content",
            filters={"conversation_id": conversation_id},
            order="created_at.desc",
            limit=max_messages,
        )
        if not messages or not isinstance(messages, list):
            return "Keine vorherige Konversation."

        # Reverse to get chronological order
        messages.reverse()

        # Build compact summary
        parts = []
        for msg in messages:
            role = "Lehrkraft" if msg.get("role") == "user" else "Assistent"
            content = str(msg.get("content", ""))[:200]  # Truncate long messages
            parts.append(f"{role}: {content}")

        return "## Bisheriger Gesprächsverlauf\n" + "\n".join(parts)
    except Exception as e:
        logger.error(f"get_full_context failed: {e}")
        return "Kontext konnte nicht geladen werden."


# ---------------------------------------------------------------------------
# Knowledge Updates — called after material generation
# ---------------------------------------------------------------------------

async def save_preference(
    teacher_id: str,
    agent_type: str,
    fach: str,
    description: str,
    content: dict[str, Any],
) -> None:
    """Save or update a teacher preference in agent_knowledge."""
    try:
        await db.insert("agent_knowledge", {
            "teacher_id": teacher_id,
            "agent_type": agent_type,
            "fach": fach,
            "knowledge_type": "preference",
            "source": "conversation",
            "description": description,
            "content": content,
        })
        logger.info(f"Saved preference for {teacher_id}/{agent_type}/{fach}: {description}")
    except Exception as e:
        logger.error(f"save_preference failed: {e}")


async def save_good_practice(
    teacher_id: str,
    agent_type: str,
    fach: str,
    description: str,
    content: dict[str, Any],
    quality_score: float = 0.7,
) -> None:
    """Save a positively rated material as good practice."""
    try:
        await db.insert("agent_knowledge", {
            "teacher_id": teacher_id,
            "agent_type": agent_type,
            "fach": fach,
            "knowledge_type": "good_practice",
            "source": "generated",
            "description": description,
            "content": content,
            "quality_score": quality_score,
        })
        logger.info(f"Saved good practice for {teacher_id}/{agent_type}/{fach}")
    except Exception as e:
        logger.error(f"save_good_practice failed: {e}")


async def update_quality_score(knowledge_id: str, delta: float) -> None:
    """Adjust quality score of a knowledge entry (e.g. +0.1 for download, -0.2 for negative feedback)."""
    try:
        entry = await db.select("agent_knowledge", filters={"id": knowledge_id}, single=True)
        if entry:
            current = entry.get("quality_score", 0.5)
            new_score = max(0.0, min(1.0, current + delta))
            times_used = entry.get("times_used", 0) + 1
            await db.update(
                "agent_knowledge",
                {"quality_score": new_score, "times_used": times_used, "updated_at": "now()"},
                filters={"id": knowledge_id},
            )
    except Exception as e:
        logger.error(f"update_quality_score failed: {e}")
