"""Versuchsanleitung-Agent — generates experiment worksheets."""

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


class VersuchsanleitungStructure(BaseModel):
    titel: str
    thema: str
    offenheitsgrad: str  # Geschlossen / Gelenkt / Offen
    zeitrahmen_minuten: int
    materialien: list[str]
    sicherheitshinweise: list[str]
    theoretischer_hintergrund: str
    hypothese: str | None = None
    durchfuehrung: list[str]  # Numbered steps
    beobachtung: str
    auswertung: str
    lehrkraft_hinweise: str


SYSTEM_PROMPT = """\
Du erstellst Versuchsanleitungen / Arbeitsblätter für naturwissenschaftliche Experimente.

## Qualitätskriterien
- Sicherheitshinweise IMMER an erster Stelle
- Offenheitsgrad klar umsetzen:
  - Geschlossen: Detaillierte Schritt-für-Schritt-Anleitung
  - Gelenkt: Leitfragen führen durch den Versuch
  - Offen: Nur Fragestellung, Schüler planen selbst
- Materialien realistisch und verfügbar
- Durchführung als nummerierte Schritte
- Wissenschaftliche Methodik: Hypothese → Versuch → Beobachtung → Auswertung
- Altersgerechte Sprache

Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


# Use BaseMaterialDeps directly
VersuchsanleitungDeps = BaseMaterialDeps


async def _system_prompt(ctx: RunContext[VersuchsanleitungDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_versuchsanleitung_agent() -> Agent[VersuchsanleitungDeps, VersuchsanleitungStructure]:
    agent = Agent(
        get_haiku(),
        deps_type=VersuchsanleitungDeps,
        output_type=VersuchsanleitungStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[VersuchsanleitungDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[VersuchsanleitungDeps], thema: str) -> str:
        """Lade bewährte Versuchsanleitungen."""
        practices = await get_good_practices(ctx.deps.teacher_id, "versuchsanleitung", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[VersuchsanleitungDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"versuchsanleitung agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[VersuchsanleitungDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"versuchsanleitung agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="versuchsanleitung",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_versuchsanleitung_agent():
    global _agent
    if _agent is None:
        _agent = create_versuchsanleitung_agent()
    return _agent
