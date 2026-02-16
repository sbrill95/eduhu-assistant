"""Escape-Room-Agent — generates chained puzzle rooms for education."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
from app.agents.knowledge import get_good_practices
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class EscapeRoomRaetsel(BaseModel):
    nummer: int
    titel: str
    beschreibung: str
    hinweis: str
    loesung: str
    uebergang: str  # Wie führt die Lösung zum nächsten Rätsel?
    material: str | None = None


class EscapeRoomStructure(BaseModel):
    titel: str
    thema: str
    zeitrahmen_minuten: int
    schwierigkeitsgrad: str
    einfuehrung: str  # Story/Narrative
    raetsel: list[EscapeRoomRaetsel]
    abschluss: str
    lehrkraft_hinweise: str


SYSTEM_PROMPT = """\
Du entwirfst Escape-Room-Rätsel für den Unterricht — aufeinander aufbauend, mit einer Rahmengeschichte.

## Qualitätskriterien
- Spannende Rahmengeschichte als roter Faden
- 4-6 Rätsel, aufeinander aufbauend (Lösung von Rätsel N führt zu Rätsel N+1)
- Mischung aus Wissens-, Logik- und Kreativrätseln
- Jedes Rätsel hat einen Hinweis für Gruppen die nicht weiterkommen
- Realistischer Zeitrahmen (Rätsel à 5-10 Min)
- Fachlicher Inhalt ist Kern, nicht Gimmick
- Analog oder digital umsetzbar

Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


@dataclass
class EscapeRoomDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


async def _system_prompt(ctx: RunContext[EscapeRoomDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_escape_room_agent() -> Agent[EscapeRoomDeps, EscapeRoomStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=EscapeRoomDeps,
        output_type=EscapeRoomStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[EscapeRoomDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[EscapeRoomDeps], thema: str) -> str:
        """Lade bewährte Escape-Room-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "escape_room", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)

    return agent


_agent = None

def get_escape_room_agent():
    global _agent
    if _agent is None:
        _agent = create_escape_room_agent()
    return _agent
