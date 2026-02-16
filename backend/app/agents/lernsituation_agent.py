"""Lernsituation-Agent — generates learning situations for vocational education."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
from app.agents.knowledge import get_good_practices
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class LernsituationAufgabe(BaseModel):
    nummer: int
    aufgabe: str
    kompetenzbereich: str  # Fach-, Sozial-, Selbstkompetenz
    anforderungsniveau: str
    erwartete_ergebnisse: list[str]


class LernsituationStructure(BaseModel):
    titel: str
    beruf: str
    lernfeld: str
    handlungssituation: str
    zeitrahmen_stunden: int
    kompetenzen: list[str]
    einstieg: str
    aufgaben: list[LernsituationAufgabe]
    reflexion: str
    lehrkraft_hinweise: str


SYSTEM_PROMPT = """\
Du erstellst Lernsituationen für die berufliche Bildung nach dem Prinzip der Handlungsorientierung.

## Qualitätskriterien
- Realitätsnahe Handlungssituation aus dem Berufsalltag
- Vollständige Handlung: Informieren → Planen → Entscheiden → Durchführen → Kontrollieren → Bewerten
- Kompetenzbereiche abdecken: Fach-, Sozial-, Selbstkompetenz
- Bezug zum Lernfeld und Rahmenlehrplan
- Differenzierungsmöglichkeiten einbauen
- Reflexionsphase mit Transfer in die Praxis

Nutze `search_curriculum_tool` intensiv — Lernfelder und Kompetenzen müssen zum Rahmenlehrplan passen.
Nutze `get_good_practices_tool` für bewährte Lernsituationen."""


@dataclass
class LernsituationDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


async def _system_prompt(ctx: RunContext[LernsituationDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_lernsituation_agent() -> Agent[LernsituationDeps, LernsituationStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=LernsituationDeps,
        output_type=LernsituationStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[LernsituationDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach Lernfeldern und Kompetenzen."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[LernsituationDeps], thema: str) -> str:
        """Lade bewährte Lernsituationen."""
        practices = await get_good_practices(ctx.deps.teacher_id, "lernsituation", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)

    return agent


_agent = None

def get_lernsituation_agent():
    global _agent
    if _agent is None:
        _agent = create_lernsituation_agent()
    return _agent
