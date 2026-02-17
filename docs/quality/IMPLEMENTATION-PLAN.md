# Implementierungsplan — Quality Benchmarks

## Status-Übersicht: Was ist implementiert, was fehlt?

### ✅ = Funktioniert | ⚠️ = Teilweise | ❌ = Fehlt | 🔧 = Fix nötig

---

## J01 — Klausur erstellen
| ID | Status | Kommentar |
|----|--------|-----------|
| J01.1 AFB-Verteilung | ✅ | Klausur-Agent generiert AFB I/II/III, `validate_afb_distribution()` prüft Verteilung |
| J01.2 Erwartungshorizont | ✅ | Im DOCX enthalten |
| J01.3 Notenschlüssel | ⚠️ | Agent generiert manchmal einen, aber nicht konsistent erzwungen |
| J01.4 DOCX-Download | ✅ | `/api/materials/{id}/docx` funktioniert |
| J01.5 Punkteverteilung | ⚠️ | Keine automatische Validierung ob Punkte aufgehen |
| J01.6 Einzelaufgabe ändern | ✅ | `patch_material_task` Tool |
| J01.7 Fachliche Korrektheit | ⚠️ | Kein automatischer Check, nur LLM-Qualität |
| J01.8 Antwortzeit | ✅ | Typisch 15-40s |

**Fehlend:** Notenschlüssel erzwingen, Punktesummen-Validierung

---

## J02 — Differenzierung
| ID | Status | Kommentar |
|----|--------|-----------|
| J02.1 Drei Niveaus | ✅ | Differenzierungs-Agent liefert Basis/Mittel/Erweitert |
| J02.2 Niveaus unterscheidbar | ✅ | Im Prompt erzwungen |
| J02.3 Gleiches Lernziel | ✅ | Im Prompt erzwungen |
| J02.4 DOCX-Download | ✅ | |
| J02.5 Hilfestellungen Basis | ⚠️ | Nicht explizit erzwungen im Prompt |

**Fehlend:** Hilfestellungen im Basis-Niveau explizit promten

---

## J03 — H5P Übungen
| ID | Status | Kommentar |
|----|--------|-----------|
| J03.1 Übungen generieren | ✅ | MultiChoice, QuestionSet, Blanks, TrueFalse, DragText |
| J03.2 Zugangscode | ✅ | `generate_exercise` Tool generiert Code |
| J03.3 QR-Code | ✅ | qrserver.com API |
| J03.4 Schülerseite | ✅ | `/s/{code}` funktioniert (gestern gefixt!) |
| J03.5 Verschiedene Typen | ✅ | 5 H5P-Typen |
| J03.6 Fachliche Korrektheit | ⚠️ | Kein automatischer Check |

**Status: Vollständig ✅**

---

## J04 — Lehrplan-RAG
| ID | Status | Kommentar |
|----|--------|-----------|
| J04.1 Chunks finden | ✅ | pgvector-Suche via `search_curriculum` Tool |
| J04.2 Kompetenzen benennen | ✅ | Aus Chunks extrahiert |
| J04.3 Kein Lehrplan → Hinweis | ⚠️ | Agent sagt manchmal nichts statt "kein Lehrplan hochgeladen" |
| J04.4 Richtiger Lehrplan | ✅ | Gefiltert nach teacher_id |

**Fehlend:** Expliziter Hinweis wenn kein Lehrplan vorhanden

---

## J05 — Stundenplanung
| ID | Status | Kommentar |
|----|--------|-----------|
| J05.1 Verlaufsplan | ✅ | `stundenplanung_agent.py` liefert Phasen |
| J05.2 Methodenvielfalt | ✅ | Im Prompt erzwungen |
| J05.3 Zeitangaben summieren | ⚠️ | Keine Validierung ob Summe = gewünschte Dauer |
| J05.4 Lehrplanbezug | ⚠️ | Kein automatisches RAG-Lookup im Stundenplanungs-Agent |
| J05.5 DOCX-Export | ✅ | `generate_stundenplanung_docx()` mit Tabelle |

**Fehlend:** Zeitsummen-Validierung, automatischer Lehrplan-Lookup

---

## J06 — Memory
| ID | Status | Kommentar |
|----|--------|-----------|
| J06.1 Explizites Merken | ✅ | `remember` Tool |
| J06.2 Implizites Erkennen | ✅ | Memory-Agent extrahiert automatisch |
| J06.3 Abruf in neuer Session | ✅ | Memories im System-Prompt (Top 50) |
| J06.4 Profilbasierter Kontext | ✅ | Profil in Block 3 des System-Prompts |
| J06.5 Memory beeinflusst Material | ⚠️ | Wissenskarte liefert Präferenzen, aber nicht immer berücksichtigt |

