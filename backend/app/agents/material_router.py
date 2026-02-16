"""Material Router — routes material generation requests to sub-agents."""

import asyncio
import logging

from app.config import get_settings
from app.models import ExamStructure, DifferenzierungStructure, MaterialRequest
from app.agents.klausur_agent import get_klausur_agent, KlausurDeps
from app.agents.differenzierung_agent import get_diff_agent, DiffDeps
from app.agents.system_prompt import build_block3_context
from app.agents.knowledge import build_wissenskarte
from app import db
import json

logger = logging.getLogger(__name__)


async def _load_material_context(teacher_id: str, material_type: str, fach: str) -> str:
    """Load preferences and templates to enrich the generation prompt."""
    parts = []

    # 1. Load personal preferences
    try:
        prefs = await db.select(
            "material_preferences",
            filters={"teacher_id": teacher_id, "material_type": material_type},
            single=True,
        )
        if prefs and prefs.get("preferences"):
            p = prefs["preferences"]
            parts.append("## Persönliche Präferenzen dieser Lehrkraft:")
            for key, val in p.items():
                parts.append(f"- {key}: {val}")
    except Exception as e:
        logger.debug(f"No preferences found: {e}")

    # 2. Load best personal template (highest rated, same fach)
    try:
        templates = await db.select(
            "material_templates",
            filters={"teacher_id": teacher_id, "material_type": material_type, "fach": fach},
            order="rating.desc",
            limit=1,
        )
        if templates and isinstance(templates, list) and len(templates) > 0:
            t = templates[0]
            content = t.get("content_json", {})
            parts.append(f"\n## Eigene Vorlage (Rating {t.get('rating', '?')}/5):")
            parts.append(f"Thema: {content.get('thema', '?')}, {len(content.get('aufgaben', []))} Aufgaben")
            if t.get("teacher_notes"):
                parts.append(f"Anmerkung: {t['teacher_notes']}")
            # Show structure as example
            for i, aufg in enumerate(content.get("aufgaben", [])[:3], 1):
                parts.append(f"  Aufgabe {i}: {aufg.get('aufgabe', '?')} (AFB {aufg.get('afb_level', '?')}, {aufg.get('punkte', '?')}P)")
            parts.append("→ Orientiere dich am Stil und Format dieser Vorlage!")
    except Exception as e:
        logger.debug(f"No templates found: {e}")

    # 3. Load good practice (global, same fach)
    try:
        gp = await db.select(
            "good_practice_materials",
            filters={"material_type": material_type, "fach": fach},
            order="quality_score.desc",
            limit=1,
        )
        if gp and isinstance(gp, list) and len(gp) > 0:
            g = gp[0]
            parts.append(f"\n## Good-Practice-Vorlage ({g.get('title', '?')}):")
            parts.append(f"{g.get('beschreibung', '')}")
            content = g.get("content_json", {})
            for i, aufg in enumerate(content.get("aufgaben", [])[:3], 1):
                parts.append(f"  Aufgabe {i}: {aufg.get('aufgabe', '?')} (AFB {aufg.get('afb_level', '?')}, {aufg.get('punkte', '?')}P)")
    except Exception as e:
        logger.debug(f"No good practices found: {e}")

    return "\n".join(parts) if parts else ""


def _is_retryable(exc: Exception) -> bool:
    """Check if an exception is worth retrying (transient errors)."""
    name = type(exc).__name__
    return any(keyword in name for keyword in ("Timeout", "Connection", "Server", "502", "503", "529"))


async def run_material_agent(request: MaterialRequest) -> ExamStructure | DifferenzierungStructure:
    """Route to the correct sub-agent based on request type."""
    if request.type == "klausur":
        return await _generate_klausur(request)
    elif request.type == "differenzierung":
        return await _generate_differenzierung(request)
    else:
        raise ValueError(f"Material-Typ '{request.type}' wird noch nicht unterstützt.")


