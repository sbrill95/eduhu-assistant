from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app import db
from app.models import MaterialRequest, MaterialResponse, ExamTask, ExamStructure
from app.services.material_service import (
    generate_material as gen_mat,
    resolve_material_type,
    load_docx_from_db,
    MATERIALS_DIR,
)
from datetime import datetime, timezone
import base64
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/materials", tags=["Materials"])

@router.post("/generate", response_model=MaterialResponse)
async def generate_material(req: MaterialRequest):
    """Generate teaching material (Klausur or Differenzierung)."""
    try:
        result = await gen_mat(
            teacher_id=req.teacher_id,
            fach=req.fach,
            klasse=req.klasse,
            thema=req.thema,
            material_type=req.type,
            dauer_minuten=req.dauer_minuten or 45,
            zusatz_anweisungen=req.zusatz_anweisungen or "",
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Material generation failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(500, f"Materialerstellung fehlgeschlagen. Bitte versuche es erneut.")

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
    from app.agents.llm import get_haiku
    from pydantic_ai import Agent
    from app.docx_generator import generate_exam_docx
    
    # 1. Load material
    record = await db.select(
        "generated_materials",
        columns="content_json, teacher_id, type",
        filters={"id": material_id},
        single=True,
    )
    if not record:
        raise HTTPException(404, "Material nicht gefunden")
    if record.get("teacher_id") != teacher_id:
        raise HTTPException(403, "Zugriff verweigert")
    if record.get("type") != "klausur":
        raise HTTPException(400, "Nur Klausuren können gepatcht werden")

    content = record["content_json"]
    aufgaben = content.get("aufgaben", [])
    if task_index < 0 or task_index >= len(aufgaben):
        raise HTTPException(400, f"Aufgabe {task_index + 1} existiert nicht (max {len(aufgaben)})")

    alte_aufgabe = aufgaben[task_index]

    # 2. Generate only the replacement task
    task_agent = Agent(
        get_haiku(),
        output_type=ExamTask,
        instructions=f"""Du bist ein Experte für Klausuraufgaben. Erstelle eine EINZELNE neue Aufgabe.
Fach: {content.get('fach','?')}, Klasse: {content.get('klasse','?')}, Thema: {content.get('thema','?')}.

Die aktuelle Aufgabe:
- Titel: {alte_aufgabe.get('aufgabe','')}
- Beschreibung: {alte_aufgabe.get('beschreibung','')}
- AFB: {alte_aufgabe.get('afb_level','')}
- Punkte: {alte_aufgabe.get('punkte',0)}
- Erwartungshorizont: {alte_aufgabe.get('erwartung',[])}

Anweisung: {anweisung}

Behalte AFB-Level und Punktzahl bei, es sei denn die Anweisung sagt explizit etwas anderes.
Die Aufgabe MUSS konkrete Angaben enthalten (Zahlenwerte bei Berechnungen, klar definierte Teilaufgaben).""",
    )

    result = await task_agent.run(f"Erstelle eine neue Version der Aufgabe: {anweisung}")
    neue_aufgabe = result.output.model_dump()

    # 3. Patch only this task
    aufgaben[task_index] = neue_aufgabe
    content["aufgaben"] = aufgaben

    # 4. Regenerate DOCX
    exam = ExamStructure(**content)
    docx_bytes = generate_exam_docx(exam)

    # 5. Update DB + disk
    MATERIALS_DIR.mkdir(exist_ok=True)
    (MATERIALS_DIR / f"{material_id}.docx").write_bytes(docx_bytes)

    await db.update(
        "generated_materials",
        {"content_json": content, "docx_base64": base64.b64encode(docx_bytes).decode("ascii")},
        filters={"id": material_id},
    )

    return {
        "patched_task": task_index,
        "alte_aufgabe": alte_aufgabe,
        "neue_aufgabe": neue_aufgabe,
        "material_id": material_id,
        "docx_url": f"/api/materials/{material_id}/docx",
    }
