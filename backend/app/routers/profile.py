from collections import defaultdict
import random

from fastapi import APIRouter, HTTPException, Depends, Query
from app import db
from app.models import ProfileUpdate
from app.deps import get_current_teacher_id
from app.constants import MEMORY_CATEGORIES_LIST, MEMORY_CATEGORY_DESCRIPTIONS
from app.token_tracking import get_usage_summary

router = APIRouter(prefix="/api/profile", tags=["Profile"])


# ── Static routes FIRST (before /{teacher_id} catch-all) ──

@router.get("/memories")
async def get_memories(current_user_id: str = Depends(get_current_teacher_id)):
    """Get all memories grouped by category."""
    memories = await db.select(
        "user_memories",
        filters={"user_id": current_user_id},
        order="category.asc,importance.desc",
    )
    if not memories or not isinstance(memories, list):
        memories = []

    grouped: dict[str, list] = defaultdict(list)
    for m in memories:
        grouped[m["category"]].append({
            "id": m["id"],
            "key": m["key"],
            "value": m["value"],
            "scope": m.get("scope", "self"),
            "importance": m.get("importance", 0.5),
            "source": m.get("source", "inferred"),
            "created_at": str(m.get("created_at", "")),
        })

    categories_with_meta = {}
    for cat in MEMORY_CATEGORIES_LIST:
        categories_with_meta[cat] = {
            "description": MEMORY_CATEGORY_DESCRIPTIONS.get(cat, ""),
            "memories": grouped.get(cat, []),
            "count": len(grouped.get(cat, [])),
        }

    return {
        "total": len(memories),
        "categories": categories_with_meta,
    }


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user_id: str = Depends(get_current_teacher_id),
):
    """Delete a single memory."""
    memory = await db.select(
        "user_memories",
        filters={"id": memory_id, "user_id": current_user_id},
        single=True,
    )
    if not memory:
        raise HTTPException(404, "Memory nicht gefunden")

    await db.delete("user_memories", filters={"id": memory_id})
    return {"deleted": True}


@router.get("/token-usage")
async def get_token_usage(
    days: int = Query(default=7, ge=1, le=90),
    agent_type: str | None = Query(default=None),
    current_user_id: str = Depends(get_current_teacher_id),
):
    """Get token usage summary for the current teacher."""
    return await get_usage_summary(current_user_id, days=days, agent_type=agent_type)


@router.get("/suggestions")
async def get_suggestions(teacher_id: str = Depends(get_current_teacher_id)):
    """Get personalized prompt suggestions for the chat welcome screen."""
    profile = await db.select("user_profiles", filters={"id": teacher_id}, single=True)

    memories_raw = await db.select(
        "user_memories",
        filters={"user_id": teacher_id},
        order="importance.desc",
        limit=10,
    )
    memories = memories_raw if isinstance(memories_raw, list) else []

    suggestions = build_suggestions(profile, memories)
    return {"suggestions": suggestions}


# ── Dynamic routes ──

@router.get("/{teacher_id}")
async def get_profile(
    teacher_id: str,
    current_user_id: str = Depends(get_current_teacher_id),
):
    if teacher_id != current_user_id:
        raise HTTPException(403, "Zugriff verweigert")

    try:
        profile = await db.select(
            "user_profiles",
            filters={"id": teacher_id},
            single=True,
        )
    except Exception:
        raise HTTPException(404, "Profil nicht gefunden")
    if not profile:
        raise HTTPException(404, "Profil nicht gefunden")
    return profile


@router.patch("/{teacher_id}")
async def update_profile(
    teacher_id: str,
    req: ProfileUpdate,
    current_user_id: str = Depends(get_current_teacher_id),
):
    if teacher_id != current_user_id:
        raise HTTPException(403, "Zugriff verweigert")

    data: dict = {}
    if req.bundesland is not None:
        data["bundesland"] = req.bundesland
    if req.schulform is not None:
        data["schulform"] = req.schulform
    if req.faecher is not None:
        data["faecher"] = req.faecher
    if req.jahrgaenge is not None:
        data["jahrgaenge"] = req.jahrgaenge
    if req.onboarding_completed is not None:
        data["onboarding_completed"] = req.onboarding_completed

    result = await db.update("user_profiles", data, filters={"id": teacher_id})
    return result


# ── Helpers ──

def build_suggestions(profile: dict | None, memories: list[dict]) -> list[str]:
    """Build personalized prompt suggestions based on profile and memories."""
    suggestions = []
    profile = profile or {}

    recent_topics = [
        m["value"] for m in memories
        if m.get("key") in ["Thema", "Unterrichtsthema"] or m.get("category") == "curriculum"
    ]
    recent_klassen = [m["value"] for m in memories if m.get("key") == "Klasse"]
    if recent_topics and recent_klassen:
        topic = recent_topics[0]
        klasse = recent_klassen[0]
        suggestions.append(f"Erstelle einen Test zu {topic} für Klasse {klasse}")
        suggestions.append(f"Erstelle differenziertes Material zu {topic}")

    faecher = profile.get("faecher", [])
    jahrgaenge = profile.get("jahrgaenge", [])
    if faecher and jahrgaenge:
        fach = faecher[0]
        jahrgang = jahrgaenge[0]
        suggestions.append(f"Plane eine Unterrichtsstunde {fach} für Klasse {jahrgang}")
        suggestions.append(f"Erstelle eine Klassenarbeit {fach} Klasse {jahrgang}")

    if faecher:
        fach = faecher[0]
        new_types = [
            f"Erstelle ein Mystery zu einem {fach}-Thema",
            f"Erstelle einen Escape Room für {fach}",
            f"Erstelle ein Lernspiel für {fach}",
            f"Erstelle eine Hilfekarte für {fach}",
            f"Erstelle einen Podcast zu {fach}",
        ]
        suggestions.extend(random.sample(new_types, min(2, len(new_types))))

    defaults = [
        "Plane eine Unterrichtsstunde für meine Klasse",
        "Erstelle ein Quiz aus einem YouTube-Video",
        "Hilf mir bei der Unterrichtsvorbereitung",
    ]

    final_suggestions = list(dict.fromkeys(suggestions))
    final_suggestions.extend(defaults)
    return final_suggestions[:3]
