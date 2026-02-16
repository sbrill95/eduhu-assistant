# Tasks: Neue Material Sub-Agents + Fundament

## Reihenfolge (WICHTIG)
**Erst Fundament (Tasks 0a-0d), dann neue Agents (Tasks 1-6).**
Ohne Fundament arbeiten alle Agents "blind" — keine Good Practices, keine Preferences, kein Chat-Kontext.

## Voraussetzung
Warte auf Steffens Prompts aus der alten Software bevor Generic Profiles geschrieben werden.

---

## Task 0: Fundament — agent_knowledge + Wissenskarte

### 0a: Tabelle `agent_knowledge` in Supabase erstellen
- Schema aus `docs/AGENT-ARCHITEKTUR-V2.md` (Zeile 80-115)
- Indices für teacher_id, fach, agent_type, quality_score, embedding
- RLS Policies

### 0b: Wissenskarte-Funktion bauen
- `_build_wissenskarte(teacher_id, agent_type, fach)` → kompakter Text (~100-200 Tokens)
- Aggregiert: Generic Profile + Anzahl Examples + Anzahl Good Practices + Preferences
- Wird in Sub-Agent System-Prompt injiziert

### 0c: Lazy-Loading Tools für Sub-Agents
- `get_good_practices(fach, thema, limit)` → pgvector Similarity Search in agent_knowledge
- `get_full_context(conversation_id)` → Chat-Verlauf laden (damit Sub-Agent weiß was vorher besprochen wurde)
- `get_example(upload_id)` → Lehrer-Upload laden

### 0d: Generic Profiles seeden (Top 8 Fächer)
- Braucht Steffens Prompts als Basis
- Physik, Mathe, Deutsch, Bio, Chemie, Englisch, Geschichte, Politik
- Je 1 Eintrag: agent_type + fach + knowledge_type="generic" + content=JSON

### 0e: Bestehenden Klausur-Agent upgraden (Pilot)
- Von Haiku → Sonnet
- Wissenskarte in System-Prompt einbauen
- Good Practice Tool anbinden
- Full Context Tool anbinden
- Testen ob Qualität steigt

### 0f: material_learning_agent.py umbauen
- Aktuell: Zeigt auf nicht-existierende Tabellen (material_preferences, material_templates, good_practice_materials) → schlägt still fehl in try/except
- Neu: Auf `agent_knowledge` umstellen (eine Tabelle statt drei)
- Implizites Rating: Download/Iteration = positiv → quality_score erhöhen
- Explizites Rating (Phase 2): 👍/👎 Button im Frontend

---

## Task 1: Hilfekarten-Agent (Backend)
**Engine**: gemini (multi-file)
**Dateien**: `backend/app/agents/hilfekarten_agent.py`, `backend/app/agents/material_router.py`, `backend/app/models.py`

### 1a: Agent-Datei erstellen
Erstelle `backend/app/agents/hilfekarten_agent.py` nach dem Pattern von `klausur_agent.py`:
- Pydantic AI Agent mit Haiku
- Output-Typ `HilfekarteStructure` (Pydantic Model)
- System-Prompt: Differenzierungsexperte, fragt nach Gruppe/Niveau/Thema
- Tools: `search_curriculum`, `get_good_practices`
- Deps: `HilfekarteDeps(teacher_id, fach, klasse, thema, zusatz)`

### 1b: Model erstellen
In `backend/app/models.py` ergänze:
```python
class HilfekarteStructure(BaseModel):
    titel: str
    thema: str
    niveau: str  # "Basis" / "Erweitert" / "Experte"
    kerninhalt: str  # Was muss verstanden werden?
    hilfestellungen: list[str]  # Schrittweise Hilfen
    beispiele: list[str]  # Konkrete Beispiele
    tipps: list[str]  # Merksätze / Eselsbrücken
    weiterführend: str | None = None  # Für schnelle Schüler
```

### 1c: Router-Integration
In `material_router.py`:
- Import `get_hilfekarte_agent, HilfekarteDeps`
- Neuer Case `material_type == "hilfekarte"`
- DOCX-Template für Hilfekarten (kompakt, 1-seitig)

### 1d: Tool im Hauptagent
In `main_agent.py` → `generate_material` Tool-Beschreibung erweitern:
- "hilfekarte" als material_type hinzufügen

---

## Task 2: Escape-Room-Agent (Backend)
**Engine**: gemini (multi-file)
**Dateien**: `backend/app/agents/escape_room_agent.py`, `backend/app/agents/material_router.py`, `backend/app/models.py`

### 2a: Agent-Datei erstellen
Erstelle `backend/app/agents/escape_room_agent.py`:
- Pydantic AI Agent mit Sonnet (komplexer als Hilfekarte)
- Output-Typ `EscapeRoomStructure`
- System-Prompt: Rätsel-Designer, aufeinander aufbauende Rätsel, visuelle Elemente
- Tools: `search_curriculum`, `get_good_practices`, `generate_image` (für visuelle Rätsel)
- Rückfragen: Thema, Zeitrahmen, Schwierigkeitsgrad, Gruppengröße, ob digital oder analog