**Status: Größtenteils ✅**

---

## J07 — Elternkommunikation
| ID | Status | Kommentar |
|----|--------|-----------|
| J07.1-J07.4 | ✅ | Hauptagent kann Briefe schreiben (kein spezieller Sub-Agent, Sonnet reicht) |

**Status: Funktioniert via Hauptagent, kein eigener Agent nötig**

---

## J08 — Bilder
| ID | Status | Kommentar |
|----|--------|-----------|
| J08.1 Bildersuche | ✅ | Pixabay via `search_images` |
| J08.2 Bildgenerierung | ✅ | Gemini Imagen via `generate_image` |
| J08.3 Bild iterieren | ⚠️ | Neues Bild ja, aber ohne Referenz auf vorheriges |
| J08.4 Download | ✅ | `/api/images/{id}` |

**Fehlend:** Bild-Iteration mit Referenz auf vorheriges Bild (Gemini hat kein img2img)

---

## J09 — Classroom-Tools
| ID | Status | Kommentar |
|----|--------|-----------|
| J09.1 Timer | ✅ | `set_timer` Tool → CountdownTimer Component |
| J09.2 Zufallsauswahl | ✅ | `classroom_tools` Tool |
| J09.3 Gruppeneintelung | ✅ | `classroom_tools` Tool |
| J09.4 Abstimmung | ✅ | `create_poll` Tool + QR-Code + `/poll/{code}` |
| J09.5 Würfeln | ✅ | `classroom_tools` Tool |

**Status: Vollständig ✅**

---

## J10 — Audio & Sprache
| ID | Status | Kommentar |
|----|--------|-----------|
| J10.1 Podcast-Skript | ✅ | `podcast_agent.py` |
| J10.2 Audio generieren | ✅ | ElevenLabs TTS (paid tier aktiv) |
| J10.3 Gesprächssimulation | ✅ | `gespraechssimulation_agent.py` |
| J10.4 YouTube-Quiz | ⚠️ | Agent gebaut, Proxy auf Render problematisch |

**Fehlend:** YouTube-Proxy zuverlässig machen

---

## J11 — Kontextbewahrung
| ID | Status | Kommentar |
|----|--------|-----------|
| J11.1 2-Turn | ✅ | |
| J11.2 5-Turn | ✅ | |
| J11.3 20+ Turns | ✅ | **Gestern gefixt** — Summary wird jetzt in History eingebaut |
| J11.4 Material-Iteration | ✅ | `continue_material` + `agent_sessions` |

**Status: Vollständig ✅ (nach gestrigem Fix)**

---

## J12 — Recherche
| ID | Status | Kommentar |
|----|--------|-----------|
| J12.1 Web-Recherche | ✅ | Brave Search |
| J12.2 Wikipedia | ✅ | `search_wikipedia` Tool |
| J12.3 Quellenangaben | ⚠️ | Agent gibt nicht immer URLs an |

**Fehlend:** Quellenangaben im Prompt erzwingen

---

## J13 — Todos
| ID | Status | Kommentar |
|----|--------|-----------|
| J13.1 Erstellen | ✅ | `manage_todos` Tool |
| J13.2 Liste anzeigen | ✅ | Todo-Cards |
| J13.3 Abhaken | ✅ | Interaktive Checkboxen |
| J13.4 Fälligkeitsdatum | ✅ | `due_date` in DB |

**Status: Vollständig ✅**

---

## Konversationsqualität (K1-K9)

| ID | Thema | Status | Kommentar |
|----|-------|--------|-----------|
| K1 | Kontextfenster | ✅ | Summary-Fix gestern |
| K2 | Memory-Hygiene | ⚠️ | Cleanup existiert, aber semantic merging fehlt |
| K3 | Halluzinationen | ⚠️ | Kein automatischer Faktencheck |
| K4 | Ton & Sprache | ✅ | System-Prompt steuert das gut |
| K5 | Proaktivität | ⚠️ | Agent schlägt selten von sich aus nächste Schritte vor |
| K6 | Fehlertoleranz | ⚠️ | 429-Retry ja, aber User-Feedback bei Fehlern noch generisch |
| K7 | Ladezeiten | ✅ | SSE Streaming |
| K8 | Datenschutz/Isolation | ⚠️ | Keine JWT-Auth, nur Header-basiert |
| K9 | Offline-Fähigkeit | ❌ | Keine Service Worker, kein Caching |

