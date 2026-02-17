"""Klausur-Agent — generates structured exams with AFB I-III tasks.

Uses Sonnet for complex exam generation with:
- Wissenskarte (knowledge summary in system prompt)
- Good Practice tool (RAG from agent_knowledge)
- Curriculum search tool
- Conversation context tool (2 depth levels)
- Teacher preferences tool
- Autonomous reasoning: Agent decides which tools to use
- Structured output for iterability (each Aufgabe separately editable)
"""

import logging

from pydantic_ai import Agent, RunContext

from app.agents.llm import get_sonnet
from app.agents.base import BaseMaterialDeps, register_ask_teacher_tool
from app.agents.knowledge import (
    get_good_practices,
    get_conversation_context,
    get_teacher_preferences,
)
from app.models import ExamStructure
from app.agents.curriculum_agent import curriculum_search

logger = logging.getLogger(__name__)

KLAUSUR_SYSTEM_PROMPT = """\
Du bist ein Experte für Klassenarbeiten und Klausuren im deutschen Schulsystem.

## Dein Workflow
1. Lies den Auftrag und die Wissenskarte
2. ENTSCHEIDE selbst was du brauchst:
   - Lehrplan relevant? → search_curriculum()
   - Bewährte Aufgaben vorhanden? → get_good_practices()
   - Lehrer-Kontext unklar? → get_conversation_context() (Chat nachlesen)
   - Lehrer-Präferenzen? → get_teacher_preferences()
3. NUR wenn kritische Info fehlt UND nicht ableitbar → Rückfrage (siehe unten)
4. Generiere die Klausur MIT dem geladenen Wissen

## DIREKT GENERIEREN — das ist der Standard!

Du hast IMMER Fach, Klasse, Thema. Das reicht. GENERIERE SOFORT.

Nutze sinnvolle Defaults für alles was nicht angegeben ist:
- Dauer: 45 Min (Klasse 5-10) oder 90 Min (Klasse 11-13)
- Aufgabenanzahl: 5-6
- AFB-Verteilung: 30/40/30
- Format: Mischung aus offenen und geschlossenen Aufgaben

## Rückfragen — FAST NIE nötig!

Stelle eine Rückfrage (ask_teacher) NUR wenn:
- Ein echter WIDERSPRUCH vorliegt (z.B. "45 Min aber 10 komplexe Aufgaben")
- Mehrere GLEICHWERTIGE Themen-Schwerpunkte möglich sind UND der Lehrer explizit mehrere genannt hat

KEINE Rückfrage bei:
- Fehlender Dauer → nutze Default
- Fehlender AFB-Verteilung → nutze 30/40/30
- Fehlender Aufgabenanzahl → nutze 5-6
- Stil-Fragen, Format-Fragen → entscheide selbst
- "Soll ich X oder Y?" → entscheide selbst, der Lehrer kann danach iterieren

Wenn du Rückfragen stellst, nutze options für Multiple-Choice:
ask_teacher("Welcher Schwerpunkt?", options=["Optik", "Mechanik", "Beides gleichwertig", "Andere Angabe"])

## Was du ZWINGEND brauchst (ohne das NICHT generieren):
- Fach + Thema (muss im Auftrag stehen)
- Klassenstufe (muss im Auftrag oder Profil stehen)
Alles andere: nutze Tools, nutze Defaults, entscheide selbst.

## AFB-Zuordnung (KRITISCH!)

### AFB I (Reproduktion) — ca. 30% der Punkte
Operatoren: Nennen, Angeben, Beschreiben, Wiedergeben, Definieren, Darstellen, Aufzählen
→ Wissen abrufen und wiedergeben. KEIN Erklären!

### AFB II (Reorganisation/Transfer) — ca. 40% der Punkte
Operatoren: Erklären, Erläutern, Vergleichen, Anwenden, Berechnen, Analysieren, Einordnen
→ Gelerntes auf neue Situationen anwenden. "Erklären" = AFB II, NICHT III!

### AFB III (Reflexion/Problemlösung) — ca. 30% der Punkte
Operatoren: Beurteilen, Bewerten, Stellung nehmen, Diskutieren, Entwickeln, Entwerfen
→ Eigenständig urteilen, kreativ Lösungen entwickeln.

## Regeln
- AFB-Verteilung: 30% I / 40% II / 30% III (max 35% III)
- Zeitbudget: Klasse 5-10 ca. 1P/Min, Klasse 11-13 ca. 1.2P/Min
- Mind. 4 Aufgaben, besser 5-6 (Teilaufgaben a/b/c zählen)
- Jede Aufgabe: konkrete Angaben, Zahlenwerte bei Berechnungen
- Erwartungshorizont: mind. 3-4 Stichpunkte pro Teilaufgabe
- Aufgaben aufsteigend nach Schwierigkeit (AFB I → II → III)
- Notenschlüssel: Standard (1 ab 87%, 2 ab 73%, 3 ab 59%, 4 ab 45%, 5 ab 20%)

PRÜFE VOR AUSGABE: AFB-Verteilung korrekt? Aufgaben konkret? Zeitbudget passend?"""


# Use BaseMaterialDeps directly — no klausur-specific fields needed
KlausurDeps = BaseMaterialDeps


