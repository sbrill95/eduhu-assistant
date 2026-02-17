"""Material-Learning-Agent — learns from download + iteration signals.

Two main functions:
1. run_download_learning(material_id) — called when teacher downloads DOCX
2. run_iteration_learning(...) — called after material iteration
"""

import logging
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

from app.agents.llm import get_haiku
from app.agents.knowledge import save_good_practice, save_preference
from app import db

logger = logging.getLogger(__name__)


async def run_download_learning(material_id: str) -> None:
    """Fire-and-forget: Teacher downloaded material → save as good practice."""
    try:
        record = await db.select(
            "generated_materials",
            columns="teacher_id,type,content_json",
            filters={"id": material_id},
            single=True,
        )
        if not record:
            logger.warning(f"Download learning: material {material_id} not found")
            return

        teacher_id = record.get("teacher_id", "")
        material_type = record.get("type", "unknown")
        content = record.get("content_json", {})

        if not teacher_id or not content:
            return

        fach = content.get("fach", "allgemein")
        thema = content.get("thema", content.get("fach_thema", ""))
        titel = content.get("titel", content.get("fach", ""))

        description = f"Heruntergeladenes Material: {titel} — {thema}"

        practice_content: dict[str, Any] = {
            "signal": "download",
            "material_type": material_type,
            "thema": thema,
        }

        if material_type == "klausur":
            aufgaben = content.get("aufgaben", [])
            afb_counts: dict[str, int] = {}
            for a in aufgaben:
                level = str(a.get("afb_level", "?"))
                afb_counts[level] = afb_counts.get(level, 0) + 1
            practice_content["afb_verteilung"] = afb_counts
            practice_content["anzahl_aufgaben"] = len(aufgaben)
            practice_content["gesamtpunkte"] = content.get("gesamtpunkte", 0)

        await save_good_practice(
            teacher_id=teacher_id,
            agent_type=material_type,
            fach=fach,
            description=description,
            content=practice_content,
            quality_score=0.7,
        )
        logger.info(f"Download learning saved for {material_id} ({material_type})")

    except Exception as e:
        logger.error(f"run_download_learning failed: {e}")


class DiffLearning(BaseModel):
    """Output of the diff-learning analysis."""
    changes: list[str] = []
    preferences: list[str] = []
    preference_keys: dict[str, Any] = {}


DIFF_PROMPT = """\
Du vergleichst zwei Versionen eines generierten Lehrmaterials.
Die Lehrkraft hat Version 1 erhalten und dann eine Änderung angefordert (Anweisung unten).
Version 2 ist das Ergebnis.

Deine Aufgabe:
1. Identifiziere die KONKRETEN Änderungen zwischen V1 und V2
2. Leite daraus PRÄFERENZEN der Lehrkraft ab

Beispiel:
- Anweisung: "leichter machen"
- Änderung: AFB III Aufgaben entfernt, mehr AFB I
- Präferenz: "Bevorzugt einfachere Aufgaben (AFB I-II Fokus)"
- preference_keys: {"afb_fokus": "I-II", "schwierigkeit": "leicht"}

Sei konkret und spezifisch. Keine allgemeinen Aussagen."""


async def run_iteration_learning(
    material_id: str,
    teacher_id: str,
    material_type: str,
    fach: str,
    old_structure: dict,
    new_structure: dict,
    anweisung: str,
) -> None:
    """Fire-and-forget: Teacher iterated on material → diff-learning."""
    try:
        agent = Agent(
            get_haiku(),
            output_type=DiffLearning,
            instructions=DIFF_PROMPT,
        )

        old_summary = _summarize_structure(old_structure, material_type)
        new_summary = _summarize_structure(new_structure, material_type)

        prompt = (
            f"Material-Typ: {material_type}\n"
            f"Fach: {fach}\n"
            f"Anweisung der Lehrkraft: {anweisung}\n\n"
            f"## Version 1 (vorher)\n{old_summary}\n\n"
            f"## Version 2 (nachher)\n{new_summary}"
        )

        result = await agent.run(prompt)
        learning = result.output

        logger.info(
            f"Diff learning: {len(learning.changes)} changes, "
            f"{len(learning.preferences)} preferences"
        )

        for i, pref_desc in enumerate(learning.preferences):
            await save_preference(
                teacher_id=teacher_id,
                agent_type=material_type,
                fach=fach,
                description=pref_desc,
                content=learning.preference_keys if i == 0 else {},
            )

        thema = new_structure.get("thema", new_structure.get("fach_thema", ""))
        await save_good_practice(
            teacher_id=teacher_id,
            agent_type=material_type,
            fach=fach,
            description=f"Iteriertes Material: {thema} (Anweisung: {anweisung[:80]})",
            content={
                "signal": "iteration",
                "anweisung": anweisung,
                "changes": learning.changes[:5],
            },
            quality_score=0.8,
        )

    except Exception as e:
        logger.error(f"run_iteration_learning failed: {e}")


def _summarize_structure(structure: dict, material_type: str) -> str:
    """Create a token-efficient summary for diff comparison."""
    if material_type == "klausur":
        aufgaben = structure.get("aufgaben", [])
        parts = [
            f"Titel: {structure.get('titel', '?')}, "
            f"Punkte: {structure.get('gesamtpunkte', '?')}"
        ]
        for i, a in enumerate(aufgaben, 1):
            parts.append(
                f"  {i}. {a.get('aufgabe', '?')} "
                f"(AFB {a.get('afb_level', '?')}, {a.get('punkte', '?')}P)"
            )
        return "\n".join(parts)

    elif material_type == "differenzierung":
        niveaus = structure.get("niveaus", [])
        parts = [f"Titel: {structure.get('titel', '?')}"]
        for n in niveaus:
            parts.append(
                f"  {n.get('niveau', '?')}: "
                f"{len(n.get('aufgaben', []))} Aufgaben, "
                f"{n.get('zeitaufwand_minuten', '?')} Min"
            )
        return "\n".join(parts)

    else:
        keys = ["titel", "thema", "fach_thema", "leitfrage", "kompetenzen"]
        parts = []
        for k in keys:
            if k in structure:
                val = structure[k]
                if isinstance(val, str):
                    parts.append(f"{k}: {val[:200]}")
                elif isinstance(val, list):
                    parts.append(f"{k}: {len(val)} items")
        return "\n".join(parts) if parts else str(structure)[:500]
