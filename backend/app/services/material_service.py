"""Material-Service — orchestriert Generierung, DOCX-Erstellung und Speicherung."""

import base64
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

from app import db
from app.models import MaterialRequest, ExamStructure, DifferenzierungStructure
from app.agents.material_router import run_material_agent
from app.docx_generator import generate_exam_docx, generate_diff_docx

logger = logging.getLogger(__name__)

MATERIALS_DIR = Path("/tmp/materials")

_TYPE_MAP = {
    "klassenarbeit": "klausur",
    "test": "klausur",
    "prüfung": "klausur",
    "pruefung": "klausur",
    "klausur": "klausur",
    "differenzierung": "differenzierung",
    "differenziert": "differenzierung",
}


def resolve_material_type(raw_type: str) -> str:
    """Normalize user-provided type to a canonical value."""
    return _TYPE_MAP.get(raw_type.lower(), "klausur")


@dataclass
class MaterialResult:
    material_id: str
    structure: ExamStructure | DifferenzierungStructure
    docx_bytes: bytes
    summary: str


async def generate_material(
    teacher_id: str,
    fach: str,
    klasse: str,
    thema: str,
    material_type: str = "klausur",
    dauer_minuten: int = 45,
    zusatz_anweisungen: str = "",
) -> MaterialResult:
    """Pipeline: Typ normalisieren -> Sub-Agent -> DOCX -> speichern -> Summary."""
    resolved_type = resolve_material_type(material_type)
    logger.info(f"Generating material: {resolved_type} (from '{material_type}') {fach} {klasse} {thema}")

    request = MaterialRequest(
        type=resolved_type,
        fach=fach,
        klasse=klasse,
        thema=thema,
        teacher_id=teacher_id,
        dauer_minuten=dauer_minuten,
        zusatz_anweisungen=zusatz_anweisungen or None,
    )

    structure = await run_material_agent(request)

    material_id = str(uuid.uuid4())

    if isinstance(structure, ExamStructure):
        docx_bytes = generate_exam_docx(structure)
        summary = _format_exam_summary(structure, material_id)
    elif isinstance(structure, DifferenzierungStructure):
        docx_bytes = generate_diff_docx(structure)
        summary = _format_diff_summary(structure, material_id)
    else:
        raise ValueError("Unbekannter Material-Typ")

    await _store_material(material_id, teacher_id, docx_bytes, structure, resolved_type)

    return MaterialResult(
        material_id=material_id,
        structure=structure,
        docx_bytes=docx_bytes,
        summary=summary,
    )


async def _store_material(
    material_id: str,
    teacher_id: str,
    docx_bytes: bytes,
    structure: ExamStructure | DifferenzierungStructure,
    material_type: str,
) -> None:
    """Store DOCX to disk cache and persist in DB."""
    # Disk cache (fast)
    MATERIALS_DIR.mkdir(exist_ok=True)
    (MATERIALS_DIR / f"{material_id}.docx").write_bytes(docx_bytes)

    # DB (durable across redeploys)
    try:
        await db.upsert(
            "generated_materials",
            {
                "id": material_id,
                "teacher_id": teacher_id,
                "type": material_type,
                "content_json": structure.model_dump(),
                "docx_base64": base64.b64encode(docx_bytes).decode("ascii"),
            },
            on_conflict="id",
        )
    except Exception as e:
        logger.warning(f"DB storage for material {material_id} failed (disk copy exists): {e}")


async def load_docx_from_db(material_id: str) -> bytes | None:
    """Load DOCX bytes from DB fallback when not on disk."""
    try:
        record = await db.select(
            "generated_materials",
            columns="docx_base64",
            filters={"id": material_id},
            single=True,
        )
        if record and isinstance(record, dict) and record.get("docx_base64"):
            docx_bytes = base64.b64decode(record["docx_base64"])
            # Re-cache on disk
            MATERIALS_DIR.mkdir(exist_ok=True)
            (MATERIALS_DIR / f"{material_id}.docx").write_bytes(docx_bytes)
            return docx_bytes
    except Exception as e:
        logger.error(f"DB fallback for material {material_id} failed: {e}")
    return None


def _format_exam_summary(exam: ExamStructure, material_id: str) -> str:
    tasks_summary = "\n".join(
        f"  {i}. {t.aufgabe} (AFB {t.afb_level}, {t.punkte}P)"
        for i, t in enumerate(exam.aufgaben, 1)
    )
    return (
        f"Klassenarbeit erstellt!\n\n"
        f"**{exam.fach} -- {exam.thema}** (Klasse {exam.klasse})\n"
        f"Dauer: {exam.dauer_minuten} Min. | Gesamtpunkte: {exam.gesamtpunkte}\n\n"
        f"**Aufgaben:**\n{tasks_summary}\n\n"
        f"Download: /api/materials/{material_id}/docx"
    )


def _format_diff_summary(diff: DifferenzierungStructure, material_id: str) -> str:
    niveaus_summary = "\n".join(
        f"  - {n.niveau}: {len(n.aufgaben)} Aufgaben, {n.zeitaufwand_minuten} Min."
        for n in diff.niveaus
    )
    return (
        f"Differenziertes Material erstellt!\n\n"
        f"**{diff.fach} -- {diff.thema}** (Klasse {diff.klasse})\n\n"
        f"**Niveaustufen:**\n{niveaus_summary}\n\n"
        f"Download: /api/materials/{material_id}/docx"
    )
