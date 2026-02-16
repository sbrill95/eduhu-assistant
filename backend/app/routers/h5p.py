from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app import db
from app.models import (
    H5PExerciseRequest, H5PExerciseResponse, PageOut
)
from app.agents.h5p_agent import run_h5p_agent
from app.h5p_generator import exercise_set_to_h5p
import logging
import uuid
import random

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exercises", tags=["H5P"])
public_router = APIRouter(prefix="/api/public", tags=["H5P Public"])

# H5P Access Code Generator
_NOUNS = [
    "tiger", "wolke", "stern", "apfel", "vogel", "blume", "stein", "welle",
    "fuchs", "regen", "sonne", "mond", "baum", "fisch", "adler", "birne",
    "drache", "feder", "garten", "hafen", "insel", "kaktus", "lampe", "mauer",
    "nacht", "ozean", "palme", "quarz", "rosen", "turm", "ufer", "wald",
]

def generate_access_code() -> str:
    """Generate a memorable access code like 'tiger42'."""
    return f"{random.choice(_NOUNS)}{random.randint(10, 99)}"

@router.post("/generate", response_model=H5PExerciseResponse)
async def generate_h5p_exercise(req: H5PExerciseRequest):
    try:
        # 1. Call H5P agent
        exercise_set = await run_h5p_agent(
            req.fach, req.klasse, req.thema, req.exercise_type, req.num_questions
        )

        # 2. Convert to H5P content — returns list of (content, type, title)
        h5p_exercises = exercise_set_to_h5p(exercise_set)

        page_id = req.page_id
        access_code = None

        # 3. If no page_id, create one
        if not page_id:
            page_record = await db.select(
                "exercise_pages",
                columns="id, access_code",
                filters={"teacher_id": req.teacher_id, "title": f"Klasse {req.klasse}"},
                single=True
            )
            if page_record:
                page_id = page_record["id"]
                access_code = page_record["access_code"]
            else:
                page_id = str(uuid.uuid4())
                access_code = generate_access_code()
                await db.insert(
                    "exercise_pages",
                    {"id": page_id, "teacher_id": req.teacher_id, "title": f"Klasse {req.klasse}", "access_code": access_code}
                )
        
        # 4. Insert each question as separate exercise
        first_exercise_id = None
        for h5p_content, h5p_type, title in h5p_exercises:
            exercise_id = str(uuid.uuid4())
            if first_exercise_id is None:
                first_exercise_id = exercise_id
            await db.insert(
                "exercises",
                {
                    "id": exercise_id,
                    "page_id": page_id,
                    "teacher_id": req.teacher_id,
                    "title": title,
                    "h5p_type": h5p_type,
                    "h5p_content": h5p_content
                }
            )

        # Get access code if it wasn't fetched/created
        if not access_code:
            page_info = await db.select(
                "exercise_pages", columns="access_code", filters={"id": page_id}, single=True
            )
            if page_info:
                access_code = page_info["access_code"]

        return H5PExerciseResponse(
            exercise_id=first_exercise_id,
            page_id=page_id,
            access_code=access_code,
            title=exercise_set.title,
            page_url=f"https://eduhu-assistant.pages.dev/s/{access_code}"
        )

    except Exception as e:
        logger.error(f"Error generating H5P exercise: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate exercise.")


@public_router.get("/pages/{access_code}")
async def get_public_page(access_code: str):
    """Public endpoint for students — no auth required."""
    page = await db.select(
        "exercise_pages",
        columns="id, title, access_code",
        filters={"access_code": access_code},
        single=True
    )
    if not page:
        raise HTTPException(status_code=404, detail="Seite nicht gefunden")
    
    exercises = await db.select(
        "exercises",
        columns="id, title, h5p_type",
        filters={"page_id": page["id"]},
        order="created_at.asc"
    )
    if not isinstance(exercises, list):
        exercises = []
    
    return {"page": page, "exercises": exercises}


