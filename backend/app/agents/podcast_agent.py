"""Podcast-Agent — generates podcast scripts and audio via ElevenLabs."""

import logging
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
from app.agents.knowledge import get_good_practices
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


@dataclass
class PodcastDeps:
    teacher_id: str
    fach: str = ""
    teacher_context: str = ""
    wissenskarte: str = ""


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

    return agent


_agent = None

def get_podcast_agent():
    global _agent
    if _agent is None:
        _agent = create_podcast_agent()
    return _agent
