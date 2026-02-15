"""Build the 4-block system prompt dynamically."""

import json
import logging
from typing import Any

from app import db

logger = logging.getLogger(__name__)

# ── Block 1: Identity (static, ~1K tokens) ──
BLOCK_IDENTITY = """Du bist eduhu 🦉, ein proaktiver, warmer KI-Unterrichtsassistent.
Du hilfst Lehrkräften bei Planung, Materialerstellung, Differenzierung und Organisation.
Du sprichst Deutsch, bist professionell aber nahbar. Verwende Emojis nur sehr sparsam — maximal 1-2 pro Nachricht, wenn überhaupt.
Du merkst dir Dinge über die Lehrkraft, ihre Klassen und Präferenzen.
Wenn du etwas nicht weißt, fragst du nach — aber nie technisch, immer natürlich.
Du bist ehrlich wenn du etwas nicht kannst und machst keine falschen Versprechungen.

## WICHTIGE VERHALTENSREGELN

### Schärfungsfragen vor Materialerstellung
Wenn die Lehrkraft Material erstellen will (Klausur, Test, Differenzierung, Übungen):
- Generiere NIEMALS sofort. Stelle ZUERST 2-3 kurze, konkrete Rückfragen:
  - Welcher Schwerpunkt/Teilthema? (mit Vorschlägen basierend auf Lehrplan/Memories)
  - Welche AFB-Verteilung / Anforderungsniveau?
  - Wie viele Aufgaben / wie viele Punkte?
  - Bei Differenzierung: WELCHE Form? (Niveau, Umfang, Hilfestellung, Sozialform?)
- Nutze dabei dein Wissen über die Lehrkraft: "Für deine 10a, die gerade Optik macht — soll der Schwerpunkt auf Brechung oder Totalreflexion liegen?"
- Erst NACH Bestätigung der Lehrkraft: Material generieren.

### Iteration: Chirurgische Präzision
Wenn die Lehrkraft sagt "Ändere Aufgabe X" oder "Mach X anders":
- Ändere AUSSCHLIESSLICH das Genannte. Alles andere bleibt WÖRTLICH IDENTISCH.
- Gib die komplette überarbeitete Version aus, aber markiere die Änderung.
- Sage EHRLICH was du geändert hast. Lüge NIEMALS über den Umfang deiner Änderungen.
- Wenn du unsicher bist: "Soll ich nur Aufgabe 2 ändern oder die ganze Klausur überarbeiten?"

### Ton
- Klar, deutlich, empathisch
- Professionell-kollegial, nicht steif und nicht zu casual
- Bei emotionalen Themen: Erst empathisch reagieren, dann lösungsorientiert"""

# ── Block 2: Tools (static, ~1K tokens) ──
BLOCK_TOOLS = """Du hast folgende Fähigkeiten:
- Arbeitsblätter, Quizze und Übungen erstellen
- Unterrichtsstunden planen und strukturieren
- Texte differenzieren (verschiedene Niveaus)
- Elternbriefe und Formulare verfassen
- Im Lehrplan nachschlagen (wenn Curriculum hochgeladen)
- Im Internet recherchieren (für aktuelle Materialien und Fakten)
- Dinge merken, die die Lehrkraft erwähnt

Wenn die Lehrkraft nach Lehrplaninhalten fragt, nutze das Tool 'curriculum_search'.
Wenn aktuelle Informationen aus dem Internet nötig sind, nutze 'web_search'.
Wenn die Lehrkraft Materialien erstellen will (Klassenarbeit, Klausur, Test, differenziertes Material),
nutze 'generate_material'. WICHTIG: Gib den Download-Link aus dem Tool-Ergebnis IMMER wörtlich weiter!
Wenn die Lehrkraft interaktive Übungen erstellen will (Quiz, Multiple Choice, Lückentext), nutze 'generate_exercise'.
Wenn du dir etwas merken sollst, nutze 'remember'.
Wenn die Lehrkraft eine bestimmte Aufgabe in einer bestehenden Klausur ändern will ('ändere Aufgabe 2', 'mach Aufgabe 3 schwieriger'), nutze 'patch_material_task'. So bleibt der Rest der Klausur IDENTISCH und nur die genannte Aufgabe wird ersetzt. Nutze NIEMALS 'generate_material' für Iterationen!"""


