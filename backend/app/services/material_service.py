"""Material-Service — orchestriert Generierung, DOCX-Erstellung und Speicherung."""

import base64
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException
from pydantic_ai import Agent

from app import db
from app.models import MaterialRequest, ExamStructure, DifferenzierungStructure, ExamTask
from app.agents.material_router import run_material_agent, _normalize_type
from app.agents.llm import get_haiku
from app.docx_generator import (
    generate_exam_docx, generate_diff_docx, generate_generic_docx,
    generate_stundenplanung_docx, generate_mystery_docx, generate_escape_room_docx,
)

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
    conversation_id: str = "",
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
        conversation_id=conversation_id,
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
        from app.agents.mystery_agent import MysteryStructure
        from app.agents.escape_room_agent import EscapeRoomStructure
        if isinstance(structure, StundenplanungStructure):
            docx_bytes = generate_stundenplanung_docx(structure)
        elif isinstance(structure, MysteryStructure):
            docx_bytes = generate_mystery_docx(structure)
        elif isinstance(structure, EscapeRoomStructure):
            docx_bytes = generate_escape_room_docx(structure)
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
    from app.agents.klausur_agent import validate_afb_distribution
    
    tasks_summary = "\n".join(
        f"  {i}. {t.aufgabe} (AFB {t.afb_level}, {t.punkte}P)"
        for i, t in enumerate(exam.aufgaben, 1)
    )
    
    # AFB distribution check
    afb_warning = validate_afb_distribution(exam)
    afb_line = f"\n\n{afb_warning}" if afb_warning else ""
    
    return (
        f"Klassenarbeit erstellt!\n\n"
        f"**{exam.fach} -- {exam.thema}** (Klasse {exam.klasse})\n"
        f"Dauer: {exam.dauer_minuten} Min. | Gesamtpunkte: {exam.gesamtpunkte}\n\n"
        f"**Aufgaben:**\n{tasks_summary}\n\n"
        f"Download: /api/materials/{material_id}/docx"
        f"{afb_line}"
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


async def patch_task(material_id: str, task_index: int, teacher_id: str, anweisung: str) -> dict:
    """Patch a single task in a Klausur. Returns dict with alte_aufgabe, neue_aufgabe, material_id, docx_url."""
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
