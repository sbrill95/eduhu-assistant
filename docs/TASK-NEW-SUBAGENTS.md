# Tasks: Material Sub-Agents + Audio-Features + Fundament

## Reihenfolge (WICHTIG)
**Erst Fundament (Tasks 0a-0g), dann neue Agents (Tasks 1-9), dann Audio (Tasks 10-12).**
Ohne Fundament arbeiten alle Agents "blind" — keine Good Practices, keine Preferences, kein Chat-Kontext.

## Design-Prinzipien (NEU)
1. **Prompts radikal vereinfachen**: Nur Kern (Struktur, Qualitätskriterien, Output-Format). Tiefe kommt aus Wissenskarte (DB).
2. **Kontextdaten statt Template-Variablen**: Lernfeld, Halbjahr, Fach etc. aus Konversation + Profil + Curriculum-RAG — nicht im Prompt hardcoden.
3. **Ginger-Logik eliminieren**: Keine if/else im Prompt für Schulform/Beruf — der Agent zieht sich den Kontext selbst.
4. **Überarbeitbarkeit als Grundprinzip**: Jedes Material strukturiert speichern (Teile, nicht Blob), damit "ändere Aufgabe 2" funktioniert.
5. **Multi-Turn bei ALLEN Agents**: Two-Phase Pattern (`generate` → `continue`) + `agent_sessions` State.
6. **Schärfungsfragen vor Generierung**: Jeder Agent fragt erst relevante Parameter ab.
7. **Implicit Feedback Loop**: Download/Iteration = positiv → `agent_knowledge` rating.

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
- `get_full_context(conversation_id)` → Chat-Verlauf zusammenfassen (Summary, nicht raw!)
- `get_example(upload_id)` → Lehrer-Upload laden

### 0d: Generic Profiles seeden
- Aus gesammelten Prompts (4 vorhanden: Lernsituation, Lernspiel, Versuchsanleitung, Stundenplanung)
- Mystery: Eigenen Prompt entwerfen (Recherche-basiert)
- Klausur, Differenzierung: Aus bestehendem Code extrahieren
- Je 1 Eintrag: agent_type + fach + knowledge_type="generic" + content=JSON
- **RADIKAL VEREINFACHT**: Nur Kern-Qualitätskriterien, keine Template-Logik

### 0e: Bestehenden Klausur-Agent upgraden (Pilot)
- Von Haiku → Sonnet
- Wissenskarte in System-Prompt einbauen
- Good Practice Tool anbinden
- Full Context Tool anbinden
- **Strukturierte Speicherung**: Aufgaben einzeln speicherbar für Überarbeitung
- Testen ob Qualität steigt

### 0f: Knowledge Cleanup Job
- Max ~50 Einträge pro teacher_id + agent_type
- Archivierung: quality_score < 0.3 AND times_used = 0 AND älter 90 Tage
- Zusammenführung: Doppelte Preferences mergen
- Cron: 1x/Woche oder bei jedem Material-Generate prüfen

### 0g: material_learning_agent.py umbauen
- Aktuell: Zeigt auf nicht-existierende Tabellen → schlägt still fehl
- Neu: Auf `agent_knowledge` umstellen (eine Tabelle statt drei)
- Implizites Rating: Download/Iteration = positiv → quality_score erhöhen

---

## Task 1: Hilfekarten-Agent
**Prompt**: Eigener Entwurf (Differenzierungsexperte)
**Model**: Haiku (einfache Struktur)
- Kompakte 1-seitige Hilfekarten
- Schrittweise Hilfen + Beispiele + Tipps
- Niveau: Basis / Erweitert / Experte
- DOCX-Output

## Task 2: Escape-Room-Agent
**Prompt**: Eigener Entwurf (Rätsel-Designer)
**Model**: Sonnet (komplex, aufeinander aufbauende Rätsel)
- Story/Narrative + verkettete Rätsel
- Optional: KI-Bildgenerierung für visuelle Rätsel
- Analog/Digital-Varianten
- DOCX-Output + optional H5P

## Task 3: Mystery-Agent
**Prompt**: Eigener Entwurf (Recherche-basiert, kein alter Prompt vorhanden)
**Model**: Sonnet (Informationskarten-Design komplex)
- Leitfrage → Informationskarten → Auflösung
- Kategorien: Fakt / Hinweis / Irreführung
- Differenzierung durch Kartensets
- DOCX-Output

