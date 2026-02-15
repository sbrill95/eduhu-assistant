"""Image Agent — generates images via Gemini Imagen API."""
import base64
import logging
import uuid
from pathlib import Path

import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

# Store active image sessions for iterative editing
_image_sessions: dict[str, list[dict]] = {}


async def generate_image(teacher_id: str, prompt: str, session_id: str | None = None) -> dict:
    """Generate or edit an image using Gemini's image generation.

    Returns: {"image_base64": str, "session_id": str, "mime_type": str}
    """
    settings = get_settings()
    api_key = settings.gemini_api_key
    if not api_key:
        return {"error": "Gemini API Key nicht konfiguriert."}

    # Build message history for iterative editing
    if session_id and session_id in _image_sessions:
        messages = _image_sessions[session_id]
    else:
        session_id = str(uuid.uuid4())[:8]
        messages = []

    # Add new user message
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

        # Extract image from response
        candidates = data.get("candidates", [])
        if not candidates:
            return {"error": "Keine Antwort von Gemini erhalten."}

        parts = candidates[0].get("content", {}).get("parts", [])
        image_data = None
        text_response = ""

        for part in parts:
            if "inlineData" in part:
                image_data = part["inlineData"]["data"]
                mime_type = part["inlineData"].get("mimeType", "image/png")
            elif "text" in part:
                text_response = part["text"]

        if not image_data:
            return {"error": f"Kein Bild generiert. Antwort: {text_response[:200]}"}

        # Save to session for future edits
        response_parts = []
        if text_response:
            response_parts.append({"text": text_response})
        response_parts.append({"inlineData": {"mimeType": mime_type, "data": image_data}})
        messages.append({"role": "model", "parts": response_parts})
        _image_sessions[session_id] = messages

        return {
            "image_base64": image_data,
            "mime_type": mime_type,
            "session_id": session_id,
            "text": text_response,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini image API error: {e.response.status_code} {e.response.text[:500]}")
        return {"error": f"Gemini API Fehler: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return {"error": f"Bildgenerierung fehlgeschlagen: {str(e)}"}
