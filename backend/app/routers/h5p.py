from fastapi import APIRouter, HTTPException
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
            page_url=f"https://eduhu-assistant.pages.dev/ueben/{access_code}"
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