## Task 4: Lernsituation-Agent
**Prompt**: Vereinfacht aus `docs/prompts/lernsituation-pflege.md`
**Model**: Sonnet (berufliche Bildung, Curriculum-intensiv)
- Handlungsorientierung, Lernfelder, Kompetenzbereiche
- Starke Curriculum-RAG Nutzung
- Fallbeispiel-Generator integriert

## Task 5: Lernspiel-Agent
**Prompt**: Vereinfacht aus empfangenem Prompt (file_65)
**Model**: Haiku (kreativ aber strukturiert)
- Kreative Lernspiele für alle Schulformen
- HTML-Output mit Spielname, Regeln, Inhalt, Material, Varianten
- Kompetenzbereich-sensitiv

## Task 6: Versuchsanleitung-Agent (Arbeitsblatt)
**Prompt**: Vereinfacht aus empfangenem Prompt (file_66)
**Model**: Haiku (strukturiert)
- Grad der Offenheit: Geschlossen / Gelenkt / Offen
- Protokollstruktur: Frei / Lückentext / Tabellen
- Sprachniveau-Differenzierung (später über Lerngruppen)
- DOCX-Output

## Task 7: Stundenplanungs-Agent
**Prompt**: Vereinfacht aus empfangenem Prompt (file_67)
**Model**: Sonnet (Verlaufsplan-Tabellen komplex)
- Einzelstunde / Doppelstunde / Unterrichtsreihe
- Verlaufsplan: Zeit | Phasen | LK-Verhalten | SuS-Verhalten | Sozialformen | Medien
- Handlungsorientierung als didaktisches Prinzip
- DOCX-Output

---

## Task 8: YouTube-Quiz
**Engine**: gemini
- YouTube Transcript Extraction (yt-dlp)
- Quiz-Agent: MultiChoice, True/False, Lückentext
- Output: DOCX oder H5P (Brücke zu H5P-Agent)
- Frontend: YouTube-URL im Chat → automatische Erkennung

## Task 9: Text-to-Speech (Vorlesen)
**Phase 1**: Web Speech API (kostenlos, sofort)
- 🔊 Button an jeder Assistant-Nachricht
- Deutsche Stimme

**Phase 2**: ElevenLabs TTS
- Bessere Qualität, natürlichere Stimmen
- `POST /api/tts` → Audio → Frontend

---

## Task 10: Gesprächssimulations-Agent (ElevenLabs)
**API**: ElevenLabs Conversational AI / TTS
**Model**: Sonnet (Szenario-Design) + ElevenLabs (Audio)
- Patienten-/Kundengespräch für berufliche Bildung
- Multi-Voice Dialog (verschiedene Sprecher)
- Eigener Agent mit Schüler-Freigabe (Access-Code Pattern wie H5P)
- Rückfragen: Gesprächstyp, Rollen, Schwierigkeitsgrad, Lernziel
- **Überarbeitbar**: Einzelne Gesprächsteile änderbar
- Benchmark: Gesprächsrealismus, didaktischer Wert

## Task 11: Podcast-Agent (ElevenLabs)
**API**: ElevenLabs TTS (Multi-Voice)
**Model**: Sonnet (Skript) + ElevenLabs (Audio)
- Aus Unterrichtsinhalten einen Podcast generieren
- Multi-Voice (Moderator + Experte / Dialog-Format)
- Rückfragen: Thema, Zielgruppe, Dauer, Format (Monolog/Dialog)
- **Überarbeitbar**: Skript-Abschnitte einzeln änderbar
- DOCX-Skript + Audio-Datei als Output
- Benchmark: Audio-Qualität, inhaltliche Korrektheit

## Task 12: Benchmark-Erweiterung
- Bestehende 18 Tests → erweitern um:
  - Material-Qualität pro Agent-Typ
  - Überarbeitungs-Workflow (Iteration)
  - Audio-Qualität (TTS, Podcast, Gesprächssimulation)
  - Schärfungsfragen-Qualität
  - Wissenskarte-Effekt (mit vs. ohne)
- Gemini als Cross-Validator (wie SCL-Tests)
- Automatisierte Regression nach jedem Deploy
