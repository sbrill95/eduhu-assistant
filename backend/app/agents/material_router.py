"""Material Router — routes material generation requests to sub-agents."""

import asyncio
import logging

from app.config import get_settings
from app.models import ExamStructure, DifferenzierungStructure, MaterialRequest
from app.agents.klausur_agent import get_klausur_agent, KlausurDeps
from app.agents.differenzierung_agent import get_diff_agent, DiffDeps
from app.agents.hilfekarten_agent import get_hilfekarten_agent, HilfekarteDeps
from app.agents.escape_room_agent import get_escape_room_agent, EscapeRoomDeps
from app.agents.mystery_agent import get_mystery_agent, MysteryDeps
from app.agents.lernsituation_agent import get_lernsituation_agent, LernsituationDeps
from app.agents.lernspiel_agent import get_lernspiel_agent, LernspielDeps
from app.agents.versuchsanleitung_agent import get_versuchsanleitung_agent, VersuchsanleitungDeps
from app.agents.stundenplanung_agent import get_stundenplanung_agent, StundenplanungDeps
from app.agents.system_prompt import build_block3_context
from app.agents.knowledge import build_wissenskarte
from app import db

logger = logging.getLogger(__name__)

# Map of supported material types to their agent_type keys
SUPPORTED_TYPES = {
    "klausur", "klassenarbeit", "differenzierung",
    "hilfekarte", "escape_room", "mystery",
    "lernsituation", "lernspiel", "versuchsanleitung",
    "stundenplanung",
}

# Normalize aliases
TYPE_ALIASES = {
    "klassenarbeit": "klausur",
    "arbeitsblatt": "versuchsanleitung",
    "experiment": "versuchsanleitung",
    "unterrichtsplanung": "stundenplanung",
    "verlaufsplan": "stundenplanung",
}


def _normalize_type(material_type: str) -> str:
    t = material_type.lower().strip()
    return TYPE_ALIASES.get(t, t)


def _is_retryable(exc: Exception) -> bool:
    name = type(exc).__name__
    return any(keyword in name for keyword in ("Timeout", "Connection", "Server", "502", "503", "529"))


async def run_material_agent(request: MaterialRequest):
    """Route to the correct sub-agent based on request type."""
    material_type = _normalize_type(request.type)

    if material_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Material-Typ '{request.type}' wird nicht unterstützt. "
            f"Verfügbar: {', '.join(sorted(SUPPORTED_TYPES))}"
        )

    settings = get_settings()
    timeout = settings.sub_agent_timeout_seconds
    max_retries = settings.sub_agent_max_retries

    teacher_context = await build_block3_context(request.teacher_id)
    wissenskarte = await build_wissenskarte(request.teacher_id, material_type, request.fach)

    prompt = _build_prompt(request, material_type)

    if material_type == "klausur":
        agent = get_klausur_agent()
        deps = KlausurDeps(teacher_id=request.teacher_id, fach=request.fach,
                           teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "differenzierung":
        agent = get_diff_agent()
        deps = DiffDeps(teacher_id=request.teacher_id, teacher_context=teacher_context)
    elif material_type == "hilfekarte":
        agent = get_hilfekarten_agent()
        deps = HilfekarteDeps(teacher_id=request.teacher_id, fach=request.fach,
                              teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "escape_room":
        agent = get_escape_room_agent()
        deps = EscapeRoomDeps(teacher_id=request.teacher_id, fach=request.fach,
                              teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "mystery":
        agent = get_mystery_agent()
        deps = MysteryDeps(teacher_id=request.teacher_id, fach=request.fach,
                           teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "lernsituation":
        agent = get_lernsituation_agent()
        deps = LernsituationDeps(teacher_id=request.teacher_id, fach=request.fach,
                                 teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "lernspiel":
        agent = get_lernspiel_agent()
        deps = LernspielDeps(teacher_id=request.teacher_id, fach=request.fach,
                             teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "versuchsanleitung":
        agent = get_versuchsanleitung_agent()
        deps = VersuchsanleitungDeps(teacher_id=request.teacher_id, fach=request.fach,
                                     teacher_context=teacher_context, wissenskarte=wissenskarte)
    elif material_type == "stundenplanung":
        agent = get_stundenplanung_agent()
        deps = StundenplanungDeps(teacher_id=request.teacher_id, fach=request.fach,
                                  teacher_context=teacher_context, wissenskarte=wissenskarte)
    else:
        raise ValueError(f"Kein Agent für Typ '{material_type}'")

    logger.info(f"Running {material_type} agent: {request.fach} {request.klasse} {request.thema}")

    last_error: Exception | None = None
    for attempt in range(1 + max_retries):
        try:
            result = await asyncio.wait_for(
                agent.run(prompt, deps=deps),
                timeout=timeout,
            )
            return result.output
        except asyncio.TimeoutError:
            logger.warning(f"{material_type} agent timeout, Versuch {attempt + 1}")
            last_error = TimeoutError(f"{material_type}-Agent hat nach {timeout}s nicht geantwortet")
        except Exception as e:
            if _is_retryable(e) and attempt < max_retries:
                logger.warning(f"{material_type} agent error (retryable), Versuch {attempt + 1}: {e}")
                await asyncio.sleep(2 ** attempt)
                last_error = e
            else:
                raise
    raise last_error  # type: ignore[misc]


def _build_prompt(request: MaterialRequest, material_type: str) -> str:
    """Build the generation prompt from the request."""
    type_labels = {
        "klausur": "eine Klassenarbeit/Klausur",
        "differenzierung": "differenziertes Material in 3 Niveaustufen",
        "hilfekarte": "eine Hilfekarte für Schüler",
        "escape_room": "einen Escape Room für den Unterricht",
        "mystery": "ein Mystery-Material mit Informationskarten",
        "lernsituation": "eine Lernsituation für die berufliche Bildung",
        "lernspiel": "ein Lernspiel",
        "versuchsanleitung": "eine Versuchsanleitung / ein Arbeitsblatt",
        "stundenplanung": "einen Stundenverlaufsplan",
    }

    parts = [
        f"Erstelle {type_labels.get(material_type, material_type)}:",
        f"- Fach: {request.fach}",
        f"- Klasse/Jahrgang: {request.klasse}",
        f"- Thema: {request.thema}",
    ]
    if request.dauer_minuten:
        parts.append(f"- Dauer/Zeitrahmen: {request.dauer_minuten} Minuten")
    if request.afb_verteilung:
        parts.append(f"- AFB-Verteilung: {request.afb_verteilung}")
    if request.zusatz_anweisungen:
        parts.append(f"- Zusätzliche Anweisungen: {request.zusatz_anweisungen}")

    return "\n".join(parts)
