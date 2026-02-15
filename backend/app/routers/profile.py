from fastapi import APIRouter, HTTPException
from app import db
from app.models import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("/{teacher_id}")
async def get_profile(teacher_id: str):
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
async def update_profile(teacher_id: str, req: ProfileUpdate):
    data: dict = {}
    if req.bundesland is not None:
        data["bundesland"] = req.bundesland
    if req.schulform is not None:
        data["schulform"] = req.schulform
    if req.faecher is not None:
        data["faecher"] = req.faecher
    if req.jahrgaenge is not None:
        data["jahrgaenge"] = req.jahrgaenge

    result = await db.update("user_profiles", data, filters={"id": teacher_id})
    return result

def build_suggestions(profile: dict | None, memories: list[dict]) -> list[str]:
    """Build personalized prompt suggestions based on profile and memories."""
    suggestions = []
    profile = profile or {}

    # Priority 1: From memories (most specific)
    recent_topics = [m["value"] for m in memories if m["key"] in ["Thema", "Unterrichtsthema"] or m["category"] == "curriculum"]
    recent_klassen = [m["value"] for m in memories if m["key"] == "Klasse"]
    if recent_topics and recent_klassen:
        topic = recent_topics[0]
        klasse = recent_klassen[0]
        suggestions.append(f"Erstelle einen Test zu {topic} für Klasse {klasse}")
        suggestions.append(f"Erstelle differenziertes Material zu {topic}")

    # Priority 2: From profile (medium specific)
    faecher = profile.get("faecher", [])
    jahrgaenge = profile.get("jahrgaenge", [])
    if faecher and jahrgaenge:
        fach = faecher[0]
        jahrgang = jahrgaenge[0]
        suggestions.append(f"Plane eine Unterrichtsstunde {fach} für Klasse {jahrgang}")
        suggestions.append(f"Erstelle eine Klassenarbeit {fach} Klasse {jahrgang}")

    # Priority 3: Defaults (fallback)
    defaults = [
        "Plane eine Unterrichtsstunde für meine Klasse",
        "Erstelle Material zu einem Thema",
        "Hilf mir bei der Unterrichtsvorbereitung",
    ]

    # Return exactly 3 suggestions, unique and filled with defaults
    final_suggestions = list(dict.fromkeys(suggestions))  # Remove duplicates
    final_suggestions.extend(defaults)
    return final_suggestions[:3]

@router.get("/suggestions")  # Note: This is usually called as /api/suggestions in main, but let's mount it under /api/suggestions or similar. 
# Wait, main.py had /api/suggestions directly. Let's keep it consistent in main. 
# I'll put this logical part here but expose it correctly.
# Ideally, suggestions are related to the user/profile context. Let's keep it here but route it carefully.
async def get_suggestions(teacher_id: str):
    """Get personalized prompt suggestions for the chat welcome screen."""
    # 1. Load profile
    profile = await db.select("user_profiles", filters={"id": teacher_id}, single=True)

    # 2. Load memories
    memories_raw = await db.select(
        "user_memories",
        columns="key,value,category",
        filters={"user_id": teacher_id},
        order="importance.desc",
        limit=10,
    )
    memories = memories_raw if isinstance(memories_raw, list) else []

    # 3. Build suggestions
    suggestions = build_suggestions(profile, memories)
    return {"suggestions": suggestions}
