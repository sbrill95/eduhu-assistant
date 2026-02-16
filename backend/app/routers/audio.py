"""Audio router — TTS, Podcast audio, Conversation simulation audio."""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.agents.tts_agent import text_to_speech, generate_dialogue, AUDIO_DIR

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["audio"])


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
