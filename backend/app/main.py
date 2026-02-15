"""eduhu-assistant — FastAPI Backend."""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.config import get_settings
import random
import uuid
import json
from app.models import (
    LoginRequest, LoginResponse,
    ChatRequest, ChatResponse, ChatMessageOut,
    ProfileUpdate, ConversationOut,
    MaterialRequest, MaterialResponse,
    H5PExerciseRequest, H5PExerciseResponse,
    PageOut, PublicPage, PublicExercise, PublicExerciseWithContent,
)
from app.agents.h5p_agent import run_h5p_agent
from app.h5p_generator import exercise_set_to_h5p
from app.agents.main_agent import get_agent, AgentDeps
from app.agents.memory_agent import run_memory_agent
from app.agents.summary_agent import maybe_summarize
from app.ingestion import ingest_curriculum

# ── Logfire ──
try:
    import logfire
    _settings = get_settings()
    if _settings.logfire_token:
        logfire.configure(
            token=_settings.logfire_token,
            service_name="eduhu-assistant",
            inspect_arguments=False,
        )
        logfire.instrument_httpx()
        logging.info("Logfire configured ✅")
    else:
        logfire = None  # type: ignore
except Exception:
    logfire = None  # type: ignore

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("eduhu.log"),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🦉 eduhu-assistant starting...")
    # Pre-create agent
    get_agent()
    logger.info("✅ Agent ready")
    yield
    logger.info("🦉 eduhu-assistant shutting down")


