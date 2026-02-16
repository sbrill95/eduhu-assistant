"""Image serving router."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.agents.image_agent import get_stored_image

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/{image_id}")
async def serve_image(image_id: str):
    """Serve a generated image by ID."""
    result = get_stored_image(image_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    image_bytes, mime_type = result
    return Response(content=image_bytes, media_type=mime_type)
