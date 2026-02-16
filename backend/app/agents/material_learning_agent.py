"""Material-Learning-Agent — learns from user interactions with materials.

Analyzes chat messages for implicit feedback signals and stores them
in agent_knowledge (preferences + good practices).
"""

import logging
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Optional
from app.agents.llm import get_haiku
from app.agents.knowledge import save_preference, save_good_practice, update_quality_score

logger = logging.getLogger(__name__)


class MaterialLearning(BaseModel):
    """What the agent extracted from the conversation."""
    has_material_interaction: bool = False
    material_id: Optional[str] = None
    signal_type: Optional[str] = None  # "positive", "negative", "iteration", "download", "continued"
    preferences_update: Optional[dict] = None
    preference_description: Optional[str] = None  # Human-readable summary
    should_save_template: bool = False
    rating: Optional[int] = None  # 1-5
    fach: Optional[str] = None
    material_type: Optional[str] = None  # "klausur", "differenzierung", etc.


LEARNING_PROMPT = """\
Du analysierst Chat-Nachrichten zwischen einer Lehrkraft und einem KI-Assistenten.
Deine Aufgabe: Erkenne Signale über Material-Qualität und Lehrer-Präferenzen.

## Signale erkennen:
- Positives Feedback: "gut", "perfekt", "genau so", "passt", "super" → signal_type="positive", rating=4-5
- Negatives Feedback: "zu schwer", "zu leicht", "zu vage", "nicht gut" → signal_type="negative", rating=1-2
- Iteration: Lehrer hat Aufgabe ändern lassen → signal_type="iteration", rating=3
- Weiterarbeit: Lehrer stellt Folgefragen zum Material → signal_type="continued", rating=3
- Download: Lehrer hat Material heruntergeladen → signal_type="download", rating=4
- Keine Material-Interaktion: has_material_interaction=false

## Präferenzen extrahieren (wenn erkennbar):
Extrahiere als preferences_update dict UND als preference_description (kurzer deutscher Satz).
Beispiele:
- "Ich hätte gerne 5 Aufgaben" → {"aufgaben_anzahl": 5}, "Bevorzugt 5 Aufgaben pro Klausur"
- "Weniger AFB III" → {"afb_max_iii_prozent": 25}, "Weniger AFB III gewünscht"
- "Immer mit Bonusaufgabe" → {"bonusaufgabe": true}, "Wünscht immer eine Bonusaufgabe"
- "Kürzere Aufgaben" → {"aufgaben_laenge": "kurz"}, "Bevorzugt kürzere Aufgabenstellungen"

## Fach und Material-Typ erkennen:
Extrahiere wenn möglich das Fach (z.B. "physik", "deutsch") und den Material-Typ (z.B. "klausur", "differenzierung").

## should_save_template:
Setze auf true wenn Rating >= 4 oder Lehrer explizit positiv reagiert."""


async def run_material_learning(
    teacher_id: str,
    conversation_id: str,
    messages: list[dict],
) -> None:
    """Fire-and-forget: Analyze conversation for material learning signals."""
    try:
        recent = messages[-6:] if len(messages) > 6 else messages
        conversation_text = "\n".join(
            f"{m.get('role', '?')}: {m.get('content', '')[:500]}"
            for m in recent
        )

        agent = Agent(
            get_haiku(),
            output_type=MaterialLearning,
            instructions=LEARNING_PROMPT,
        )

        result = await agent.run(
            f"Analysiere diese Konversation:\n\n{conversation_text}"
        )
        learning = result.output

        if not learning.has_material_interaction:
            return

        logger.info(
            f"Material learning: signal={learning.signal_type}, "
            f"rating={learning.rating}, fach={learning.fach}, "
            f"type={learning.material_type}, prefs={learning.preferences_update}"
        )

        agent_type = learning.material_type or "klausur"
        fach = learning.fach or "allgemein"

        # Save preferences if detected
        if learning.preferences_update and learning.preference_description:
            await save_preference(
                teacher_id=teacher_id,
                agent_type=agent_type,
                fach=fach,
                description=learning.preference_description,
                content=learning.preferences_update,
            )

        # Save as good practice if positively rated
        if learning.should_save_template and learning.rating and learning.rating >= 4:
            await save_good_practice(
                teacher_id=teacher_id,
                agent_type=agent_type,
                fach=fach,
                description=f"Positiv bewertetes Material (Rating {learning.rating}/5)",
                content={"signal": learning.signal_type, "rating": learning.rating},
                quality_score=learning.rating / 5.0,
            )

        # Update quality score for negative feedback
        if learning.signal_type == "negative" and learning.material_id:
            await update_quality_score(learning.material_id, -0.2)

    except Exception as e:
        logger.error(f"Material learning agent failed: {e}")