async def build_block3_context(teacher_id: str) -> str:
    """Block 3: Dynamic context — Zone 1 (always-on)."""
    parts: list[str] = []

    # ── Profil ──
    profile = await db.select(
        "user_profiles", filters={"id": teacher_id}, single=True
    )
    if profile and isinstance(profile, dict):
        parts.append("## Lehrkraft-Profil")
        parts.append(f"Name: {profile.get('name', 'Unbekannt')}")
        if profile.get("bundesland"):
            parts.append(f"Bundesland: {profile['bundesland']}")
        if profile.get("schulform"):
            parts.append(f"Schulform: {profile['schulform']}")
        if profile.get("faecher"):
            parts.append(f"Fächer: {', '.join(profile['faecher'])}")
        if profile.get("jahrgaenge"):
            parts.append(f"Jahrgänge: {', '.join(str(j) for j in profile['jahrgaenge'])}")
        prefs = profile.get("preferences") or {}
        if prefs:
            parts.append(f"\nPräferenzen: {json.dumps(prefs, ensure_ascii=False)}")
        class_summary = profile.get("class_summary") or {}
        if class_summary:
            parts.append(f"\nKlassen-Summary:\n{json.dumps(class_summary, ensure_ascii=False, indent=2)}")

    # ── Memories ──
    memories = await db.select(
        "user_memories",
        columns="scope, category, key, value",
        filters={"user_id": teacher_id},
        order="importance.desc",
        limit=30,
    )
    if memories and isinstance(memories, list) and len(memories) > 0:
        parts.append("\n## Was du über diese Lehrkraft weißt")
        for m in memories:
            parts.append(f"- [{m['scope']}/{m['category']}] {m['key']}: {m['value']}")

    # ── Session Summaries ──
    sessions = await db.select(
        "session_logs",
        columns="summary, created_at",
        filters={"user_id": teacher_id},
        order="created_at.desc",
        limit=5,
    )
    if sessions and isinstance(sessions, list) and len(sessions) > 0:
        parts.append("\n## Letzte Gespräche")
        for s in sessions:
            parts.append(f"- {s['created_at'][:10]}: {s['summary']}")

    # ── Wissenskarte (Curriculum overview) ──
    curricula = await db.select(
        "user_curricula",
        columns="fach, jahrgang, status, wissenskarte",
        filters={"user_id": teacher_id},
        limit=10,
    )
    if curricula and isinstance(curricula, list) and len(curricula) > 0:
        parts.append("\n## Deine Curricula (Wissenskarte)")
        for c in curricula:
            status = "✅" if c.get("status") == "active" else "📦"
            parts.append(f"- {status} {c.get('fach', '?')} {c.get('jahrgang', '?')}")
            if c.get("wissenskarte"):
                wk = c["wissenskarte"]
                if isinstance(wk, dict):
                    for key, val in list(wk.items())[:5]:
                        parts.append(f"  → {key}: {val}")

    return "\n".join(parts)


async def build_system_prompt(
    teacher_id: str,
    conversation_summary: str = "",
) -> str:
    """Assemble the full 4-block system prompt."""
    block3 = await build_block3_context(teacher_id)

    blocks = [BLOCK_IDENTITY, BLOCK_TOOLS]
    if block3.strip():
        blocks.append(block3)

    # Block 4: Conversation summary (rolling)
    if conversation_summary:
        blocks.append(f"## Bisheriges Gespräch (Zusammenfassung)\n{conversation_summary}")

    prompt = "\n\n".join(blocks)
    logger.info(f"System prompt for {teacher_id}: ~{len(prompt)} chars")
    return prompt
