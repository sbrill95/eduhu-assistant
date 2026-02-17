"""Hilfekarten-Agent — generates step-by-step help cards for students."""

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


class HilfekarteStructure(BaseModel):
    titel: str
    thema: str
    niveau: str  # Basis / Erweitert / Experte
    kerninhalt: str
    hilfestellungen: list[str]
    beispiele: list[str]
    tipps: list[str]
    weiterfuehrend: str | None = None


SYSTEM_PROMPT = """\
Du erstellst kompakte Hilfekarten für Schüler — eine Seite, klar strukturiert.

## Qualitätskriterien
- Schrittweise Hilfen: Vom Einfachen zum Komplexen
- Konkrete Beispiele mit Lösungsweg
- Merksätze / Eselsbrücken als Tipps
- Niveau klar kennzeichnen (Basis/Erweitert/Experte)
- Sprache altersgerecht und ermutigend
- Max. 5-7 Hilfestellungen, 2-3 Beispiele, 2-3 Tipps

Nutze `search_curriculum_tool` für Lehrplaninhalte und `get_good_practices_tool` für bewährte Formate."""


# Use BaseMaterialDeps directly
HilfekarteDeps = BaseMaterialDeps


async def _system_prompt(ctx: RunContext[HilfekarteDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_hilfekarten_agent() -> Agent[HilfekarteDeps, HilfekarteStructure]:
    agent = Agent(
        get_haiku(),
        deps_type=HilfekarteDeps,
        output_type=HilfekarteStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[HilfekarteDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[HilfekarteDeps], thema: str) -> str:
        """Lade bewährte Hilfekarten-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "hilfekarte", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[HilfekarteDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"hilfekarte agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[HilfekarteDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"hilfekarte agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="hilfekarte",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_hilfekarten_agent():
    global _agent
    if _agent is None:
        _agent = create_hilfekarten_agent()
    return _agent