async def _generate_klausur(request: MaterialRequest) -> ExamStructure:
    """Run the klausur agent with timeout and retry."""
    settings = get_settings()
    timeout = settings.sub_agent_timeout_seconds
    max_retries = settings.sub_agent_max_retries

    agent = get_klausur_agent()
    teacher_context = await build_block3_context(request.teacher_id)
    wissenskarte = await build_wissenskarte(request.teacher_id, "klausur", request.fach)
    deps = KlausurDeps(
        teacher_id=request.teacher_id,
        fach=request.fach,
        teacher_context=teacher_context,
        wissenskarte=wissenskarte,
    )

    # Legacy context loading (will be fully replaced by Wissenskarte)
    preferences_context = await _load_material_context(request.teacher_id, "klausur", request.fach)

    prompt_parts = [
        f"Erstelle eine Klassenarbeit/Klausur:",
        f"- Fach: {request.fach}",
        f"- Klasse/Jahrgang: {request.klasse}",
        f"- Thema: {request.thema}",
    ]
    if request.dauer_minuten:
        prompt_parts.append(f"- Dauer: {request.dauer_minuten} Minuten")
    if request.afb_verteilung:
        prompt_parts.append(f"- AFB-Verteilung: {request.afb_verteilung}")
    if request.zusatz_anweisungen:
        prompt_parts.append(f"- Zusätzliche Anweisungen: {request.zusatz_anweisungen}")
    if preferences_context:
        prompt_parts.append(f"\n{preferences_context}")

    prompt = "\n".join(prompt_parts)
    logger.info(f"Running klausur agent: {request.fach} {request.klasse} {request.thema}")

    last_error: Exception | None = None
    for attempt in range(1 + max_retries):
        try:
            result = await asyncio.wait_for(
                agent.run(prompt, deps=deps),
                timeout=timeout,
            )
            return result.output
        except asyncio.TimeoutError:
            logger.warning(f"Klausur agent timeout, Versuch {attempt + 1}")
            last_error = TimeoutError(f"Klausur-Agent hat nach {timeout}s nicht geantwortet")
        except Exception as e:
            if _is_retryable(e) and attempt < max_retries:
                logger.warning(f"Klausur agent error (retryable), Versuch {attempt + 1}: {e}")
                await asyncio.sleep(2 ** attempt)
                last_error = e
            else:
                raise
    raise last_error  # type: ignore[misc]


async def _generate_differenzierung(request: MaterialRequest) -> DifferenzierungStructure:
    """Run the differenzierung agent with timeout and retry."""
    settings = get_settings()
    timeout = settings.sub_agent_timeout_seconds
    max_retries = settings.sub_agent_max_retries

    agent = get_diff_agent()
    teacher_context = await build_block3_context(request.teacher_id)
    deps = DiffDeps(teacher_id=request.teacher_id, teacher_context=teacher_context)

    prompt_parts = [
        f"Erstelle differenziertes Material in 3 Niveaustufen (Basis/Mittel/Erweitert):",
        f"- Fach: {request.fach}",
        f"- Klasse/Jahrgang: {request.klasse}",
        f"- Thema: {request.thema}",
    ]
    if request.dauer_minuten:
        prompt_parts.append(f"- Zeitrahmen: {request.dauer_minuten} Minuten")
    if request.zusatz_anweisungen:
        prompt_parts.append(f"- Zusätzliche Anweisungen: {request.zusatz_anweisungen}")

    prompt = "\n".join(prompt_parts)
    logger.info(f"Running differenzierung agent: {request.fach} {request.klasse} {request.thema}")

    last_error: Exception | None = None
    for attempt in range(1 + max_retries):
        try:
            result = await asyncio.wait_for(
                agent.run(prompt, deps=deps),
                timeout=timeout,
            )
            return result.output
        except asyncio.TimeoutError:
            logger.warning(f"Differenzierung agent timeout, Versuch {attempt + 1}")
            last_error = TimeoutError(f"Differenzierung-Agent hat nach {timeout}s nicht geantwortet")
        except Exception as e:
            if _is_retryable(e) and attempt < max_retries:
                logger.warning(f"Differenzierung agent error (retryable), Versuch {attempt + 1}: {e}")
                await asyncio.sleep(2 ** attempt)
                last_error = e
            else:
                raise
    raise last_error  # type: ignore[misc]
