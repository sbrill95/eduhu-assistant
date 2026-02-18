"""Memory Cleanup — Batch-Job für Deduplizierung und Konsolidierung.

Operations:
0. Migrate old free-text categories to fixed 8 categories
1. Exakte Duplikate löschen (gleicher user_id + key + value)
2. Key-Duplikate mergen (gleicher key, egal welche category)
3. Veraltete Einträge archivieren (>90 Tage, importance < 0.5)
"""

import logging
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from app import db
from app.constants import MEMORY_CATEGORIES_LIST

logger = logging.getLogger(__name__)

# ── Mapping from old chaotic categories to fixed ones ──
# TODO: Remove this dict once all memories are migrated (one-time migration)
OLD_TO_NEW_CATEGORY: dict[str, str] = {
    # persoenlich
    "personal": "persoenlich", "name": "persoenlich", "identity": "persoenlich",
    "location": "persoenlich", "contact": "persoenlich", "school_type": "persoenlich",
    "profession": "persoenlich", "greeting": "persoenlich", "emotion": "persoenlich",
    "personal_interest": "persoenlich", "personal_trait": "persoenlich",
    "personality_traits": "persoenlich", "professional_profile": "persoenlich",
    "working_style": "persoenlich", "professional_approach": "persoenlich",
    "expertise": "persoenlich", "teaching_experience": "persoenlich",
    "interests": "persoenlich", "Interest": "persoenlich", "Passion": "persoenlich",
    # faecher_und_themen
    "subject": "faecher_und_themen", "subjects": "faecher_und_themen",
    "topic": "faecher_und_themen", "topics": "faecher_und_themen",
    "current_topic": "faecher_und_themen", "current_topics": "faecher_und_themen",
    "current_focus": "faecher_und_themen", "current_subjects": "faecher_und_themen",
    "subject_focus": "faecher_und_themen", "subject_content": "faecher_und_themen",
    "subject_topic": "faecher_und_themen", "subject_topics": "faecher_und_themen",
    "subject_planning": "faecher_und_themen", "subject_progression": "faecher_und_themen",
    "learning_topic": "faecher_und_themen", "learning_topics": "faecher_und_themen",
    "physics": "faecher_und_themen", "physics_topic": "faecher_und_themen",
    "physics_topics": "faecher_und_themen", "optik_themen": "faecher_und_themen",
    "themenbereich": "faecher_und_themen", "unterrichtsfächer": "faecher_und_themen",
    "teaching_subjects": "faecher_und_themen", "teaching_specialty": "faecher_und_themen",
    "Physik Unterricht": "faecher_und_themen", "Physics Topic": "faecher_und_themen",
    "Unterrichtsthema": "faecher_und_themen", "lesson_topic": "faecher_und_themen",
    "topic_complexity": "faecher_und_themen",
    # klassen_und_schueler
    "class_details": "klassen_und_schueler", "class_level": "klassen_und_schueler",
    "class_levels": "klassen_und_schueler", "class_context": "klassen_und_schueler",
    "class_detail": "klassen_und_schueler", "class_mood": "klassen_und_schueler",
    "grade": "klassen_und_schueler", "grade_level": "klassen_und_schueler",
    "grade_levels": "klassen_und_schueler", "teaching_classes": "klassen_und_schueler",
    "teaching_levels": "klassen_und_schueler", "teaching groups": "klassen_und_schueler",
    "student_interest": "klassen_und_schueler", "Schülerinteresse": "klassen_und_schueler",
    "student_list": "klassen_und_schueler", "target_group": "klassen_und_schueler",
    "learning_level": "klassen_und_schueler", "learning_needs": "klassen_und_schueler",
    "learning_challenges": "klassen_und_schueler", "learning_challenge": "klassen_und_schueler",
    "learning_issue": "klassen_und_schueler", "challenges": "klassen_und_schueler",
    "challenge": "klassen_und_schueler", "difficulty_level": "klassen_und_schueler",
    "performance": "klassen_und_schueler", "learning_progress": "klassen_und_schueler",
    "learning_status": "klassen_und_schueler", "learning_context": "klassen_und_schueler",
    # didaktik
    "teaching": "didaktik", "teaching_approach": "didaktik", "teaching_style": "didaktik",
    "teaching_method": "didaktik", "teaching_preference": "didaktik",
    "teaching_preferences": "didaktik", "teaching_interest": "didaktik",
    "teaching_intention": "didaktik", "teaching_focus": "didaktik",
    "teaching_strategy": "didaktik", "Teaching Method": "didaktik",
    "engagement_strategy": "didaktik", "support_strategy": "didaktik",
    "learning_method": "didaktik", "learning_goal": "didaktik",
    "learning_stages": "didaktik", "learning_focus": "didaktik",
    "learning_activity": "didaktik", "interaction": "didaktik",
    "interaction_pattern": "didaktik", "interaction_type": "didaktik",
    "communication": "didaktik", "additional teaching": "didaktik",
    "lesson_planning": "didaktik", "lesson_plan": "didaktik",
    "lesson_preparation": "didaktik", "lesson_design": "didaktik",
    "lesson_focus": "didaktik", "lesson_resource": "didaktik",
    "planning": "didaktik", "preparation": "didaktik",
    "teaching_tool": "didaktik", "teaching_resource": "didaktik",
    "teaching_material": "didaktik",
    # pruefungen
    "assessment": "pruefungen", "assessment_planning": "pruefungen",
    "assessment_structure": "pruefungen", "assessment_history": "pruefungen",
    "assessment_details": "pruefungen", "assessment_parameters": "pruefungen",
    "exam_structure": "pruefungen", "exam_details": "pruefungen",
    "exam_planning": "pruefungen", "exam_design": "pruefungen",
    "exam_requirements": "pruefungen", "exam_sections": "pruefungen",
    "exam_conditions": "pruefungen", "exam_performance": "pruefungen",
    "klausur": "pruefungen", "Klausur": "pruefungen",
    "klausur_planung": "pruefungen", "Klausurplanung": "pruefungen",
    "klausur_details": "pruefungen", "klausur_niveau": "pruefungen",
    "klausur_parameter": "pruefungen", "klausur_thema": "pruefungen",
    "Klausurthema": "pruefungen", "klausur_design": "pruefungen",
    "Klausurstruktur": "pruefungen", "klausur_vorbereitung": "pruefungen",
    "klausur_präferenz": "pruefungen", "physics_exam_preparation": "pruefungen",
    "test_preparation": "pruefungen",
    # materialien
    "learning_material": "materialien", "Learning Material": "materialien",
    "Teaching Material": "materialien", "material": "materialien",
    "materials": "materialien", "lesson_material": "materialien",
    "content": "materialien", "content_creation": "materialien",
    "content_preferences": "materialien", "document_type": "materialien",
    "design_request": "materialien", "design_preference": "materialien",
    "design_style": "materialien", "learning_resource": "materialien",
    "learning_support": "materialien", "learning_request": "materialien",
    "resources": "materialien", "media": "materialien",
    "exercise_type": "materialien", "exercise_details": "materialien",
    "quiz_format": "materialien", "quiz_type": "materialien",
    "educational_request": "materialien", "teaching_skills": "materialien",
    # feedback
    "explicit": "feedback", "overview": "feedback",
    "type": "feedback", "capabilities": "feedback",
    "technical_limitation": "feedback", "security_awareness": "feedback",
    # curriculum
    "curriculum_focus": "curriculum", "curriculum_search": "curriculum",
    "curriculum_competencies": "curriculum", "lehrplan_interesse": "curriculum",
    "course_details": "curriculum", "Kompetenzen": "curriculum",
    "Lernziele": "curriculum", "Fachliche Ziele": "curriculum",
}