app = FastAPI(
    title="eduhu-assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# Instrument FastAPI with Logfire
if logfire is not None:
    try:
        logfire.instrument_fastapi(app)
    except Exception:
        pass

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════
# H5P Access Code Generator
# ═══════════════════════════════════════

_NOUNS = [
    "tiger", "wolke", "stern", "apfel", "vogel", "blume", "stein", "welle",
    "fuchs", "regen", "sonne", "mond", "baum", "fisch", "adler", "birne",
    "drache", "feder", "garten", "hafen", "insel", "kaktus", "lampe", "mauer",
    "nacht", "ozean", "palme", "quarz", "rosen", "turm", "ufer", "wald",
]

def generate_access_code() -> str:
    """Generate a memorable access code like 'tiger42'."""
    return f"{random.choice(_NOUNS)}{random.randint(10, 99)}"


# ═══════════════════════════════════════
# Auth
# ═══════════════════════════════════════

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    teacher = await db.select(
        "teachers",
        columns="id, name",
        filters={"password": req.password.strip()},
        single=True,
    )
    if not teacher:
        raise HTTPException(401, "Falsches Passwort")

    # Ensure profile exists
    await db.upsert(
        "user_profiles",
        {"id": teacher["id"], "name": teacher["name"]},
        on_conflict="id",
    )

    return LoginResponse(teacher_id=teacher["id"], name=teacher["name"])


# ═══════════════════════════════════════
# Chat
# ═══════════════════════════════════════

@app.post("/api/chat/send", response_model=ChatResponse)
async def chat_send(req: ChatRequest, request: Request):
    teacher_id = req.teacher_id
    conversation_id = req.conversation_id

    # Create conversation if new
    if not conversation_id:
        conv = await db.insert(
            "conversations",
            {"user_id": teacher_id, "title": req.message[:80]},
        )
        conversation_id = conv["id"]

    # Store user message
    await db.insert("messages", {
        "conversation_id": conversation_id,
        "role": "user",
        "content": req.message,
    })

    # Load history
    history = await db.select(
        "messages",
        columns="role, content",
        filters={"conversation_id": conversation_id},
        order="created_at.asc",
        limit=20,
    )
    messages = history if isinstance(history, list) else []

    # Maybe summarize if conversation is long
    summary = await maybe_summarize(conversation_id, teacher_id, messages)

    # Run the agent
    agent = get_agent()
    deps = AgentDeps(
        teacher_id=teacher_id,
        conversation_id=conversation_id,
        base_url=str(request.base_url).rstrip("/"),
    )

    # Build message history for Pydantic AI
    from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse
    from pydantic_ai.messages import UserPromptPart, TextPart

    # The agent.run() takes a user prompt + message_history
    # We pass all but the last message as history, last as prompt
    message_history: list[ModelMessage] = []
    for m in messages[:-1]:
        if m["role"] == "user":
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=m["content"])])
            )
        else:
            message_history.append(
                ModelResponse(parts=[TextPart(content=m["content"])])
            )

    try:
        result = await agent.run(
            req.message,
            deps=deps,
            message_history=message_history,
        )
        assistant_text = result.output
    except Exception as e:
        logger.error(f"Agent error: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(500, f"KI-Antwort fehlgeschlagen: {type(e).__name__}")

    # Store assistant message
    saved = await db.insert("messages", {
        "conversation_id": conversation_id,
        "role": "assistant",
        "content": assistant_text,
    })

    # Update conversation timestamp
    await db.update(
        "conversations",
        {"updated_at": datetime.now(timezone.utc).isoformat()},
        filters={"id": conversation_id},
    )

    # Fire-and-forget: memory agent
    asyncio.create_task(
        run_memory_agent(teacher_id, conversation_id, messages + [
            {"role": "assistant", "content": assistant_text}
        ])
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message=ChatMessageOut(
            id=saved.get("id", f"msg-{conversation_id}"),
            role="assistant",
            content=assistant_text,
            timestamp=saved.get("created_at", ""),
        ),
    )


# ═══════════════════════════════════════
# History
# ═══════════════════════════════════════

@app.get("/api/chat/history")
async def chat_history(conversation_id: str):
    messages = await db.select(
        "messages",
        columns="id, role, content, created_at",
        filters={"conversation_id": conversation_id},
        order="created_at.asc",
    )
    return {
        "messages": [
            {"id": m["id"], "role": m["role"], "content": m["content"], "timestamp": m["created_at"]}
            for m in (messages if isinstance(messages, list) else [])
        ]
    }


@app.get("/api/chat/conversations")
async def chat_conversations(teacher_id: str):
    convs = await db.select(
        "conversations",
        columns="id, title, updated_at",
        filters={"user_id": teacher_id},
        order="updated_at.desc",
        limit=20,
    )
    return [
        ConversationOut(id=c["id"], title=c.get("title"), updated_at=c["updated_at"])
        for c in (convs if isinstance(convs, list) else [])
    ]


# ═══════════════════════════════════════
# Conversation Management
# ═══════════════════════════════════════

@app.delete("/api/chat/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, teacher_id: str):
    """Delete a conversation and its messages."""
    settings = get_settings()
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    base = settings.supabase_url
    import httpx
    async with httpx.AsyncClient() as client:
        # Delete messages first
        await client.delete(
            f"{base}/rest/v1/messages?conversation_id=eq.{conversation_id}",
            headers=headers,
        )
        # Delete session logs
        await client.delete(
            f"{base}/rest/v1/session_logs?conversation_id=eq.{conversation_id}",
            headers=headers,
        )
        # Delete conversation (verify ownership)
        await client.delete(
            f"{base}/rest/v1/conversations?id=eq.{conversation_id}&user_id=eq.{teacher_id}",
            headers=headers,
        )
    return {"deleted": True}


@app.patch("/api/chat/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, title: str = ""):
    """Update conversation title."""
    if title:
        await db.update(
            "conversations",
            {"title": title[:80]},
            filters={"id": conversation_id},
        )
    return {"updated": True}


# ═══════════════════════════════════════
# Profile
# ═══════════════════════════════════════

@app.get("/api/profile/{teacher_id}")
async def get_profile(teacher_id: str):
    profile = await db.select(
        "user_profiles",
        filters={"id": teacher_id},
        single=True,
    )
    if not profile:
        raise HTTPException(404, "Profil nicht gefunden")
    return profile


@app.patch("/api/profile/{teacher_id}")
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


# ═══════════════════════════════════════
# Curriculum Upload
# ═══════════════════════════════════════

@app.post("/api/curriculum/upload")
async def upload_curriculum(
    file: UploadFile = File(...),
    teacher_id: str = Form(...),
    fach: str = Form(...),
    jahrgang: str = Form(""),
    bundesland: str = Form(""),
):
    """Upload a curriculum PDF for ingestion (text → chunks → embeddings)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Nur PDF-Dateien werden unterstützt")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(400, "Datei zu groß (max 20 MB)")

    try:
        result = await ingest_curriculum(
            teacher_id=teacher_id,
            fach=fach,
            jahrgang=jahrgang,
            bundesland=bundesland,
            pdf_bytes=pdf_bytes,
            filename=file.filename,
        )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(500, f"Ingestion fehlgeschlagen: {str(e)}")


@app.get("/api/curriculum/list")
async def list_curricula(teacher_id: str):
    """List all curricula for a teacher."""
    curricula = await db.select(
        "user_curricula",
        columns="id, fach, jahrgang, bundesland, status, filename, created_at",
        filters={"user_id": teacher_id},
        order="created_at.desc",
    )
    return curricula if isinstance(curricula, list) else []


@app.delete("/api/curriculum/{curriculum_id}")
async def delete_curriculum(curriculum_id: str, teacher_id: str):
    """Delete a curriculum and its chunks."""
    settings = get_settings()
    # Delete chunks first
    url = f"{settings.supabase_url}/rest/v1/curriculum_chunks?curriculum_id=eq.{curriculum_id}"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    async with __import__("httpx").AsyncClient() as client:
        await client.delete(url, headers=headers)
    # Delete curriculum
    url2 = f"{settings.supabase_url}/rest/v1/user_curricula?id=eq.{curriculum_id}&user_id=eq.{teacher_id}"
    async with __import__("httpx").AsyncClient() as client:
        await client.delete(url2, headers=headers)
    return {"deleted": True}


# ═══════════════════════════════════════
# Suggestions
# ═══════════════════════════════════════

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


# ═══════════════════════════════════════
# Suggestions
# ═══════════════════════════════════════

@app.get("/api/suggestions")
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


# ═══════════════════════════════════════
# Health
# ═══════════════════════════════════════

# ═══════════════════════════════════════
# Materials
# ═══════════════════════════════════════

from fastapi.responses import FileResponse

from app.services.material_service import (
    generate_material as gen_mat,
    resolve_material_type,
    load_docx_from_db,
    MATERIALS_DIR,
)


@app.post("/api/materials/generate", response_model=MaterialResponse)
async def generate_material(req: MaterialRequest):
    """Generate teaching material (Klausur or Differenzierung)."""
    try:
        result = await gen_mat(
            teacher_id=req.teacher_id,
            fach=req.fach,
            klasse=req.klasse,
            thema=req.thema,
            material_type=req.type,
            dauer_minuten=req.dauer_minuten or 45,
            zusatz_anweisungen=req.zusatz_anweisungen or "",
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Material generation failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(500, f"Materialerstellung fehlgeschlagen: {type(e).__name__}: {str(e)}")

    now = datetime.now(timezone.utc).isoformat()
    return MaterialResponse(
        id=result.material_id,
        type=resolve_material_type(req.type),
        content=result.structure.model_dump(),
        docx_url=f"/api/materials/{result.material_id}/docx",
        created_at=now,
    )


@app.get("/api/materials/{material_id}/docx")
async def download_material_docx(material_id: str):
    """Download generated material as DOCX (disk cache with DB fallback)."""
    docx_path = MATERIALS_DIR / f"{material_id}.docx"
    if not docx_path.exists():
        # Fallback: load from DB and re-cache on disk
        docx_bytes = await load_docx_from_db(material_id)
        if not docx_bytes:
            raise HTTPException(404, "Material nicht gefunden")
    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"material-{material_id[:8]}.docx",
    )


# ═══════════════════════════════════════
# Health
# ═══════════════════════════════════════

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/debug/imports")
async def debug_imports():
    """Debug: test if all material imports work."""
    errors = []
    try:
        from app.agents.material_router import run_material_agent
    except Exception as e:
        errors.append(f"material_router: {e}")
    try:
        from app.agents.klausur_agent import get_klausur_agent
    except Exception as e:
        errors.append(f"klausur_agent: {e}")
    try:
        from app.agents.differenzierung_agent import get_diff_agent
    except Exception as e:
        errors.append(f"differenzierung_agent: {e}")
    try:
        from app.docx_generator import generate_exam_docx, generate_diff_docx
    except Exception as e:
        errors.append(f"docx_generator: {e}")
    try:
        from app.models import ExamStructure, DifferenzierungStructure
    except Exception as e:
        errors.append(f"models: {e}")
    return {"errors": errors, "ok": len(errors) == 0}


# ═══════════════════════════════════════
# H5P Endpoints
# ═══════════════════════════════════════

@app.post("/api/exercises/generate", response_model=H5PExerciseResponse)
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
            page_url=f"/s/{access_code}"
        )

    except Exception as e:
        logger.error(f"Error generating H5P exercise: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate exercise.")


@app.get("/api/exercises/pages", response_model=list[PageOut])
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
        pages = []

    page_outs = []
    for p in pages:
        count_res = await db.select(
            "exercises",
            columns="COUNT(id) as count",
            filters={"page_id": p["id"]},
            single=True
        )
        exercise_count = count_res["count"] if count_res else 0
        page_outs.append(PageOut(
            id=p["id"],
            title=p["title"],
            access_code=p["access_code"],
            exercise_count=exercise_count
        ))
    return page_outs


@app.get("/api/public/pages/{code}")
async def get_public_page(code: str):
    page_record = await db.select(
        "exercise_pages",
        columns="id, title, access_code",
        filters={"access_code": code},
        single=True
    )
    if not page_record:
        raise HTTPException(status_code=404, detail="Page not found")

    page = PublicPage(id=page_record["id"], title=page_record["title"], access_code=page_record["access_code"])

    exercise_records = await db.select(
        "exercises",
        columns="id, title, h5p_type, created_at",
        filters={"page_id": page.id},
        order="created_at.asc"
    )
    if not isinstance(exercise_records, list):
        exercise_records = []

    exercises = [
        PublicExercise(id=row["id"], title=row["title"], h5p_type=row["h5p_type"], created_at=str(row["created_at"]))
        for row in exercise_records
    ]

    return {"page": page, "exercises": exercises}


@app.get("/api/public/exercises/{exercise_id}", response_model=PublicExerciseWithContent)
async def get_public_exercise(exercise_id: str):
    record = await db.select(
        "exercises",
        columns="id, title, h5p_type, h5p_content, created_at",
        filters={"id": exercise_id},
        single=True
    )
    if not record:
        raise HTTPException(status_code=404, detail="Exercise not found")

    h5p_content = record["h5p_content"]
    if isinstance(h5p_content, str):
        h5p_content = json.loads(h5p_content)
    return PublicExerciseWithContent(
        id=record["id"],
        title=record["title"],
        h5p_type=record["h5p_type"],
        h5p_content=h5p_content,
        created_at=str(record["created_at"])
    )


# ── H5P Standalone endpoints ──

H5P_TYPE_MAP = {
    "H5P.MultiChoice": {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
    "H5P.Blanks": {"machineName": "H5P.Blanks", "majorVersion": 1, "minorVersion": 14},
    "H5P.TrueFalse": {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
    "H5P.DragText": {"machineName": "H5P.DragText", "majorVersion": 1, "minorVersion": 10},
}


@app.get("/api/public/h5p/{exercise_id}/h5p.json")
async def get_h5p_manifest(exercise_id: str):
    record = await db.select(
        "exercises",
        columns="id, title, h5p_type",
        filters={"id": exercise_id},
        single=True,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Exercise not found")
    lib = H5P_TYPE_MAP.get(record["h5p_type"], H5P_TYPE_MAP["H5P.MultiChoice"])
    return {
        "title": record["title"],
        "language": "de",
        "mainLibrary": lib["machineName"],
        "preloadedDependencies": [
            {"machineName": lib["machineName"], "majorVersion": lib["majorVersion"], "minorVersion": lib["minorVersion"]},
            {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
            {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
        ],
    }


@app.get("/api/public/h5p/{exercise_id}/content/content.json")
async def get_h5p_content(exercise_id: str):
    record = await db.select(
        "exercises",
        columns="id, h5p_content",
        filters={"id": exercise_id},
        single=True,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Exercise not found")
    h5p_content = record["h5p_content"]
    if isinstance(h5p_content, str):
        h5p_content = json.loads(h5p_content)
    return h5p_content
