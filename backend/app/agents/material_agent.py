"""Material Coordinator Agent — routes material generation requests."""

import logging
import os
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModel

from app.config import get_settings
from app.models import ExamStructure, MaterialRequest
from app.agents.klausur_agent import get_klausur_agent, KlausurDeps
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)

MATERIAL_SYSTEM_PROMPT = """\
Du bist ein Material-Koordinator für Lehrkräfte. Du hilfst bei der Erstellung von Unterrichtsmaterialien.

Wenn eine Klausur/Klassenarbeit angefragt wird, nutze das Tool `generate_klausur`.
Wenn du Lehrplaninformationen brauchst, nutze `search_curriculum`.

Antworte immer auf Deutsch.
"""


@dataclass
class MaterialDeps:
    teacher_id: str
    request: MaterialRequest


async def run_material_agent(request: MaterialRequest) -> ExamStructure:
    """Run the material agent for a given request. Currently supports klausur only."""
    if request.type == "klausur":
        return await _generate_klausur(request)
    else:
        raise ValueError(f"Material-Typ '{request.type}' wird noch nicht unterstützt.")


async def _generate_klausur(request: MaterialRequest) -> ExamStructure:
    """Directly run the klausur agent with the request details."""
    agent = get_klausur_agent()
    deps = KlausurDeps(teacher_id=request.teacher_id)

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

    result = await agent.run(prompt, deps=deps)
    return result.output
