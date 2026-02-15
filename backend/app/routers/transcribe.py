from fastapi import APIRouter, UploadFile, File, Depends
from app.deps import get_current_teacher_id
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Transcribe"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    teacher_id: str = Depends(get_current_teacher_id),
):
    """Transcribe audio via OpenAI Whisper API."""
    audio_bytes = await file.read()

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            files={
                "file": (
                    file.filename or "audio.webm",
                    audio_bytes,
                    file.content_type or "audio/webm",
                )
            },
            data={"model": "whisper-1", "language": "de"},
        )
        resp.raise_for_status()
        result = resp.json()

    return {"text": result.get("text", "")}
