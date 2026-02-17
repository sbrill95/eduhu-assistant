"""Lernspiel-Agent — generates creative learning games."""

import logging
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool, register_ask_teacher_tool

from app.agents.llm import get_haiku
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)
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


# Use BaseMaterialDeps directly
LernspielDeps = BaseMaterialDeps


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


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[LernspielDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"lernspiel agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[LernspielDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"lernspiel agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="lernspiel",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_lernspiel_agent():
    global _agent
    if _agent is None:
        _agent = create_lernspiel_agent()
    return _agent
