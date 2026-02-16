"""Image Agent — generates images via Gemini Imagen API."""
import base64
import logging
import uuid

import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

# Store active image sessions for iterative editing
_image_sessions: dict[str, list[dict]] = {}
# Store generated images for serving
_image_store: dict[str, tuple[bytes, str]] = {}  # id -> (bytes, mime_type)


def get_stored_image(image_id: str) -> tuple[bytes, str] | None:
    """Retrieve a stored image by ID."""
    return _image_store.get(image_id)


async def generate_image(teacher_id: str, prompt: str, session_id: str | None = None) -> dict:
    """Generate or edit an image using Gemini's image generation."""
    settings = get_settings()
    api_key = settings.gemini_api_key
    if not api_key:
        return {"error": "Gemini API Key nicht konfiguriert. Bitte GEMINI_API_KEY in den Umgebungsvariablen setzen."}

    # Build message history for iterative editing
    if session_id and session_id in _image_sessions:
        messages = _image_sessions[session_id]
    else:
        session_id = str(uuid.uuid4())[:8]
        messages = []

    messages.append({"role": "user", "parts": [{"text": prompt}]})

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}",
                json={
                    "contents": messages,
                    "generationConfig": {
                        "responseModalities": ["TEXT", "IMAGE"],
                    },
                },
            )
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "Keine Antwort von Gemini erhalten."}

        parts = candidates[0].get("content", {}).get("parts", [])
        image_data = None
        text_response = ""
        mime_type = "image/png"

        for part in parts:
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
                mime_type = part["inlineData"].get("mimeType", "image/png")
            elif "text" in part:
                text_response = part["text"]

        if not image_data:
            return {"error": f"Kein Bild generiert. Antwort: {text_response[:200]}"}

        # Store image in memory for serving via API
        image_id = str(uuid.uuid4())[:12]
        image_bytes = base64.b64decode(image_data)
        _image_store[image_id] = (image_bytes, mime_type)

        # Save to session for future edits
        response_parts = []
        if text_response:
            response_parts.append({"text": text_response})
        response_parts.append({"inlineData": {"mimeType": mime_type, "data": image_data}})
        messages.append({"role": "model", "parts": response_parts})
        _image_sessions[session_id] = messages

        # Clean up old images (keep last 50)
        if len(_image_store) > 50:
            oldest = list(_image_store.keys())[:-50]
            for k in oldest:
                del _image_store[k]

        return {
            "image_id": image_id,
            "session_id": session_id,
            "mime_type": mime_type,
            "text": text_response,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini image API error: {e.response.status_code} {e.response.text[:500]}")
        return {"error": f"Gemini API Fehler: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {"error": f"Bildgenerierung fehlgeschlagen: {str(e)}"}
