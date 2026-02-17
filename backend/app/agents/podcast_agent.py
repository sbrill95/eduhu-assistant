"""Podcast-Agent — generates podcast scripts and audio via ElevenLabs."""

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


class PodcastSegment(BaseModel):
    sprecher: str  # "Moderator", "Experte", etc.
    stimme: str  # "male", "female", "educator", "storyteller"
    text: str
    regieanweisung: str | None = None  # "(nachdenklich)", "(begeistert)"


class PodcastStructure(BaseModel):
    titel: str
    thema: str
    format: str  # Monolog, Dialog, Interview, Diskussion
    dauer_minuten: int
    intro: str
    segmente: list[PodcastSegment]
    outro: str
    didaktischer_rahmen: str


SYSTEM_PROMPT = """\
Du erstellst Podcast-Skripte für didaktische Zwecke — klar strukturiert, mehrsprecherfähig.

## Qualitätskriterien
- Klarer roter Faden mit didaktischem Ziel
- Dialogische Struktur (mind. 2 Sprecher bei Dialog/Interview)
- Natürliche Sprache — klingt wie ein echter Podcast, nicht wie ein Vortrag
- Intro + Segmente + Outro
- Regieanweisungen für Emotionen/Pausen
- Zusammenfassungen/Kernbotschaften einbauen
- Dauer realistisch: ~150 Wörter pro Minute gesprochener Text

Verfügbare Stimmen: male, female, educator, storyteller.
Nutze `search_curriculum_tool` und `get_good_practices_tool`."""


# Use BaseMaterialDeps directly
PodcastDeps = BaseMaterialDeps


async def _system_prompt(ctx: RunContext[PodcastDeps]) -> str:
    prompt = SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext\n{ctx.deps.teacher_context}"
    return prompt


def create_podcast_agent() -> Agent[PodcastDeps, PodcastStructure]:
    agent = Agent(
        get_sonnet(),
        deps_type=PodcastDeps,
        output_type=PodcastStructure,
        instructions=_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[PodcastDeps], query: str) -> str:
        """Durchsuche den Lehrplan."""
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[PodcastDeps], thema: str) -> str:
        """Lade bewährte Podcast-Beispiele."""
        practices = await get_good_practices(ctx.deps.teacher_id, "podcast", ctx.deps.fach, thema, 2)
        if not practices:
            return "Keine Beispiele gefunden."
        return "\n".join(f"- {p.get('description', '')}" for p in practices)


    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[PodcastDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"podcast agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[PodcastDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"podcast agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="podcast",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_agent = None

def get_podcast_agent():
    global _agent
    if _agent is None:
        _agent = create_podcast_agent()
    return _agent
