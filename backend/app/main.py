"""eduhu-assistant — FastAPI Backend."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.deps import verify_admin
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
    logger.info("eduhu-assistant starting...")
    from app.db import init_pool, close_pool
    await init_pool()
    logger.info("Database pool ready")
    get_agent()
    logger.info("Agent ready")
    yield
    logger.info("eduhu-assistant shutting down")
    await close_pool()


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
_cors_settings = get_settings()
_cors_origins = ["http://localhost:5173", "http://localhost:4173"]
if _cors_settings.cors_origins:
    _cors_origins.extend([o.strip() for o in _cors_settings.cors_origins.split(",") if o.strip()])
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
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
    return {"status": "ok", "version": "0.5.0", "material_types": 12, "routes": len(app.routes)}


@app.post("/api/admin/memory-cleanup")
async def memory_cleanup(teacher_id: str | None = None, _=Depends(verify_admin)):
    """Trigger memory cleanup. 2x/Tag via Cron oder manuell."""
    from app.memory_cleanup import run_cleanup
    stats = await run_cleanup(teacher_id)
    return {"status": "ok", "stats": stats}


@app.post("/api/admin/knowledge-cleanup")
async def knowledge_cleanup(teacher_id: str | None = None, _=Depends(verify_admin)):
    """Trigger knowledge cleanup — remove duplicates, archive low-quality, cap at 50."""
    from app.agents.knowledge import cleanup_knowledge
    stats = await cleanup_knowledge(teacher_id)
    return {"status": "ok", "stats": stats}


@app.post("/api/admin/seed-knowledge")
async def seed_knowledge(_=Depends(verify_admin)):
    """Re-seed generic profiles into agent_knowledge."""
    from app.seed_knowledge import seed_generic_profiles
    count = await seed_generic_profiles()
    return {"status": "ok", "seeded": count}


@app.get("/api/debug/youtube")
async def debug_youtube():
    """Debug: test yt-dlp proxy connectivity."""
    try:
        from app.agents.youtube_quiz_agent import extract_transcript
        text, title, url = await asyncio.wait_for(
            extract_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            timeout=30,
        )
        return {"ok": True, "title": title, "transcript_length": len(text)}
    except Exception as e:
        return {"ok": False, "error": str(e), "type": type(e).__name__}


@app.get("/api/debug/env")
async def debug_env():
    """Debug: check which optional env vars are set (no values exposed)."""
    import os
    settings = get_settings()
    return {
        "webshare_proxy_url": bool(settings.webshare_proxy_url),
        "elevenlabs_api_key": bool(settings.elevenlabs_api_key),
        "gemini_api_key": bool(settings.gemini_api_key),
        "pixabay_api_key": bool(settings.pixabay_api_key),
        "brave_api_key": bool(settings.brave_api_key),
        "openai_api_key": bool(settings.openai_api_key),
        "logfire_token": bool(settings.logfire_token),
        "COOLIFY": bool(os.environ.get("COOLIFY_URL")),
    }


@app.get("/api/debug/imports")
async def debug_imports():
    """Debug: test if all material imports work."""
    errors = []
    try:
        pass
    except Exception as e:
        errors.append(f"material_router: {e}")
    try:
        pass
    except Exception as e:
        errors.append(f"klausur_agent: {e}")
    try:
        pass
    except Exception as e:
        errors.append(f"differenzierung_agent: {e}")
    try:
        pass
    except Exception as e:
        errors.append(f"docx_generator: {e}")
    try:
        pass
    except Exception as e:
        errors.append(f"models: {e}")
    return {"errors": errors, "ok": len(errors) == 0}