# Categories that map to themselves (already valid)
for cat in MEMORY_CATEGORIES_LIST:
    OLD_TO_NEW_CATEGORY[cat] = cat


async def run_cleanup(teacher_id: str | None = None) -> dict:
    """Hauptfunktion: Cleanup für einen oder alle Teacher."""
    stats = {"migrated": 0, "duplicates_removed": 0, "merged": 0, "archived": 0}

    if teacher_id:
        teacher_ids = [teacher_id]
    else:
        teachers = await db.select("teachers")
        teacher_ids = [t["id"] for t in (teachers or [])]

    for tid in teacher_ids:
        result = await _cleanup_teacher(tid)
        for k, v in result.items():
            stats[k] += v

    logger.info(f"Memory cleanup done: {stats}")
    return stats


async def _cleanup_teacher(teacher_id: str) -> dict:
    """Cleanup für einen einzelnen Teacher."""
    stats = {"migrated": 0, "duplicates_removed": 0, "merged": 0, "archived": 0}

    memories = await db.select(
        "user_memories",
        filters={"user_id": teacher_id},
        order="created_at.asc",
    )
    if not memories or not isinstance(memories, list):
        return stats

    logger.info(f"Cleaning up {len(memories)} memories for teacher {teacher_id[:8]}...")

    # ── Phase 0: Migrate old categories to fixed ones ──
    for m in memories:
        old_cat = m["category"]
        if old_cat not in MEMORY_CATEGORIES_LIST:
            new_cat = OLD_TO_NEW_CATEGORY.get(old_cat)
            if new_cat is None:
                logger.warning(f"Unmapped category '{old_cat}' → fallback 'feedback'")
                new_cat = "feedback"
            try:
                await db.update(
                    "user_memories",
                    {"category": new_cat},
                    filters={"id": m["id"]},
                )
                m["category"] = new_cat
                stats["migrated"] += 1
            except Exception as e:
                if "409" in str(e) or "Conflict" in str(e):
                    # Unique constraint conflict — duplicate after migration, delete this one
                    try:
                        await db.delete("user_memories", filters={"id": m["id"]})
                        stats["duplicates_removed"] += 1
                    except Exception:
                        pass
                else:
                    logger.warning(f"Failed to migrate category {old_cat}: {e}")

    # ── Phase 1: Exakte Duplikate löschen ──
    seen: dict[str, dict] = {}
    to_delete: list[str] = []

    for m in memories:
        fingerprint = f"{m['scope']}|{m['category']}|{m['key']}|{m['value']}"
        if fingerprint in seen:
            to_delete.append(seen[fingerprint]["id"])
            seen[fingerprint] = m
        else:
            seen[fingerprint] = m

    if to_delete:
        try:
            await db.delete_by_ids("user_memories", to_delete)
            stats["duplicates_removed"] = len(to_delete)
        except Exception as e:
            logger.warning(f"Failed to delete duplicates: {e}")

    # ── Phase 2: Key-Duplikate mergen ──
    key_groups: dict[str, list[dict]] = defaultdict(list)
    remaining = [m for m in memories if m["id"] not in to_delete]

    for m in remaining:
        key_groups[m["key"]].append(m)

    merge_delete: list[str] = []
    for group_key, group in key_groups.items():
        if len(group) <= 1:
            continue
        group.sort(
            key=lambda x: x.get("updated_at", x.get("created_at", "")),
            reverse=True,
        )
        keeper = group[0]
        for old in group[1:]:
            merge_delete.append(old["id"])

        max_importance = max(m.get("importance", 0.5) for m in group)
        if keeper.get("importance", 0.5) < max_importance:
            try:
                await db.update(
                    "user_memories",
                    {
                        "importance": max_importance,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    filters={"id": keeper["id"]},
                )
            except Exception as e:
                logger.warning(f"Failed to update importance for {keeper['id']}: {e}")

    if merge_delete:
        try:
            await db.delete_by_ids("user_memories", merge_delete)
            stats["merged"] = len(merge_delete)
        except Exception as e:
            logger.warning(f"Failed to delete merged: {e}")

    # ── Phase 3: Veraltete Einträge archivieren ──
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    all_deleted = set(to_delete + merge_delete)
    stale_ids = [
        m["id"]
        for m in remaining
        if m["id"] not in all_deleted
        and m.get("importance", 0.5) < 0.5
        and m.get("updated_at", m.get("created_at", "")) < cutoff
    ]

    if stale_ids:
        try:
            await db.delete_by_ids("user_memories", stale_ids)
            stats["archived"] = len(stale_ids)
        except Exception as e:
            logger.warning(f"Failed to archive stale: {e}")

    final_count = len(memories) - stats["duplicates_removed"] - stats["merged"] - stats["archived"]
    logger.info(
        f"Teacher {teacher_id[:8]}: "
        f"migrated {stats['migrated']}, removed {stats['duplicates_removed']} dupes, "
        f"merged {stats['merged']}, archived {stats['archived']} "
        f"(was {len(memories)}, now ~{final_count})"
    )

    return stats