async def _klausur_system_prompt(ctx: RunContext[KlausurDeps]) -> str:
    prompt = KLAUSUR_SYSTEM_PROMPT
    if ctx.deps.wissenskarte:
        prompt += f"\n\n{ctx.deps.wissenskarte}"
    if ctx.deps.teacher_context:
        prompt += f"\n\n## Kontext der Lehrkraft\n{ctx.deps.teacher_context}"
    return prompt


def create_klausur_agent() -> Agent[KlausurDeps, ExamStructure]:
    model = get_sonnet()

    agent = Agent(
        model,
        deps_type=KlausurDeps,
        output_type=ExamStructure,
        instructions=_klausur_system_prompt,
    )

    @agent.tool
    async def search_curriculum_tool(ctx: RunContext[KlausurDeps], query: str) -> str:
        """Durchsuche den Lehrplan nach relevanten Inhalten für die Klausur.
        Nutze dieses Tool um sicherzustellen, dass die Aufgaben lehrplankonform sind."""
        logger.info(f"Klausur agent curriculum search: {query}")
        return await curriculum_search(ctx.deps.teacher_id, query)

    @agent.tool
    async def get_good_practices_tool(ctx: RunContext[KlausurDeps], thema: str) -> str:
        """Lade bewährte Klausur-Beispiele aus der Wissensdatenbank.
        Nutze dieses Tool um Inspiration für Aufgabenformate und -qualität zu bekommen."""
        logger.info(f"Klausur agent good practices: {thema}")
        practices = await get_good_practices(
            teacher_id=ctx.deps.teacher_id,
            agent_type="klausur",
            fach=ctx.deps.fach,
            thema=thema,
            limit=3,
        )
        if not practices:
            return "Keine bewährten Beispiele gefunden."
        
        parts = []
        for p in practices:
            desc = p.get("description", "")
            content = p.get("content", {})
            score = p.get("quality_score", 0)
            parts.append(f"### {desc} (Qualität: {score:.1f})\n{_format_content(content)}")
        return "\n\n".join(parts)

    @agent.tool
    async def get_conversation_context_tool(
        ctx: RunContext[KlausurDeps], depth: str = "summary"
    ) -> str:
        """Lies den bisherigen Chat-Verlauf nach.
        depth='summary': Kompakte Übersicht (~100-200 Tokens)
        depth='full': Letzte 10 Nachrichten (~500-1000 Tokens)
        Nutze 'summary' zuerst. Nur 'full' wenn du mehr Details brauchst."""
        logger.info(f"Klausur agent conversation context: depth={depth}")
        return await get_conversation_context(ctx.deps.conversation_id, depth=depth)

    @agent.tool
    async def get_teacher_preferences_tool(ctx: RunContext[KlausurDeps]) -> str:
        """Lade explizite Präferenzen dieser Lehrkraft für Klausuren.
        Gibt zurück: Bevorzugte Aufgabenanzahl, Stil, Format etc."""
        logger.info(f"Klausur agent teacher preferences")
        prefs = await get_teacher_preferences(
            teacher_id=ctx.deps.teacher_id,
            agent_type="klausur",
            fach=ctx.deps.fach,
        )
        if not prefs:
            return "Keine gespeicherten Präferenzen für diese Lehrkraft."
        
        parts = []
        for p in prefs:
            desc = p.get("description", "")
            if desc:
                parts.append(f"- {desc}")
        return "Lehrkraft-Präferenzen:\n" + "\n".join(parts) if parts else "Keine Präferenzen."

    # Register ask_teacher tool for clarification
    register_ask_teacher_tool(agent)

    return agent


def _format_content(content: dict) -> str:
    """Format JSONB content to readable text for the agent."""
    if not content:
        return ""
    parts = []
    for key, val in content.items():
        if isinstance(val, list):
            parts.append(f"{key}: {', '.join(str(v) for v in val[:5])}")
        elif isinstance(val, dict):
            parts.append(f"{key}: {val}")
        else:
            parts.append(f"{key}: {val}")
    return "\n".join(parts[:10])


def validate_afb_distribution(exam: ExamStructure) -> str | None:
    """Check AFB distribution. Returns warning string if off, None if OK."""
    total = sum(t.punkte for t in exam.aufgaben)
    if total == 0:
        return None
    
    afb_points = {"I": 0, "II": 0, "III": 0}
    for t in exam.aufgaben:
        level = t.afb_level.strip().upper()
        if level in afb_points:
            afb_points[level] += t.punkte
    
    pcts = {k: round(v / total * 100) for k, v in afb_points.items()}
    
    warnings = []
    if pcts["I"] < 20 or pcts["I"] > 40:
        warnings.append(f"AFB I: {pcts['I']}% (soll 25-35%)")
    if pcts["II"] < 30 or pcts["II"] > 50:
        warnings.append(f"AFB II: {pcts['II']}% (soll 35-45%)")
    if pcts["III"] < 20 or pcts["III"] > 40:
        warnings.append(f"AFB III: {pcts['III']}% (soll 25-35%)")
    
    if warnings:
        return f"⚠️ AFB-Verteilung: {', '.join(warnings)} | Ist: I={pcts['I']}% II={pcts['II']}% III={pcts['III']}%"
    return None


_klausur_agent: Agent[KlausurDeps, ExamStructure] | None = None


def get_klausur_agent() -> Agent[KlausurDeps, ExamStructure]:
    global _klausur_agent
    if _klausur_agent is None:
        _klausur_agent = create_klausur_agent()
    return _klausur_agent
