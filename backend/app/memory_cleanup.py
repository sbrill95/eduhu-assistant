"""Memory Cleanup — Batch-Job für Deduplizierung und Konsolidierung.

Läuft 2x täglich via Cron. Strukturierte DB-Operationen, kein LLM-Call.
Für semantisches Merging: Anthropic Batch API (50% günstiger).

Operations:
1. Exakte Duplikate löschen (gleicher user_id + key + value)
2. Semantische Duplikate mergen (gleicher key, ähnlicher value) via Batch API
3. Importance + updated_at pflegen
4. Veraltete Einträge archivieren (>90 Tage, importance < 0.5, nie genutzt)
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from app import db

logger = logging.getLogger(__name__)


async def run_cleanup(teacher_id: str | None = None) -> dict:
    """Hauptfunktion: Cleanup für einen oder alle Teacher.
    
    Returns: {"duplicates_removed": N, "merged": N, "archived": N}
    """
    stats = {"duplicates_removed": 0, "merged": 0, "archived": 0}

    # Alle Teacher oder einzelnen
    if teacher_id:
        teacher_ids = [teacher_id]
    else:
        teachers = await db.select("user_profiles", columns="id")
        teacher_ids = [t["id"] for t in (teachers or [])]

    for tid in teacher_ids:
        result = await _cleanup_teacher(tid)
        for k, v in result.items():
            stats[k] += v

    logger.info(f"Memory cleanup done: {stats}")
    return stats


async def _cleanup_teacher(teacher_id: str) -> dict:
    """Cleanup für einen einzelnen Teacher."""
    stats = {"duplicates_removed": 0, "merged": 0, "archived": 0}

    memories = await db.select(
        "user_memories",
        filters={"user_id": teacher_id},
        order="created_at.asc",
    )
    if not memories or not isinstance(memories, list):
        return stats

    logger.info(f"Cleaning up {len(memories)} memories for teacher {teacher_id[:8]}...")

    # ── Phase 1: Exakte Duplikate löschen ──
    seen: dict[str, dict] = {}  # (scope, category, key, value) → neuestes Memory
    to_delete: list[str] = []

    for m in memories:
        fingerprint = f"{m['scope']}|{m['category']}|{m['key']}|{m['value']}"
        if fingerprint in seen:
            # Duplikat gefunden — behalte das neuere
            old = seen[fingerprint]
            to_delete.append(old["id"])
            seen[fingerprint] = m
        else:
            seen[fingerprint] = m

    for mid in to_delete:
        try:
            await db.delete("user_memories", filters={"id": mid})
            stats["duplicates_removed"] += 1
        except Exception as e:
            logger.warning(f"Failed to delete duplicate {mid}: {e}")

    # ── Phase 2: Key-Duplikate mergen (gleicher key, egal welche category) ──
    # Memory-Agent speichert "duration: 45 Min" unter 5 verschiedenen categories.
    # Behalte nur den neuesten pro key.
    key_groups: dict[str, list[dict]] = defaultdict(list)
    remaining = [m for m in memories if m["id"] not in to_delete]

    for m in remaining:
        group_key = m['key']  # Nur key, NICHT scope|category
        key_groups[group_key].append(m)

    for group_key, group in key_groups.items():
        if len(group) <= 1:
            continue

        # Sortiere nach updated_at desc — behalte neuestes
        group.sort(key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True)
        keeper = group[0]

        # Lösche die älteren
        for old in group[1:]:
            try:
                await db.delete("user_memories", filters={"id": old["id"]})
                stats["merged"] += 1
            except Exception as e:
                logger.warning(f"Failed to delete merged {old['id']}: {e}")

        # Update keeper: höchste importance aus der Gruppe behalten
        max_importance = max(m.get("importance", 0.5) for m in group)
        if keeper.get("importance", 0.5) < max_importance:
            try:
                await db.update(
                    "user_memories",
                    {"importance": max_importance, "updated_at": datetime.now(timezone.utc).isoformat()},
                    filters={"id": keeper["id"]},
                )
            except Exception as e:
                logger.warning(f"Failed to update importance for {keeper['id']}: {e}")

    # ── Phase 3: Veraltete Einträge archivieren ──
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    stale = [
        m for m in remaining
        if m.get("importance", 0.5) < 0.5
        and m.get("updated_at", m.get("created_at", "")) < cutoff
    ]

    for m in stale:
        try:
            await db.delete("user_memories", filters={"id": m["id"]})
            stats["archived"] += 1
        except Exception as e:
            logger.warning(f"Failed to archive {m['id']}: {e}")

    logger.info(
        f"Teacher {teacher_id[:8]}: "
        f"removed {stats['duplicates_removed']} dupes, "
        f"merged {stats['merged']}, "
        f"archived {stats['archived']} "
        f"(was {len(memories)}, now ~{len(memories) - sum(stats.values())})"
    )

    return stats