@public_router.get("/h5p/{exercise_id}")
async def get_public_h5p_content(exercise_id: str):
    """Public endpoint — returns H5P JSON content for the player."""
    exercise = await db.select(
        "exercises",
        columns="h5p_content, h5p_type",
        filters={"id": exercise_id},
        single=True
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Übung nicht gefunden")
    return exercise["h5p_content"]


@public_router.get("/h5p/{exercise_id}/h5p.json")
async def get_h5p_metadata(exercise_id: str):
    """h5p-standalone metadata file."""
    exercise = await db.select(
        "exercises",
        columns="h5p_type, title",
        filters={"id": exercise_id},
        single=True
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Übung nicht gefunden")
    h5p_type = exercise["h5p_type"]
    # Map type to library version
    # Dependencies required by h5p-standalone to load libraries
    base_deps = [
        {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
        {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
        {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "H5P.Components", "majorVersion": 1, "minorVersion": 0},
        {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
        {"machineName": "jQuery.ui", "majorVersion": 1, "minorVersion": 10},
    ]
    
    type_deps = {
        "H5P.MultiChoice": [
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
        ],
        "H5P.Blanks": [
            {"machineName": "H5P.Blanks", "majorVersion": 1, "minorVersion": 14},
            {"machineName": "H5P.TextUtilities", "majorVersion": 1, "minorVersion": 3},
        ],
        "H5P.TrueFalse": [
            {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
        ],
        "H5P.DragText": [
            {"machineName": "H5P.DragText", "majorVersion": 1, "minorVersion": 10},
            {"machineName": "H5P.TextUtilities", "majorVersion": 1, "minorVersion": 3},
        ],
        "H5P.QuestionSet": [
            {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 20},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.Video", "majorVersion": 1, "minorVersion": 6},
        ],
    }
    
    preloaded = base_deps + type_deps.get(h5p_type, [])
    
    # Fix #4: Cache H5P responses — content never changes after creation
    return JSONResponse(
        content={
            "mainLibrary": h5p_type,
            "title": exercise.get("title", "Übung"),
            "preloadedDependencies": preloaded,
        },
        headers={"Cache-Control": "public, max-age=3600"},
    )


@public_router.get("/h5p/{exercise_id}/content/content.json")
async def get_h5p_content_json(exercise_id: str):
    """h5p-standalone content file."""
    import json as _json
    exercise = await db.select(
        "exercises",
        columns="h5p_content",
        filters={"id": exercise_id},
        single=True
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Übung nicht gefunden")
    content = exercise["h5p_content"]
    # Handle double-encoded JSON strings from older entries
    if isinstance(content, str):
        try:
            content = _json.loads(content)
        except (ValueError, TypeError):
            pass
    return JSONResponse(content=content, headers={"Cache-Control": "public, max-age=3600"})


@public_router.get("/poll/{access_code}")
async def get_poll(access_code: str):
    """Public: Get poll data for voting page."""
    poll = await db.select("polls", filters={"access_code": access_code, "active": True}, single=True)
    if not poll:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")
    return {
        "id": poll["id"],
        "question": poll["question"],
        "options": poll["options"],
        "access_code": access_code,
    }


@public_router.post("/poll/{access_code}/vote")
async def vote_poll(access_code: str, body: dict):
    """Public: Cast a vote."""
    option = body.get("option", "")
    if not option:
        raise HTTPException(status_code=400, detail="Option fehlt")
    
    poll = await db.select("polls", filters={"access_code": access_code, "active": True}, single=True)
    if not poll:
        raise HTTPException(status_code=404, detail="Abstimmung nicht gefunden")
    
    options = poll["options"] if isinstance(poll["options"], list) else []
    if option not in options:
        raise HTTPException(status_code=400, detail="Ungültige Option")
    
    votes = poll["votes"] if isinstance(poll["votes"], dict) else {}
    votes[option] = votes.get(option, 0) + 1
    
    await db.update("polls", {"votes": votes}, filters={"id": poll["id"]})
    return {"voted": True, "total": sum(votes.values())}


@router.get("/pages", response_model=list[PageOut])
async def list_exercise_pages(teacher_id: str):
    # This requires a custom query, which is not directly supported by the simple db wrapper.
    # For now, we'll fetch pages and then count exercises for each.
    # In a real app, a JOIN would be more efficient.
    pages = await db.select(
        "exercise_pages",
        columns="id, title, access_code",
        filters={"teacher_id": teacher_id},
        order="created_at.desc"
    )
    if not isinstance(pages, list):
        return []
    
    result = []
    for p in pages:
        # Count exercises
        # This is n+1 but acceptable for small scale
        exercises = await db.select(
            "exercises",
            columns="count",
            filters={"page_id": p["id"]},
            count=True
        )
        count = exercises if isinstance(exercises, int) else 0
        
        result.append(PageOut(
            id=p["id"],
            title=p["title"],
            access_code=p["access_code"],
            exercise_count=count
        ))
    
    return result

@router.delete("/pages/{page_id}")
async def delete_exercise_page(page_id: str, teacher_id: str):
    """Delete an exercise page and all exercises."""
    # Verify ownership
    page = await db.select(
        "exercise_pages",
        columns="id, teacher_id",
        filters={"id": page_id},
        single=True
    )
    if not page or page.get("teacher_id") != teacher_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Delete exercises for this page
    await db.delete("exercises", filters={"page_id": page_id})
    # Delete page
    await db.delete("exercise_pages", filters={"id": page_id})
    return {"deleted": True}
