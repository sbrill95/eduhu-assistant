"""Material-Service — orchestriert Generierung, DOCX-Erstellung und Speicherung."""

import base64
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

from app import db
from app.models import MaterialRequest, ExamStructure, DifferenzierungStructure
from app.agents.material_router import run_material_agent, _normalize_type
from app.docx_generator import generate_exam_docx, generate_diff_docx, generate_generic_docx, generate_stundenplanung_docx

logger = logging.getLogger(__name__)

MATERIALS_DIR = Path("/tmp/materials")

def resolve_material_type(raw_type: str) -> str:
    """Normalize user-provided type to a canonical value."""
    return _normalize_type(raw_type)


@dataclass
class MaterialResult:
    material_id: str
    structure: any  # ExamStructure, DifferenzierungStructure, or new agent types
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
        # All new agent types use generic or specialized DOCX
        from app.agents.stundenplanung_agent import StundenplanungStructure
        if isinstance(structure, StundenplanungStructure):
            docx_bytes = generate_stundenplanung_docx(structure)
        else:
            title = getattr(structure, "titel", "Material")
            docx_bytes = generate_generic_docx(structure, title)
        summary = _format_generic_summary(structure, material_id, resolved_type)

    await _store_material(material_id, teacher_id, docx_bytes, structure, resolved_type)

    # For audio-capable types, add audio generation hint to summary
    if resolved_type in ("podcast", "gespraechssimulation"):
        summary += "\n\n💡 Sag 'Als Audio generieren' um daraus eine Audiodatei zu erstellen."

    return MaterialResult(
        material_id=material_id,
        structure=structure,
        docx_bytes=docx_bytes,
        summary=summary,
    )


def _format_generic_summary(structure, material_id: str, material_type: str) -> str:
    """Format a summary for any new material type."""
    type_labels = {
        "hilfekarte": "Hilfekarte",
        "escape_room": "Escape Room",
        "mystery": "Mystery-Material",
        "lernsituation": "Lernsituation",
        "lernspiel": "Lernspiel",
        "versuchsanleitung": "Versuchsanleitung",
        "stundenplanung": "Stundenverlaufsplan",
    }
    label = type_labels.get(material_type, material_type.title())
    titel = getattr(structure, "titel", "Material")
    thema = getattr(structure, "thema", getattr(structure, "fach_thema", ""))

    return (
        f"{label} erstellt!\n\n"
        f"**{titel}**\n"
        f"Thema: {thema}\n\n"
        f"Download: /api/materials/{material_id}/docx"
    )


async def _store_material(
    material_id: str,
    teacher_id: str,
    docx_bytes: bytes,
    structure,
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