### 2b: Model
```python
class EscapeRoomRaetsel(BaseModel):
    nummer: int
    titel: str
    beschreibung: str
    hinweis: str
    loesung: str
    uebergang: str  # Wie führt die Lösung zum nächsten Rätsel?
    material: str | None = None  # Benötigtes Material
    bild_prompt: str | None = None  # Für KI-Bildgenerierung

class EscapeRoomStructure(BaseModel):
    titel: str
    thema: str
    zeitrahmen_minuten: int
    schwierigkeitsgrad: str
    einfuehrung: str  # Story/Narrative
    raetsel: list[EscapeRoomRaetsel]
    abschluss: str  # Finale Auflösung
    lehrkraft_hinweise: str  # Vorbereitung + Durchführung
```

### 2c: Router + Tool (analog zu 1c/1d)

---

## Task 3: Mystery-Agent (Backend)
**Engine**: gemini (multi-file)
**Dateien**: `backend/app/agents/mystery_agent.py`, `backend/app/agents/material_router.py`, `backend/app/models.py`

### 3a: Agent-Datei
Ähnlich Escape-Room, aber Mystery-Methodik:
- Informationskarten die zusammengeführt werden müssen
- Leitfrage als Ausgangspunkt
- Differenzierung durch unterschiedliche Kartensets

### 3b: Model
```python
class MysteryKarte(BaseModel):
    nummer: int
    inhalt: str
    kategorie: str  # "Fakt", "Hinweis", "Irreführung"
    schwierigkeit: str  # "leicht", "mittel", "schwer"

class MysteryStructure(BaseModel):
    titel: str
    thema: str
    leitfrage: str  # Die zentrale Mystery-Frage
    hintergrund: str  # Kontext/Szenario
    karten: list[MysteryKarte]
    loesung: str  # Erwartete Auflösung
    differenzierung: str  # Tipps für verschiedene Niveaus
    lehrkraft_hinweise: str
```

---

## Task 4: Lernsituation-Agent (Backend)
**Engine**: gemini (multi-file, braucht Curriculum-Integration)
**Dateien**: `backend/app/agents/lernsituation_agent.py`, material_router, models

### 4a: Agent-Datei
- Pydantic AI Agent mit Sonnet (komplex, berufliche Bildung)
- MUSS Curriculum-RAG intensiv nutzen
- System-Prompt: Berufsbildungsexperte, versteht Handlungsorientierung, Lernfelder
- Rückfragen: Beruf/Ausbildungsgang, Lernfeld, Kompetenzbereich, Praxisbezug

### 4b: Model
```python
class LernsituationAufgabe(BaseModel):
    nummer: int
    aufgabe: str
    kompetenzbereich: str  # Fach-, Sozial-, Selbstkompetenz
    anforderungsniveau: str
    erwartete_ergebnisse: list[str]
    material: str | None = None

class LernsituationStructure(BaseModel):
    titel: str
    beruf: str
    lernfeld: str
    handlungssituation: str  # Praxisnahe Beschreibung
    zeitrahmen_stunden: int
    kompetenzen: list[str]  # Zu erwerbende Kompetenzen
    einstieg: str  # Problematisierung / Motivation
    aufgaben: list[LernsituationAufgabe]
    reflexion: str  # Reflexions-/Transferphase
    lehrkraft_hinweise: str
```

---

## Task 5: YouTube-Quiz (Backend + Frontend)
**Engine**: gemini
**Dateien**: `backend/app/agents/youtube_quiz_agent.py`, neuer Router

### 5a: YouTube Transcript Extraction
- `yt-dlp` oder YouTube Transcript API
- Transcript als Text extrahieren
- An Quiz-Generator übergeben

### 5b: Quiz-Agent
- Input: Transcript + Schwerpunkt-Wahl
- Output: Quiz (MultiChoice, True/False, Lückentext)
- Kann als DOCX ODER H5P ausgegeben werden (Brücke zu H5P-Agent)

### 5c: Frontend
- Input-Feld für YouTube-URL
- Oder: YouTube-Link im Chat einfügen → Agent erkennt automatisch

---

## Task 6: Text-to-Speech (Frontend)
**Engine**: gemini-flash (einfach)
**Dateien**: `src/components/chat/ChatMessage.tsx`

### 6a: TTS Button
- 🔊 Button an jeder Assistant-Nachricht
- Web Speech API (kostenlos, sofort)
- `speechSynthesis.speak(new SpeechSynthesisUtterance(text))`
- Deutsche Stimme auswählen

### 6b: Optional Backend TTS (Phase 2)
- Gemini TTS (`gemini-2.5-flash-preview-tts`) für bessere Qualität
- `POST /api/tts` → Audio-Datei → Frontend spielt ab
