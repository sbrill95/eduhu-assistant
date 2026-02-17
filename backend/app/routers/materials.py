import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models import MaterialRequest, MaterialResponse
from app.agents.material_learning_agent import run_download_learning
from app.services.material_service import (
    generate_material as gen_mat,
    resolve_material_type,
    load_docx_from_db,
    MATERIALS_DIR,
    patch_task,
)
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/materials", tags=["Materials"])

@router.post("/generate")
async def generate_material(req: MaterialRequest):
    """Generate teaching material (any of 12 types)."""
    try:
        result = await gen_mat(
            teacher_id=req.teacher_id,
            fach=req.fach,
            klasse=req.klasse,
            thema=req.thema,
            material_type=req.type,
            dauer_minuten=req.dauer_minuten or 45,
            zusatz_anweisungen=req.zusatz_anweisungen or "",
            conversation_id=getattr(req, 'conversation_id', ''),
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Material generation failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(500, "Materialerstellung fehlgeschlagen. Bitte versuche es erneut.")

    # Handle clarification (sub-agent needs more info)
    if result.result_type == "clarification":
        resp = {"type": "clarification", "question": result.summary, "session_id": result.session_id}
        if result.options:
            resp["options"] = result.options
        return resp

    now = datetime.now(timezone.utc).isoformat()
    return MaterialResponse(
        id=result.material_id,
        type=resolve_material_type(req.type),
        content=result.structure.model_dump(),
        docx_url=f"/api/materials/{result.material_id}/docx",
        created_at=now,
    )


@router.get("/{material_id}/docx")
async def download_material_docx(material_id: str):
    """Download generated material as DOCX (disk cache with DB fallback)."""
    docx_path = MATERIALS_DIR / f"{material_id}.docx"
    if not docx_path.exists():
        # Fallback: load from DB and re-cache on disk
        docx_bytes = await load_docx_from_db(material_id)
        if not docx_bytes:
            raise HTTPException(404, "Material nicht gefunden")
    # Fire-and-forget: Learning signal
    asyncio.create_task(run_download_learning(material_id))

    return FileResponse(
        path=str(docx_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"material-{material_id[:8]}.docx",
    )


@router.patch("/{material_id}/task/{task_index}")
async def patch_material_task(
    material_id: str,
    task_index: int,
    teacher_id: str = "",
    anweisung: str = "schwieriger machen",
):
    """Regeneriere eine einzelne Aufgabe einer Klausur. Rest bleibt identisch."""
    return await patch_task(material_id, task_index, teacher_id, anweisung)
