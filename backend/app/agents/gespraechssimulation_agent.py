"""Gesprächssimulations-Agent — generates conversation scripts for vocational training."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
from app.agents.knowledge import get_good_practices
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class GespraechsRolle(BaseModel):
    name: str  # "Patient Müller", "Kundin Schmidt"
    beschreibung: str
    stimme: str  # "male", "female", "educator"
    verhalten: str  # Wie verhält sich die Person?
    ziel: str  # Was will die Person erreichen?


class GespraechsAbschnitt(BaseModel):
    nummer: int
    sprecher: str
    text: str
    regieanweisung: str | None = None
    verzweigung: str | None = None  # Alternative Reaktion bei anderer Antwort


class GespraechssimulationStructure(BaseModel):
    titel: str
    thema: str
    szenario: str  # Beschreibung der Gesprächssituation
    lernziel: str
    rollen: list[GespraechsRolle]
    ablauf: list[GespraechsAbschnitt]
    feedback_kriterien: list[str]  # Worauf sollen Schüler achten?
    lehrkraft_hinweise: str


SYSTEM_PROMPT = """\
Du entwirfst Gesprächssimulationen für die berufliche Bildung — realitätsnah und lernzielorientiert.

## Qualitätskriterien
- Realitätsnahes Szenario aus dem Berufsalltag
- Klare Rollenbeschreibungen mit Motivation/Ziel
- Natürlicher Gesprächsverlauf (nicht roboterhaft)
- Mögliche Verzweigungen (Was wenn der Schüler anders reagiert?)
- Feedback-Kriterien zur Auswertung
- Typische Szenarien: Arzt-Patient, Verkäufer-Kunde, Pfleger-Angehörige, Berater-Klient

Verfügbare Stimmen: male, female, educator, storyteller.
Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


@dataclass
class GespraechssimulationDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


async def _system_prompt(ctx: RunContext[GespraechssimulationDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_gespraechssimulation_agent() -> Agent[GespraechssimulationDeps, GespraechssimulationStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=GespraechssimulationDeps,
        output_type=GespraechssimulationStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[GespraechssimulationDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[GespraechssimulationDeps], thema: str) -> str:
        """Lade bewährte Gesprächssimulationen."""
        practices = await get_good_practices(ctx.deps.teacher_id, "gespraechssimulation", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)

    return agent


_agent = None

def get_gespraechssimulation_agent():
    global _agent
    if _agent is None:
        _agent = create_gespraechssimulation_agent()
    return _agent
