"""H5P Exercise Agent — generates interactive exercise content.

Uses Haiku for exercise generation with:
- Wissenskarte (knowledge summary in system prompt)
- Good Practice tool (RAG from agent_knowledge)
- Curriculum search tool
- Conversation context tool (2 depth levels)
- Teacher preferences tool
- Autonomous reasoning: Agent decides which tools to use
"""

import logging

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from app.agents.llm import get_haiku
from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool, register_ask_teacher_tool
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)


class ExerciseAnswer(BaseModel):
    text: str
    correct: bool
    feedback: str = ""


class ExerciseQuestion(BaseModel):
    question: str
    answers: list[ExerciseAnswer] = []
    correct: bool | None = None  # for truefalse


class ExerciseSet(BaseModel):
    title: str
    exercise_type: str  # "multichoice", "blanks", "truefalse", "dragtext"
    questions: list[ExerciseQuestion] = []  # for multichoice/truefalse
    text_with_gaps: str | None = None  # for blanks/dragtext


# Use BaseMaterialDeps directly
H5PDeps = BaseMaterialDeps


H5P_SYSTEM_PROMPT = """\
Du bist ein erfahrener Pädagoge und Experte für die Erstellung von digitalen Lernmaterialien.
Erstelle ansprechende und didaktisch wertvolle Übungen für Schüler:innen.
Alle Inhalte auf Deutsch. Altersgerecht für die angegebene Klassenstufe.

## Dein Workflow
1. Lies den Auftrag und die Wissenskarte
2. ENTSCHEIDE selbst was du brauchst:
   - Lehrplan relevant? → search_curriculum()
   - Bewährte Übungen vorhanden? → get_good_practices()
   - Lehrer-Kontext unklar? → get_conversation_context() (Chat nachlesen)
   - Lehrer-Präferenzen? → get_teacher_preferences()
3. Generiere die Übungen MIT dem geladenen Wissen

## Übungstypen
- "multichoice": Multiple-Choice-Fragen mit je 4 Antwortoptionen (1 richtig, 3 falsch).
  Jede Antwort braucht Feedback.
- "blanks": Lückentext — markiere Lücken mit *Antwort* Syntax.
  Beispiel: "Die Hauptstadt von Deutschland ist *Berlin*."
- "truefalse": Wahr/Falsch-Aussagen. Setze correct=true oder correct=false.
- "dragtext": Zuordnungstext — markiere Drag-Wörter mit *Wort* Syntax.

## Regeln
- Fragen klar und eindeutig formulieren
- Falsche Antworten plausibel machen (keine offensichtlich falschen)
- Feedback bei jeder Antwort: kurz erklären WARUM richtig/falsch
- Bei "auto": Wähle den didaktisch sinnvollsten Typ für das Thema
"""


async def _h5p_system_prompt(ctx: RunContext[H5PDeps]) -> str:
    prompt = H5P_SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext der Lehrkraft\n{ctx.deps.teacher_context}"
    return prompt


def _create_agent() -> Agent[H5PDeps, ExerciseSet]:
    agent = Agent(
        get_haiku(),
        deps_type=H5PDeps,
        output_type=ExerciseSet,
        instructions=_h5p_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[H5PDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten für die Übungen."""
        logger.info(f"H5P agent curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[H5PDeps], thema: str) -> str:
        """Lade bewährte Übungsbeispiele aus der Wissensdatenbank."""
        logger.info(f"H5P agent good practices: {thema}")
        practices = await get_good_practices(
            teacher_id=ctx.deps.teacher_id,
            agent_type="h5p",
            fach=ctx.deps.fach,
            thema=thema,
            limit=2,
        )
        if not practices:
            return "Keine bewährten Beispiele gefunden."
        parts = []
        for p in practices:
            desc = p.get("description", "")
            score = p.get("quality_score", 0)
            parts.append(f"- {desc} (Qualität: {score:.1f})")
        return "\n".join(parts)

    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[H5PDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)"""
        logger.info(f"H5P agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[H5PDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft."""
        logger.info(f"H5P agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="h5p",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen."
        parts = [f"- {p.get('description', '')}" for p in prefs if p.get("description")]
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    register_ask_teacher_tool(agent)

    return agent


_h5p_agent: Agent[H5PDeps, ExerciseSet] | None = None


def get_h5p_agent() -> Agent[H5PDeps, ExerciseSet]:
    global _h5p_agent
    if _h5p_agent is None:
        _h5p_agent = _create_agent()
    return _h5p_agent


async def run_h5p_agent(
    fach: str,
    klasse: str,
    thema: str,
    exercise_type: str = "auto",
    num_questions: int = 5,
    teacher_id: str = "",
    conversation_id: str = "",
    teacher_context: str = "",
    wissenskarte: str = "",
) -> ExerciseSet:
    """Compatibility wrapper — runs the H5P agent with deps."""
    agent = get_h5p_agent()
    deps = H5PDeps(
        teacher_id=teacher_id,
        conversation_id=conversation_id,
        fach=fach,
        wissenskarte=wissenskarte,
        teacher_context=teacher_context,
    )
    prompt = (
        f"Erstelle ein Übungsset für {fach}, Klasse {klasse}, Thema: {thema}.\n"
        f"Anzahl Fragen: {num_questions}.\n"
        f"Übungstyp: {exercise_type}.\n"
    )
    if exercise_type == "auto":
        prompt += "Wähle den besten Übungstyp für dieses Thema.\n"
    
    logger.info(f"H5P Agent: {fach} {klasse} {thema} ({exercise_type})")
    result = await agent.run(prompt, deps=deps)
    return result.output
