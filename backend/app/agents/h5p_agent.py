"""H5P Exercise Agent — generates interactive exercise content."""
import logging
from pydantic import BaseModel
from pydantic_ai import Agent
from app.agents.llm import get_haiku

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


H5P_SYSTEM_PROMPT = """\
Du bist ein erfahrener Pädagoge und Experte für die Erstellung von digitalen Lernmaterialien.
Erstelle ansprechende und didaktisch wertvolle Übungen für Schüler:innen.
Alle Inhalte auf Deutsch.
Altersgerecht für die angegebene Klassenstufe.

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


def _create_agent() -> Agent[None, ExerciseSet]:
    return Agent(
        get_haiku(),
        output_type=ExerciseSet,
        instructions=H5P_SYSTEM_PROMPT,
    )


async def run_h5p_agent(
    fach: str,
    klasse: str,
    thema: str,
    exercise_type: str = "auto",
    num_questions: int = 5,
) -> ExerciseSet:
    agent = _create_agent()
    prompt = (
        f"Erstelle ein Übungsset für {fach}, Klasse {klasse}, Thema: {thema}.\n"
        f"Anzahl Fragen: {num_questions}.\n"
        f"Übungstyp: {exercise_type}.\n"
    )
    if exercise_type == "auto":
        prompt += "Wähle den besten Übungstyp für dieses Thema.\n"
    
    logger.info(f"H5P Agent: {fach} {klasse} {thema} ({exercise_type})")
    result = await agent.run(prompt)
    return result.output