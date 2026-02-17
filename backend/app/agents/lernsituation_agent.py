"""Lernsituation-Agent — generates learning situations for vocational education."""

import logging
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool, register_ask_teacher_tool

from app.agents.llm import get_sonnet
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)
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


# Use BaseMaterialDeps directly
LernsituationDeps = BaseMaterialDeps


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


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[LernsituationDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"lernsituation agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[LernsituationDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"lernsituation agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="lernsituation",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_lernsituation_agent():
    global _agent
    if _agent is None:
        _agent = create_lernsituation_agent()
    return _agent
