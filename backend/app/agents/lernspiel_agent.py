"""Lernspiel-Agent — generates creative learning games."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_haiku
from app.agents.knowledge import get_good_practices
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class LernspielStructure(BaseModel):
    titel: str
    thema: str
    zielgruppe: str
    dauer_minuten: int
    spielname: str
    regeln: str
    inhalt: str
    materialien: list[str]
    varianten: list[str]
    kompetenzen: list[str]


SYSTEM_PROMPT = """\
Du entwirfst kreative Lernspiele, die Spaß machen und gleichzeitig Lernziele erreichen.

## Qualitätskriterien
- Klarer Spielname und einfache Regeln
- Altersgerecht und motivierend
- Fachlicher Inhalt ist spieltragend, nicht aufgesetzt
- Materialien realistisch (im Klassenzimmer verfügbar)
- Mindestens 2 Varianten für Differenzierung
- Kompetenzorientiert (was lernen die Schüler?)
- Zeitrahmen realistisch

Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


@dataclass
class LernspielDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


async def _system_prompt(ctx: RunContext[LernspielDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_lernspiel_agent() -> Agent[LernspielDeps, LernspielStructure]:
    agent = Agent(
        get_haiku(),
        deps_type=LernspielDeps,
        output_type=LernspielStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[LernspielDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[LernspielDeps], thema: str) -> str:
        """Lade bewährte Lernspiel-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "lernspiel", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)

    return agent


_agent = None

def get_lernspiel_agent():
    global _agent
    if _agent is None:
        _agent = create_lernspiel_agent()
    return _agent
