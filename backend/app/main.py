"""eduhu-assistant — FastAPI Backend."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.agents.main_agent import get_agent

# Import routers
from app.routers import auth, chat, profile, curriculum, materials, h5p, todos
from app.exceptions import global_exception_handler

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
    version="0.4.0",
    lifespan=lifespan,
)

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)

# Instrument FastAPI with Logfire
if logfire is not None:
    try:
        logfire.instrument_fastapi(app)
    except Exception:
        pass

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eduhu-assistant.pages.dev",
        "http://localhost:5173",
        "http://localhost:4173",
    ],  # Production + local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ──
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(profile.router)
app.include_router(curriculum.router)
app.include_router(materials.router)
app.include_router(h5p.router)
app.include_router(h5p.public_router)
app.include_router(todos.router)

from app.routers import transcribe
app.include_router(transcribe.router)

from app.routers import images
app.include_router(images.router)

from app.routers import audio
app.include_router(audio.router)
app.include_router(audio.public_router)


@app.get("/api/suggestions")
async def get_suggestions_wrapper(teacher_id: str):
    """Alias for /api/profile/suggestions to keep API consistent for frontend if needed."""
    # Note: If frontend calls /api/suggestions, we can redirect or just call the function
    return await profile.get_suggestions(teacher_id)


# ═══════════════════════════════════════
# Health
# ═══════════════════════════════════════

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.4.0", "material_types": 12, "routes": 45}


@app.post("/api/admin/memory-cleanup")
async def memory_cleanup(teacher_id: str | None = None):
    """Trigger memory cleanup. 2x/Tag via Cron oder manuell."""
    import os
    # Only allow in dev or with secret header
    secret = os.environ.get("ADMIN_SECRET", "cleanup-2026")
    # For now, no auth check — will add later
    from app.memory_cleanup import run_cleanup
    stats = await run_cleanup(teacher_id)
    return {"status": "ok", "stats": stats}


@app.post("/api/admin/knowledge-cleanup")
async def knowledge_cleanup(teacher_id: str | None = None):
    """Trigger knowledge cleanup — remove duplicates, archive low-quality, cap at 50."""
    from app.agents.knowledge import cleanup_knowledge
    stats = await cleanup_knowledge(teacher_id)
    return {"status": "ok", "stats": stats}


@app.post("/api/admin/seed-knowledge")
async def seed_knowledge():
    """Re-seed generic profiles into agent_knowledge."""
    from app.seed_knowledge import seed_generic_profiles
    count = await seed_generic_profiles()
    return {"status": "ok", "seeded": count}


@app.get("/api/debug/imports")
async def debug_imports():
    import os
    if os.environ.get("RENDER"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
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
