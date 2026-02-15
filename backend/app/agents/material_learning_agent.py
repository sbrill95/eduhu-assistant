"""Material-Learning-Agent — learns from user interactions with materials."""

import logging
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional
from app.agents.llm import get_haiku
from app import db

logger = logging.getLogger(__name__)


class MaterialLearning(BaseModel):
    """What the agent extracted from the conversation."""
    has_material_interaction: bool = False
    material_id: Optional[str] = None
    signal_type: Optional[str] = None  # "positive", "negative", "iteration", "download", "continued"
    preferences_update: Optional[dict] = None
    should_save_template: bool = False
    rating: Optional[int] = None  # 1-5


LEARNING_PROMPT = """\
Du analysierst Chat-Nachrichten zwischen einer Lehrkraft und einem KI-Assistenten.
Deine Aufgabe: Erkenne Signale über Material-Qualität und Lehrer-Präferenzen.

## Signale erkennen:
- Positives Feedback: "gut", "perfekt", "genau so", "passt", "super" → signal_type="positive", rating=4-5
- Negatives Feedback: "zu schwer", "zu leicht", "zu vage", "nicht gut" → signal_type="negative", rating=1-2
- Iteration: Lehrer hat Aufgabe ändern lassen → signal_type="iteration", rating=3
- Weiterarbeit: Lehrer stellt Folgefragen zum Material → signal_type="continued", rating=3
- Keine Material-Interaktion: has_material_interaction=false

## Präferenzen extrahieren (wenn erkennbar):
- Aufgabenanzahl: "Ich hätte gerne 5 Aufgaben" → {"aufgaben_anzahl": 5}
- AFB-Verteilung: "Weniger AFB III" → {"afb_max_iii_prozent": 25}
- AFB-Verteilung: "Mehr Reproduktion" → {"afb_min_i_prozent": 40}
- Bonusaufgabe: "Immer mit Bonusaufgabe" → {"bonusaufgabe": true}
- Notenschlüssel: "Ab 90% eine 1" → {"notenschluessel_anpassung": "1 ab 90%"}
- Teilaufgaben: "Lieber mit Teilaufgaben" → {"teilaufgaben": true}
- Format: "Kürzere Aufgaben" → {"aufgaben_laenge": "kurz"}

## Material-ID erkennen:
Wenn eine material_id in der Konversation erwähnt wird (z.B. in Download-Links oder Tool-Ergebnissen), gib sie als material_id zurück.

## should_save_template:
Setze auf true wenn:
- Rating >= 4 (positives Feedback)
- Lehrer hat Material iteriert UND danach positiv reagiert
- Lehrer sagt explizit "Das ist ein gutes Muster" o.ä.

Wenn keine Material-Interaktion erkennbar ist, gib has_material_interaction=false zurück."""


async def run_material_learning(
    teacher_id: str,
    conversation_id: str,
    messages: list[dict],
) -> None:
    """Fire-and-forget: Analyze conversation for material learning signals."""
    try:
        # Only analyze last 6 messages for efficiency
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

        logger.info(f"Material learning: signal={learning.signal_type}, rating={learning.rating}, prefs={learning.preferences_update}")

        # Update preferences if detected
        if learning.preferences_update:
            await _update_preferences(teacher_id, learning.preferences_update)

        # Save template if material was rated highly
        if learning.should_save_template and learning.material_id:
            await _save_as_template(teacher_id, learning.material_id, learning.rating or 3)

    except Exception as e:
        logger.error(f"Material learning agent failed: {e}")


async def _update_preferences(teacher_id: str, prefs_update: dict) -> None:
    """Merge new preferences with existing ones."""
    try:
        existing = await db.select(
            "material_preferences",
            filters={"teacher_id": teacher_id},
            single=True,
        )

        if existing:
            current_prefs = existing.get("preferences", {})
            current_prefs.update(prefs_update)
            await db.update(
                "material_preferences",
                {"preferences": current_prefs},
                filters={"id": existing["id"]},
            )
        else:
            await db.insert(
                "material_preferences",
                {
                    "teacher_id": teacher_id,
                    "material_type": "klausur",
                    "preferences": prefs_update,
                },
            )
        logger.info(f"Updated preferences for {teacher_id}: {prefs_update}")
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")


async def _save_as_template(teacher_id: str, material_id: str, rating: int) -> None:
    """Save a generated material as a personal template."""
    try:
        material = await db.select(
            "generated_materials",
            columns="content_json, type",
            filters={"id": material_id},
            single=True,
        )
        if not material:
            return

        content = material["content_json"]
        await db.insert(
            "material_templates",
            {
                "teacher_id": teacher_id,
                "material_type": material.get("type", "klausur"),
                "fach": content.get("fach", ""),
                "klassenstufe": content.get("klasse", ""),
                "thema": content.get("thema", ""),
                "content_json": content,
                "rating": rating,
                "source": "iterated",
            },
        )
        logger.info(f"Saved template from material {material_id} with rating {rating}")
    except Exception as e:
        logger.error(f"Failed to save template: {e}")
