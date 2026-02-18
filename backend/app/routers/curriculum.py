from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app import db
from app.ingestion import ingest_curriculum
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/curriculum", tags=["Curriculum"])

@router.post("/upload")
async def upload_curriculum(
    file: UploadFile = File(...),
    teacher_id: str = Form(...),
    fach: str = Form(...),
    jahrgang: str = Form(""),
    bundesland: str = Form(""),
):
    """Upload a curriculum PDF for ingestion (text → chunks → embeddings)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Nur PDF-Dateien werden unterstützt")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(400, "Datei zu groß (max 20 MB)")

    try:
        result = await ingest_curriculum(
            teacher_id=teacher_id,
            fach=fach,
            jahrgang=jahrgang,
            bundesland=bundesland,
            pdf_bytes=pdf_bytes,
            filename=file.filename,
        )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(500, f"Ingestion fehlgeschlagen: {str(e)}")


@router.get("/list")
async def list_curricula(teacher_id: str):
    """List all curricula for a teacher."""
    curricula = await db.select(
        "user_curricula",
        columns="id, fach, jahrgang, bundesland, status, filename, created_at",
        filters={"user_id": teacher_id},
        order="created_at.desc",
    )
    return curricula if isinstance(curricula, list) else []


@router.delete("/{curriculum_id}")
async def delete_curriculum(curriculum_id: str, teacher_id: str):
    """Delete a curriculum and its chunks."""
    await db.delete("curriculum_chunks", filters={"curriculum_id": curriculum_id})
    await db.delete("user_curricula", filters={"id": curriculum_id, "user_id": teacher_id})
    return {"deleted": True}
