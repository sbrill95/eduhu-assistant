"""Fixed constants for the eduhu-assistant backend."""

from typing import Literal

MEMORY_CATEGORIES = Literal[
    "faecher_und_themen",
    "klassen_und_schueler",
    "didaktik",
    "pruefungen",
    "materialien",
    "persoenlich",
    "feedback",
    "curriculum",
]

MEMORY_CATEGORIES_LIST: list[str] = [
    "faecher_und_themen",
    "klassen_und_schueler",
    "didaktik",
    "pruefungen",
    "materialien",
    "persoenlich",
    "feedback",
    "curriculum",
]

MEMORY_CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "faecher_und_themen": "Fächer, Lieblingsthemen, Schwerpunkte, aktuelle Unterrichtsthemen",
    "klassen_und_schueler": "Klassenstufen, Lerngruppen, Besonderheiten, Schülerdynamik",
    "didaktik": "Methoden, Unterrichtsstil, Differenzierung, pädagogische Ansätze",
    "pruefungen": "AFB-Präferenzen, Klausurformat, Bewertungskriterien, Prüfungsstil",
    "materialien": "Format-Vorlieben, Länge, Stil, bevorzugte Materialtypen",
    "persoenlich": "Name, Schule, Bundesland, Erfahrung, persönliche Infos",
    "feedback": "Was der Lehrkraft gefiel/nicht gefiel, Korrekturen, Rückmeldungen",
    "curriculum": "Lehrplan-Bezüge, Kompetenzen, Bildungsstandards",
}
