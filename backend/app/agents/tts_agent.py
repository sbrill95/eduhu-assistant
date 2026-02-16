"""TTS Agent — Text-to-Speech via ElevenLabs API."""

import logging
import uuid
from pathlib import Path

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

AUDIO_DIR = Path("/tmp/audio")

# Default German voices
VOICES = {
    "default": "JH302OKVzGGJc47f08ex",      # Manuel — German male narrator
    "male": "kkJxCnlRCckmfFvzDW5Q",         # Alexander — German male
    "female": "iTisibUrmoYf5lx0UXC3",       # Simone K. — German female  
    "educator": "JH302OKVzGGJc47f08ex",     # Manuel — narrator style
    "storyteller": "eJHgBguIWw9PtA4GHbSP",  # Clemens Hartmann — dramatic
}


async def text_to_speech(
    text: str,
    voice: str = "default",
    model_id: str = "eleven_multilingual_v2",
) -> tuple[str, bytes]:
    """Convert text to speech. Returns (audio_id, mp3_bytes)."""
    settings = get_settings()
    api_key = settings.elevenlabs_api_key
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY nicht konfiguriert")

    voice_id = VOICES.get(voice, voice)  # Allow direct voice_id too
    
    audio_id = str(uuid.uuid4())

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            },
        )
        response.raise_for_status()
        audio_bytes = response.content

    # Cache to disk
    AUDIO_DIR.mkdir(exist_ok=True)
    (AUDIO_DIR / f"{audio_id}.mp3").write_bytes(audio_bytes)

    logger.info(f"TTS generated: {audio_id} ({len(audio_bytes)} bytes, voice={voice})")
    return audio_id, audio_bytes


async def generate_dialogue(
    script: list[dict],  # [{"speaker": "Arzt", "voice": "male", "text": "..."}, ...]
    model_id: str = "eleven_multilingual_v2",
) -> tuple[str, bytes]:
    """Generate a multi-voice dialogue by concatenating TTS segments.
    
    Returns (audio_id, mp3_bytes) of the concatenated audio.
    """
    settings = get_settings()
    api_key = settings.elevenlabs_api_key
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY nicht konfiguriert")

    segments: list[bytes] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for entry in script:
            voice_id = VOICES.get(entry.get("voice", "default"), entry.get("voice", VOICES["default"]))
            
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": entry["text"],
                    "model_id": model_id,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
            )
            response.raise_for_status()
            segments.append(response.content)

    # Simple concatenation of MP3 segments (works for MP3 format)
    audio_id = str(uuid.uuid4())
    combined = b"".join(segments)

    AUDIO_DIR.mkdir(exist_ok=True)
    (AUDIO_DIR / f"{audio_id}.mp3").write_bytes(combined)

    logger.info(f"Dialogue generated: {audio_id} ({len(combined)} bytes, {len(script)} segments)")
    return audio_id, combined