---

## 15 Interaktionsdimensionen

| # | Dimension | Status |
|---|-----------|--------|
| 1 | Intent-Erkennung | ✅ Hauptagent + Router |
| 2 | Proaktivität | ⚠️ Agent schlägt selten Folge-Aktionen vor |
| 3 | Smarte Rückfragen | ✅ Schärfungsfragen implementiert |
| 4 | Technische Zuverlässigkeit | ✅ Pipelines funktionieren |
| 5 | Sprachkompetenz | ⚠️ Kein explizites Fremdsprachen-Handling |
| 6 | Iterativer Workflow | ✅ Multi-Turn via agent_sessions |
| 7 | Zielgerichtete Überarbeitung | ✅ patch_material_task + continue_material |
| 8 | Export-Flexibilität | ⚠️ Nur DOCX, kein PDF/LaTeX |
| 9 | Material-Erweiterung | ⚠️ "Mach daraus auch H5P" nicht implementiert |
| 10 | Kontextbewahrung | ✅ Summary-Fix |
| 11 | Präferenz-Lernen | ✅ Wissenskarte + Memory |
| 12 | Pädagogische Qualität | ⚠️ Keine automatische Validierung |
| 13 | Fehlertoleranz | ⚠️ Retry ja, User-Feedback generisch |
| 14 | Quellenreferenz | ⚠️ Nicht konsistent |
| 15 | Teilbarkeit | ✅ H5P Codes, Audio Codes, QR |

---

## Implementierungsplan — Priorisiert

### Phase 1: Quick Fixes (je 15-30 Min) — Diese Woche

| # | Was | Wie | Aufwand |
|---|-----|-----|---------|
| 1 | **Notenschlüssel erzwingen** (J01.3) | Klausur-Agent Prompt: "IMMER Notenschlüssel mit Punktetabelle" | 15 Min |
| 2 | **Quellenangaben erzwingen** (J12.3, D14) | System-Prompt: "Nenne IMMER die Quelle bei Recherche-Ergebnissen" | 15 Min |
| 3 | **"Kein Lehrplan" Hinweis** (J04.3) | `search_curriculum` Tool: Wenn 0 Ergebnisse → expliziter Hinweis | 15 Min |
| 4 | **Proaktive Folge-Vorschläge** (D2) | System-Prompt: "Schlage nach jeder Material-Erstellung 2-3 Folgeaktionen vor" | 15 Min |
| 5 | **Hilfestellungen Basis-Niveau** (J02.5) | Differenzierungs-Agent Prompt erweitern | 15 Min |
| 6 | **Zeitsummen-Check Stundenplan** (J05.3) | Post-Generation Validierung wie bei AFB | 30 Min |
| 7 | **Bessere Fehlermeldungen** (K6, D13) | `HTTPException` mit konkretem Detail statt generischem Text | 30 Min |

### Phase 2: Benchmark-Runner (1-2 Tage)

| # | Was | Wie |
|---|-----|-----|
| 1 | **`benchmark_runner.py`** | Python CLI: YAML Testsets laden, API aufrufen, Ergebnisse sammeln |
| 2 | **Regex-Evaluator** | Pattern-Match auf Antworten |
| 3 | **Struktur-Evaluator** | DOCX prüfen (hat Tabelle? hat Erwartungshorizont?) |
| 4 | **Latenz-Evaluator** | Zeitmessung pro Request |
| 5 | **LLM-Judge** | Haiku bewertet Antwortqualität nach Rubrik |
| 6 | **Roundtrip-Evaluator** | Multi-Turn Konversationen simulieren |
| 7 | **YAML-Testsets** | J01-J13 als `test_sets/*.yaml` |
| 8 | **Report-Generator** | JSON + Markdown mit Pass/Fail pro Test |

### Phase 3: Material-Cross-Generation (D9) — Mittelfristig

| # | Was | Wie |
|---|-----|-----|
| 1 | **"Mach daraus H5P"** | Klausur → H5P-Übungen automatisch ableiten |
| 2 | **"Mach daraus Podcast"** | Material → Audio-Skript → TTS |
| 3 | **YouTube als Materialquelle** | Transkript → beliebiger Sub-Agent (nicht nur Quiz) |
| 4 | **Website als Materialquelle** | URL → Text-Extraktion → Material-Kontext |

### Phase 4: Fortgeschrittene Qualität — Langfristig

