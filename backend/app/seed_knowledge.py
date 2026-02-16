"""Seed generic knowledge profiles for sub-agents into the agent_knowledge table."""

import asyncio
import logging
import os
import sys
from typing import Any

# API Endpoint Stub in a FastAPI router:
# @router.post("/dev/seed-generic-profiles", tags=["dev"])
# async def seed_generic_profiles_endpoint():
#     """Seeds the database with generic agent knowledge profiles."""
#     count = await seed_generic_profiles()
#     return {"message": f"Seeded {count} generic profiles."}

# Ensure 'app' is in the path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


GENERIC_PROFILES: list[dict[str, Any]] = [
    {
        "agent_type": "klausur",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Klausur-Erstellung",
        "content": {
            "beschreibung": "Erstellt eine vollständige Klausur mit Aufgaben, die die Anforderungsbereiche (AFB I-III) abdecken, einem detaillierten Erwartungshorizont und einem Notenschlüssel.",
            "qualitaetskriterien": ["Klare Aufgabenstellung", "Abdeckung der AFB I-III", "Detaillierter Erwartungshorizont mit Punktvergabe", "Transparenter Notenschlüssel", "Angemessene Bearbeitungszeit"],
            "output_format": "Markdown-Dokument mit Aufgaben, Erwartungshorizont und Notenschlüssel.",
            "rueckfragen": ["Welche Themen sollen abgedeckt werden?", "Wie lang ist die Bearbeitungszeit?", "Gibt es spezielle Operatoren, die verwendet werden sollen?"]
        }
    },
    {
        "agent_type": "differenzierung",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für differenziertes Material",
        "content": {
            "beschreibung": "Erstellt Unterrichtsmaterialien in drei verschiedenen Schwierigkeitsstufen (Basis, Mittel, Erweitert), um auf unterschiedliche Lernniveaus einzugehen.",
            "qualitaetskriterien": ["Klare Trennung der Niveaus", "Aufgaben auf gleichem Kerninhalt basierend", "Ansteigende Komplexität", "Unterstützungsangebote für Basis-Niveau", "Herausforderungen für Erweitert-Niveau"],
            "output_format": "Markdown-Abschnitte für jede Niveaustufe mit Aufgaben und Materialien.",
            "rueckfragen": ["Welches Kernthema soll differenziert werden?", "Welche Sozialform ist geplant?", "Gibt es vorhandenes Ausgangsmaterial?"]
        }
    },
    {
        "agent_type": "hilfekarte",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Hilfekarten",
        "content": {
            "beschreibung": "Gestaltet Hilfekarten, die schrittweise Anleitungen, Beispiele oder Tipps zu einer bestimmten Aufgabe oder einem Konzept bieten.",
            "qualitaetskriterien": ["Eine Idee pro Karte", "Klar und verständlich formuliert", "Visuelle Unterstützung (wo möglich)", "Schritt-für-Schritt-Anleitungen", "Konkrete Beispiele"],
            "output_format": "Einzelne Abschnitte im Markdown-Format, die jeweils eine Hilfekarte repräsentieren.",
            "rueckfragen": ["Wobei genau benötigen die Schüler Hilfe?", "Soll die Hilfe einen Prozess erklären oder eine Definition liefern?", "Gibt es ein konkretes Beispielproblem?"]
        }
    },
    {
        "agent_type": "escape_room",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für didaktische Escape Rooms",
        "content": {
            "beschreibung": "Entwickelt ein didaktisches Escape Room-Szenario mit einer Kette von Rätseln, einer fesselnden Hintergrundgeschichte und einem Zeitlimit.",
            "qualitaetskriterien": ["Spannende Erzählung/Rahmenhandlung", "Logisch aufeinander aufbauende Rätsel", "Bezug zum Lerninhalt", "Klare Spielregeln und Ziel", "Materialliste"],
            "output_format": "Markdown-Dokument mit Story, Rätseln, Lösungen und Materialliste.",
            "rueckfragen": ["Welches Thema soll der Escape Room behandeln?", "Wie lange soll das Spiel dauern?", "Für welche Gruppengröße ist es gedacht?"]
        }
    },
    {
        "agent_type": "mystery",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für die Mystery-Methode",
        "content": {
            "beschreibung": "Konzipiert eine Mystery-Unterrichtsmethode mit einer Leitfrage und einer Reihe von Informationskarten (Clues), die zur Lösung führen.",
            "qualitaetskriterien": ["Fesselnde Leitfrage", "Sinnvoll strukturierte Informationskarten", "Enthält 'Red Herrings' (Ablenkungen)", "Fördert kooperatives Arbeiten", "Klare Auflösung am Ende"],
            "output_format": "Markdown-Dokument mit Leitfrage, nummerierten Informationskarten und einer Musterlösung.",
            "rueckfragen": ["Was ist die zentrale Frage (Leitfrage) des Mysterys?", "Welche Kerninformationen sollen die Schüler entdecken?", "Sollen bestimmte falsche Fährten eingebaut werden?"]
        }
    },
    {
        "agent_type": "lernsituation",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Lernsituationen (berufliche Bildung)",
        "content": {
            "beschreibung": "Entwickelt eine handlungsorientierte Lernsituation für die berufliche Bildung, die sich an Lernfeldern und realen beruflichen Problemstellungen orientiert.",
            "qualitaetskriterien": ["Berufsrelevante Problemstellung", "Vollständige Handlung (Informieren, Planen, Durchführen, Kontrollieren)", "Bezug zum Lernfeld", "Aktivierung der Schüler", "Klar definierte Arbeitsaufträge"],
            "output_format": "Markdown-Dokument, das die Lernsituation mit Ausgangslage, Arbeitsauftrag und erwarteten Ergebnissen beschreibt.",
            "rueckfragen": ["Für welchen Ausbildungsberuf und welches Lernfeld ist die Lernsituation?", "Welche berufliche Handlung soll im Mittelpunkt stehen?", "Welche Vorkenntnisse haben die Auszubildenden?"]
        }
    },
    {
        "agent_type": "lernspiel",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Lernspiele",
        "content": {
            "beschreibung": "Erstellt ein Lernspiel mit klaren Regeln, einem didaktischen Ziel, den benötigten Materialien und möglichen Spielvarianten.",
            "qualitaetskriterien": ["Klares Spielziel mit Lernfokus", "Einfache und verständliche Regeln", "Hoher Motivationscharakter", "Benötigtes Material wird aufgelistet", "Mögliche Varianten zur Differenzierung"],
            "output_format": "Markdown-Dokument mit Spielanleitung, Materialliste und didaktischem Kommentar.",
            "rueckfragen": ["Welcher Lerninhalt soll spielerisch vermittelt werden?", "Ist es für Einzel-, Partner- oder Gruppenarbeit gedacht?", "Wie viel Zeit steht zur Verfügung?"]
        }
    },
    {
        "agent_type": "versuchsanleitung",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Versuchsanleitungen",
        "content": {
            "beschreibung": "Schreibt eine strukturierte Anleitung für ein Experiment, inklusive Hypothesenbildung, Materialliste, Durchführungsprotokoll und Auswertung.",
            "qualitaetskriterien": ["Klare Forschungsfrage/Hypothese", "Detaillierte Materialliste", "Schritt-für-Schritt-Anleitung zur Durchführung", "Sicherheitshinweise", "Strukturierte Vorlage für Beobachtung und Auswertung"],
            "output_format": "Markdown-Arbeitsblatt mit Abschnitten für Hypothese, Materialien, Durchführung, Beobachtung und Auswertung.",
            "rueckfragen": ["Welches physikalische, chemische oder biologische Prinzip soll demonstriert werden?", "Welche Materialien stehen zur Verfügung?", "Welche Sicherheitsaspekte sind zu beachten?"]
        }
    },
    {
        "agent_type": "stundenplanung",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Stundenplanung",
        "content": {
            "beschreibung": "Entwirft einen detaillierten Verlaufsplan für eine Unterrichtsstunde in tabellarischer Form, inklusive Phasen, Zeitangaben, Methoden und Medien.",
            "qualitaetskriterien": ["Logischer Aufbau (Einstieg, Erarbeitung, Sicherung)", "Realistische Zeitplanung", "Methodenvielfalt", "Sozialformen-Wechsel", "Klar formulierte Lernziele"],
            "output_format": "Markdown-Tabelle mit Spalten für Phase, Zeit, Lehreraktivität, Schüleraktivität, Methode/Sozialform, Medien.",
            "rueckfragen": ["Was ist das Stundenthema und das Lernziel?", "Wie lang ist die Unterrichtsstunde?", "Welche Vorkenntnisse haben die Schüler?"]
        }
    },
    {
        "agent_type": "podcast",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Podcast-Erstellung",
        "content": {
            "beschreibung": "Erstellt ein Skript für einen didaktischen Podcast, inklusive Sprecherrollen, Soundeffekten und einer klaren didaktischen Rahmung.",
            "qualitaetskriterien": ["Klarer roter Faden", "Dialogische Struktur (mehrere Sprecher)", "Einbindung von Soundeffekten/Musik", "Verständliche Sprache", "Zusammenfassungen/Kernbotschaften"],
            "output_format": "Markdown-Skript mit Sprecherzuweisungen und Regieanweisungen.",
            "rueckfragen": ["Welches Thema soll im Podcast behandelt werden?", "Wie lang soll der Podcast sein?", "Soll es ein Interview, ein Erzählformat oder eine Diskussion sein?"]
        }
    },
    {
        "agent_type": "gespraechssimulation",
        "teacher_id": None,
        "fach": "allgemein",
        "knowledge_type": "generic",
        "source": "system",
        "description": "Generisches Profil für Gesprächssimulationen",
        "content": {
            "beschreibung": "Entwickelt ein Skript für eine Gesprächssimulation (z.B. Arzt-Patient, Verkäufer-Kunde) mit klar definierten Rollen und Zielen.",
            "qualitaetskriterien": ["Realitätsnahes Szenario", "Klare Rollenbeschreibungen", "Definiertes Gesprächsziel", "Mögliche Verzweigungen/Reaktionen", "Feedback-Kriterien zur Auswertung"],
            "output_format": "Markdown-Dokument mit Szenariobeschreibung, Rollenkarten und möglichem Gesprächsverlauf.",
            "rueckfragen": ["Welche Gesprächssituation soll simuliert werden?", "Was ist das Ziel der Simulation für die Lernenden?", "Welche Rollen gibt es?"]
        }
    },
]


async def seed_generic_profiles() -> int:
    """Deletes old generic profiles and inserts a fresh set."""
    logger.info("Deleting existing generic system profiles...")
    await db.delete(
        "agent_knowledge",
        filters={"knowledge_type": "generic", "source": "system"},
    )

    logger.info(f"Deleted old profiles. Now inserting {len(GENERIC_PROFILES)} new profiles...")
    await db.insert_batch("agent_knowledge", GENERIC_PROFILES)
    
    logger.info("Successfully seeded generic profiles.")
    return len(GENERIC_PROFILES)


if __name__ == "__main__":
    asyncio.run(seed_generic_profiles())
