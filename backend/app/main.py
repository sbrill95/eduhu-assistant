"""eduhu-assistant — FastAPI Backend."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.config import get_settings
from app.models import (
    LoginRequest, LoginResponse,
    ChatRequest, ChatResponse, ChatMessageOut,
    ProfileUpdate, ConversationOut,
    MaterialRequest, MaterialResponse,
)
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
async def chat_send(req: ChatRequest):
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
    deps = AgentDeps(teacher_id=teacher_id, conversation_id=conversation_id)

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
    from datetime import datetime, timezone
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

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi.responses import FileResponse

MATERIALS_DIR = Path("/tmp/materials")
MATERIALS_DIR.mkdir(exist_ok=True)

# In-memory store for generated materials (id -> MaterialResponse + exam data)
_materials_store: dict[str, dict] = {}


@app.post("/api/materials/generate", response_model=MaterialResponse)
async def generate_material(req: MaterialRequest):
    """Generate teaching material (Klausur or Differenzierung)."""
    from app.agents.material_agent import run_material_agent
    from app.docx_generator import generate_exam_docx, generate_diff_docx
    from app.models import ExamStructure, DifferenzierungStructure

    try:
        result = await run_material_agent(req)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Material generation failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(500, f"Materialerstellung fehlgeschlagen: {type(e).__name__}: {str(e)}")

    # Generate DOCX based on type
    material_id = str(uuid.uuid4())
    if isinstance(result, ExamStructure):
        docx_bytes = generate_exam_docx(result)
    elif isinstance(result, DifferenzierungStructure):
        docx_bytes = generate_diff_docx(result)
    else:
        docx_bytes = b""

    docx_path = MATERIALS_DIR / f"{material_id}.docx"
    if docx_bytes:
        docx_path.write_bytes(docx_bytes)

    now = datetime.now(timezone.utc).isoformat()
    response = MaterialResponse(
        id=material_id,
        type=req.type,
        content=result.model_dump(),
        docx_url=f"/api/materials/{material_id}/docx" if docx_bytes else None,
        created_at=now,
    )

    _materials_store[material_id] = {"response": response, "path": str(docx_path)}
    return response


@app.get("/api/materials/{material_id}/docx")
async def download_material_docx(material_id: str):
    """Download generated material as DOCX."""
    docx_path = MATERIALS_DIR / f"{material_id}.docx"
    if not docx_path.exists():
        raise HTTPException(404, "Material nicht gefunden")
    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"klassenarbeit-{material_id[:8]}.docx",
    )


# ═══════════════════════════════════════
# Health
# ═══════════════════════════════════════

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