| # | Was |
|---|-----|
| 1 | PDF-Export (neben DOCX) |
| 2 | Fremdsprachen-Handling (Englisch-Klausuren mit englischem Content) |
| 3 | Automatischer Faktencheck via LLM-Judge |
| 4 | Bild-Iteration mit Referenz (wenn Gemini img2img unterstützt) |
| 5 | Semantic Memory Merging (Anthropic Batch API) |
| 6 | Proper Auth (JWT / Supabase Auth) |

---

---

## Phase 0: Lernloop aktivieren (HÖCHSTE PRIO)

> Die Sub-Agents arbeiten aktuell ohne Fachwissen und ohne Lernfähigkeit.
> Die Architektur (Wissenskarte, agent_knowledge) ist designed und die DB existiert,
> aber der Loop läuft nicht. Das ist der wichtigste architektonische Hebel.

### Ist-Zustand
- ✅ `agent_knowledge` Tabelle (4 Typen: generic, good_practice, preference, feedback)
- ✅ 11 Generic Profiles geseeded
- ✅ `build_wissenskarte()` — kompakte Summary für Sub-Agent Prompt
- ✅ Tools gebaut: `get_good_practices`, `get_teacher_preferences`, `save_preference`, `save_good_practice`
- ✅ `material_learning_agent.py` existiert
- ❌ Nur Klausur-Agent nutzt Wissenskarte — 10 andere Sub-Agents arbeiten statisch
- ❌ Learning-Agent hat kein Feedback-Signal (weiß nicht ob Material gut/schlecht war)
- ❌ Good Practices werden nie gespeichert (Mechanismus da, nie getriggert)
- ❌ DOCX-Download wird nicht als positives Signal erfasst
- ❌ `user_memories` und `agent_knowledge` sind getrennte Silos

### Soll-Loop
```
Lehrer fragt Material an
  → Sub-Agent lädt Wissenskarte (Generic + Good Practices + Teacher Preferences)
  → Generiert Material MIT diesem Wissen
  → Lehrer reagiert:
      - Download = positives Signal
      - Iteration ("ändere das") = negatives Signal
      - Explizites Feedback = direktes Signal
  → Learning-Agent extrahiert: Was war gut/schlecht? Was will der Lehrer?
  → Speichert in agent_knowledge (good_practice / preference / feedback)
  → Nächstes Mal: Sub-Agent hat besseres Wissen
```

### Implementierungsschritte

| # | Was | Wie | Aufwand |
|---|-----|-----|---------|
| 0a | **Wissenskarte in alle Sub-Agents** | `build_wissenskarte(teacher_id, agent_type)` in die 10 fehlenden Agents einbauen (als Teil des System-Prompts) | 1-2h |
| 0b | **Feedback-Signale erfassen** | DOCX-Download → `agent_knowledge` type=feedback, score=1.0; `continue_material` → type=feedback, score=0.3 + Änderungswunsch als content | 1h |
| 0c | **Learning-Agent mit echtem Input** | Nach Material-Generierung: Feedback-Signale + Chat-Kontext + Material-Struktur übergeben | 1h |
| 0d | **Good Practices automatisch speichern** | Bei positivem Feedback (Download ohne Iteration): Material-Struktur als good_practice in agent_knowledge | 30 Min |
| 0e | **Memories → Knowledge Bridge** | `build_wissenskarte()` liest AUCH aus `user_memories` (Fach-Präferenzen, Klasseninfos) — oder Memory-Agent schreibt parallel in agent_knowledge | 1h |
| 0f | **Quality Score Update** | Bei Iteration: Score des gespeicherten Materials senken; bei Download: Score erhöhen. Wissenskarte priorisiert hoch-bewertete Practices. | 30 Min |

**Gesamtaufwand: ~5-6h**

### Erwartetes Ergebnis
- Lehrer erstellt 3 Klausuren → Sub-Agent kennt seine Vorlieben beim 4. Mal
- "Bevorzugt praxisnahe Aufgaben" → wird in allen Material-Typen berücksichtigt
- Good Practices sammeln sich an → neue Lehrer profitieren von generischen Best Practices

---

## Empfehlung

**SOFORT:** Phase 0 (Lernloop) — der architektonische Kern, ohne den alles statisch bleibt
**Parallel:** Phase 1 Quick Fixes (Prompt-Tweaks, 2-3h)
**Diese Woche:** Phase 2 (Benchmark-Runner) — automatisierte Qualitätsmessung
**Nächste Woche:** Phase 3 (Cross-Generation) — das "Wow"-Feature für Demos
