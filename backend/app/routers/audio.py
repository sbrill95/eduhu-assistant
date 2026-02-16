"""Audio router — TTS, Podcast audio, Conversation simulation audio."""

import logging
import random
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.agents.tts_agent import text_to_speech, AUDIO_DIR
from app import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["audio"])
public_router = APIRouter(prefix="/api/public/audio", tags=["audio-public"])


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"


class TTSResponse(BaseModel):
    audio_id: str
    audio_url: str


@router.post("/tts", response_model=TTSResponse)
async def tts_endpoint(req: TTSRequest):
    """Generate speech from text via ElevenLabs."""
    if not req.text.strip():
        raise HTTPException(400, "Text darf nicht leer sein")
    if len(req.text) > 5000:
        raise HTTPException(400, "Text zu lang (max 5000 Zeichen)")

    try:
        audio_id, _ = await text_to_speech(req.text, req.voice)
        return TTSResponse(audio_id=audio_id, audio_url=f"/api/audio/{audio_id}")
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        raise HTTPException(500, f"TTS-Fehler: {str(e)}")


@router.get("/{audio_id}")
async def get_audio(audio_id: str):
    """Serve a generated audio file."""
    path = AUDIO_DIR / f"{audio_id}.mp3"
    if not path.exists():
        raise HTTPException(404, "Audio nicht gefunden")
    return Response(
        content=path.read_bytes(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'inline; filename="{audio_id}.mp3"'},
    )


class ShareAudioRequest(BaseModel):
    teacher_id: str
    title: str
    audio_type: str  # tts, podcast, gespraechssimulation
    audio_ids: list[str]
    script: dict | None = None


class ShareAudioResponse(BaseModel):
    access_code: str
    page_url: str


def _generate_code() -> str:
    word = random.choice(["stern", "wolke", "blume", "feder", "funke", "perle", "licht", "welle"])
    num = random.randint(10, 99)
    return f"{word}{num}"


@router.post("/share", response_model=ShareAudioResponse)
async def share_audio(req: ShareAudioRequest):
    """Create a shareable audio page with access code (like H5P pages)."""
    code = _generate_code()
    try:
        await db.insert("audio_pages", {
            "teacher_id": req.teacher_id,
            "title": req.title,
            "access_code": code,
            "audio_type": req.audio_type,
            "script": req.script,
            "audio_ids": req.audio_ids,
        })
        return ShareAudioResponse(
            access_code=code,
            page_url=f"/audio/{code}",
        )
    except Exception as e:
        logger.error(f"Share audio failed: {e}")
        raise HTTPException(500, str(e))


# ── Public endpoints (no auth) ──

@public_router.get("/pages/{access_code}")
async def get_audio_page(access_code: str):
    """Public: Get audio page by access code."""
    page = await db.select("audio_pages", filters={"access_code": access_code}, single=True)
    if not page:
        raise HTTPException(404, "Audio-Seite nicht gefunden")
    return {
        "id": page["id"],
        "title": page["title"],
        "audio_type": page["audio_type"],
        "audio_ids": page.get("audio_ids", []),
        "script": page.get("script"),
    }
