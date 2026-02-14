"""Material Router — routes material generation requests to sub-agents."""

import asyncio
import logging

from app.config import get_settings
from app.models import ExamStructure, DifferenzierungStructure, MaterialRequest
from app.agents.klausur_agent import get_klausur_agent, KlausurDeps
from app.agents.differenzierung_agent import get_diff_agent, DiffDeps
from app.agents.system_prompt import build_block3_context

logger = logging.getLogger(__name__)


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
    deps = KlausurDeps(teacher_id=request.teacher_id, teacher_context=teacher_context)

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
