# Smart Agents Plan — Sub-Agents die denken

> Stand: 2026-02-17
> Ziel: JTBD bestmöglich erfüllen, nicht auf Benchmarks optimieren

## Das Problem

Unsere 12 Material-Agents sind "dumm":
- Sie bekommen alles reingeschoben (Wissenskarte im Prompt, Tools registriert)
- Aber sie **nutzen die Tools nicht eigenständig** — sie generieren One-Shot
- Sie können **keine Rückfragen stellen** wenn Info fehlt
- Sie **lernen nicht** — kein Feedback-Loop aktiv
- Kein **Entwurf vor Export** — Lehrer sieht erst das fertige DOCX

## Das Ziel

Jeder Sub-Agent soll eine **eigene Session** haben, in der er:
1. **Selbst reasoned**: "Habe ich genug Info? Was brauche ich noch?"
2. **Eigenständig Tools aufruft**: Lehrplan, Good Practices, Lehrer-Kontext — WENN er es braucht
3. **Rückfragen stellt**: "Schwerpunkt Stromkreise oder Induktion?" — zurück an den Lehrer
4. **Aus Feedback lernt**: Download = gut, Iteration = verbesserungswürdig
5. **Entwurf zeigt**: Zusammenfassung im Chat BEVOR das DOCX generiert wird

## Architektur-Überblick

```
Lehrer → Hauptagent (Konversation + Vorklärung)
              │
              ▼ generate_material(...)
         Material-Router
              │
              ▼ startet Sub-Agent mit eigener Session
         Sub-Agent (z.B. Klausur-Agent)
              │
              ├── Reasoned: "Brauche Lehrplan" → search_curriculum()
              ├── Reasoned: "Good Practices laden" → get_good_practices()
              ├── Reasoned: "Info fehlt" → ClarificationRequest zurück
              │     ↕ (Two-Phase: State speichern → User fragen → fortsetzen)
              └── Generiert Material → Entwurf im Chat → Lehrer OK → DOCX
```

## Was der Hauptagent dem Sub-Agent übergibt

Der Hauptagent hat bereits Schärfungsfragen gestellt und alles Konversationale geklärt.
Der Sub-Agent bekommt einen **klaren, strukturierten Auftrag**:

| Parameter | Quelle | Immer da? |
|-----------|--------|-----------|
| `fach` | Aus Chat / Profil | ✅ Ja |
| `klasse` | Aus Chat / Profil | ✅ Ja |
| `thema` | Aus Chat | ✅ Ja |
| `material_type` | Router-Entscheidung | ✅ Ja |
| `dauer_minuten` | Aus Chat (oder Default) | ⚠️ Optional |
| `zusatz_anweisungen` | Alles was der Lehrer gesagt hat (inkl. Schärfungsfragen-Antworten) | ⚠️ Optional |
| `teacher_id` | Auth-Context | ✅ Ja (für Tool-Zugriff) |
| `conversation_id` | Chat-Context | ✅ Ja (für get_full_context) |
| Wissenskarte | `build_wissenskarte()` | ✅ Ja (im System-Prompt) |

Der Sub-Agent bekommt also alles was der Hauptagent schon geklärt hat — er soll NICHT nochmal dasselbe fragen.

## 5 Bausteine

### Baustein 1: Sub-Agent Reasoning (Eigenständige Tool-Nutzung)

**Ist:** Sub-Agents haben Tools registriert, aber der System-Prompt sagt ihnen nicht,
dass sie diese NUTZEN sollen. Sie generieren einfach drauflos.
Außerdem fehlt `get_full_context` als Tool — Sub-Agent kann nicht in den Chat schauen.

**Soll:** 
- `get_full_context` als Tool in alle Sub-Agents (Chat-Verlauf nachlesen)
- System-Prompt für jeden Sub-Agent explizit:
```
## Dein Workflow
1. Lies den Auftrag und die Wissenskarte
2. ENTSCHEIDE selbst was du brauchst:
   - Lehrplan relevant? → search_curriculum()
   - Bewährte Aufgaben vorhanden? → get_good_practices()
   - Lehrer-Kontext unklar? → get_full_context() (Chat nachlesen)
   - Lehrer-Präferenzen? → get_teacher_preferences()
3. NUR wenn kritische Info fehlt UND nicht ableitbar → Rückfrage
4. Generiere das Material MIT dem geladenen Wissen

## Entwurf zeigen oder direkt generieren?

Standard: Zeige einen kurzen Entwurf ("Ich würde die Klausur so aufbauen: ...").
Das gibt der Lehrkraft die Chance, frühzeitig zu korrigieren, BEVOR du alles generierst.

Direkt generieren (OHNE Entwurf) nur wenn ALLE diese Bedingungen erfüllt sind:
- Auftrag ist vollständig und eindeutig (Fach, Thema, Klasse, Format, Umfang)
- Keine Interpretationsspielräume bei Schwerpunkt oder Struktur
- Präferenzen der Lehrkraft sind bekannt (aus Wissenskarte)

Beachte den Gesprächskontext: Wenn im Hauptchat bereits ausführlich über
Inhalt, Struktur und Wünsche gesprochen wurde, ist ein Entwurf überflüssig —
diese Vorklärung hat der Hauptagent bereits geleistet.
Nutze get_conversation_context() im Zweifel.

Im Zweifel: lieber kurz validieren. Ein Satz reicht:
"Ich mache 5 Aufgaben, Schwerpunkt Stromkreise, AFB 30/40/30 — passt das?"

## Rückfragen — NUR wenn es NICHT anders geht
Der Hauptagent hat bereits Schärfungsfragen gestellt. Du hast:
- Fach, Klasse, Thema, Dauer (IMMER vorhanden)
- Zusatzanweisungen des Lehrers (WENN vorhanden)
- Wissenskarte mit Präferenzen (WENN vorhanden)
- Tools: Lehrplan, Good Practices, Chat-Verlauf, Lehrer-Präferenzen

Stelle eine Rückfrage NUR wenn:
- Ein WIDERSPRUCH vorliegt (z.B. "45 Min aber 10 Aufgaben unmöglich")
- Eine KRITISCHE Entscheidung ansteht die du NICHT ableiten kannst
  (z.B. "Klausur über 3 Themen, Schwerpunkt auf welchem?")
- NICHT bei: Stil-Fragen, Format-Fragen, Kleinigkeiten
  → nutze Präferenzen oder entscheide selbst

## Was du ZWINGEND brauchst (ohne das NICHT generieren):
- Fach + Thema (muss im Auftrag stehen)
- Klassenstufe (muss im Auftrag oder Profil stehen)
Alles andere: nutze Tools, nutze Defaults, entscheide selbst.
```

**Aufwand:** Prompt-Anpassung + get_full_context Tool für 12 Agents. ~2-3h.
**Engine:** Gemini Pro (Multi-File Prompt-Refactoring)

### Baustein 2: Two-Phase Rückfragen (Multi-Turn Sub-Agent)

**Ist:** Sub-Agent generiert immer, auch wenn er raten muss.

**Soll:** Sub-Agent kann `ClarificationRequest` zurückgeben:
- Material-Router speichert State (message_history) in `agent_sessions`
- Hauptagent bekommt Rückfrage, stellt sie dem Lehrer
- Nach Antwort: `continue_material_generation(session_id, antwort)`
- Sub-Agent setzt fort MIT vollem Kontext (kein Kontextverlust)

**Technisch:**
- Neuer Output-Typ: `MaterialResult` (entweder Material ODER ClarificationRequest)
- Two-Phase Tool Pattern: `generate_material` → `continue_material_generation`
- `agent_sessions` Tabelle existiert bereits — muss erweitert werden um `message_history`
- Pydantic AI `message_history` Serialisierung

**Aufwand:** ~4-6h (Material-Router Umbau + neues Tool + State-Management)
**Engine:** Gemini Pro (komplexe Multi-File Änderung)

### Baustein 3: Feedback-Loop aktivieren

**Ist:** `material_learning_agent.py` existiert, schreibt in `agent_knowledge`.
Aber: kein Signal kommt rein. Downloads werden nicht erfasst, Iterationen nicht.

**Soll:**
- **DOCX-Download** → Signal an Learning-Agent: "Material wurde übernommen" (positiv)
- **continue_material** (Iteration) → Signal: "Material war nicht gut genug" (negativ) + Änderungswunsch
- **Explizites Lob** ("Super!") → Signal: Rating 5/5
- Learning-Agent extrahiert: Was war gut → `good_practice`, Was soll anders → `preference`

**Konkret:**
1. `GET /api/materials/{id}/docx` → nach Download: fire-and-forget Learning-Agent Call
2. `continue_material` Tool → vor Neugenerierung: Feedback-Signal speichern
3. Hauptagent: Bei "Super", "Perfekt", "Genau so" → `save_feedback(material_id, positive=true)`

**Aufwand:** ~2-3h
**Engine:** Gemini Pro (Router + Endpoint-Änderungen)

### Baustein 4: Entwurf vor Export

**Ist:** Sub-Agent → DOCX sofort → Download-Link im Chat

**Soll:** Sub-Agent → Zusammenfassung im Chat → Lehrer bestätigt → DOCX

**Flow:**
1. Sub-Agent generiert Material-Struktur (JSON, nicht DOCX)
2. Material-Router gibt Zusammenfassung an Hauptagent zurück:
   "Klausur: 5 Aufgaben, 45 Punkte, AFB 30/40/30. Themen: Ohm, Kirchhoff, Induktion."
3. Hauptagent zeigt Zusammenfassung + fragt: "Passt das? Oder soll ich was ändern?"
4. Lehrer: "Passt" → DOCX generieren
5. Lehrer: "Ändere Aufgabe 3" → continue_material_generation mit Feedback

**Aufwand:** ~2h (Material-Router Return-Logik + Hauptagent Prompt)
**Engine:** Gemini Pro

### Baustein 5: Good Practices automatisch füllen

**Ist:** `save_good_practice()` existiert, wird nie aufgerufen.

**Soll:** Bei positivem Feedback (Download ohne Iteration):
1. Material-Struktur aus `generated_materials` laden
2. Einzelne Aufgaben/Abschnitte als `good_practice` in `agent_knowledge` speichern
3. Embedding generieren für RAG-Suche
4. Nächste Generierung: Sub-Agent findet diese als Inspiration

**Aufwand:** ~1-2h (im Feedback-Loop integriert, Baustein 3)
**Engine:** Gemini Pro

## Reihenfolge

```
Baustein 1: Reasoning-Prompts        ─── Tag 1, Vormittag (2h)
    │                                      Prompt-Refactoring für 12 Agents
    ▼
Baustein 3: Feedback-Loop            ─── Tag 1, Nachmittag (3h)
    │ + Baustein 5 (Good Practices)        Download-Signal, Iteration-Signal
    ▼
Baustein 4: Entwurf vor Export       ─── Tag 2, Vormittag (2h)
    │                                      Material-Router Return-Logik
    ▼
Baustein 2: Multi-Turn Rückfragen    ─── Tag 2, Nachmittag (4-6h)
    │                                      Two-Phase Pattern, State-Management
    ▼
E2E Test + Feinschliff               ─── Tag 3 (halber Tag)
```

**Warum diese Reihenfolge?**
- Baustein 1 macht die Agents sofort schlauer (Prompt-only, kein Code-Risk)
- Baustein 3+5 aktivieren den Lernloop (größter langfristiger Impact)
- Baustein 4 verbessert UX sofort (Lehrer sieht was kommt)
- Baustein 2 ist der aufwändigste, braucht die solide Basis der anderen

## Betroffene Dateien

| Datei | Bausteine | Änderung |
|-------|-----------|----------|
| `agents/klausur_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/differenzierung_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/escape_room_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/mystery_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/lernsituation_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/podcast_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/gespraechssimulation_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/stundenplanung_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/hilfekarten_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/lernspiel_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/versuchsanleitung_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/h5p_agent.py` | 1, 2 | Neuer Prompt + ClarificationRequest Output |
| `agents/material_router.py` | 2, 3, 4 | Multi-Turn Loop, Entwurf-Return, Feedback-Signal |
| `agents/material_learning_agent.py` | 3, 5 | Feedback-Signale empfangen, Good Practice speichern |
| `agents/main_agent.py` | 2, 4 | `continue_material_generation` Tool, Entwurf-Anzeige |
| `agents/knowledge.py` | 5 | Good Practice Extraction |
| `routers/materials.py` | 3 | Download-Signal senden |
| `models.py` | 2 | ClarificationRequest, MaterialResult Modelle |
| `db.py` | 2 | agent_sessions message_history Serialisierung |

## Token-Optimierung (langfristig, NICHT jetzt)

Steffen hat erwähnt: langfristig Token-Kosten optimieren.
Für SPÄTER notiert, jetzt nur Qualität:

- Haiku für einfache Agents statt Sonnet (wenn Quality ausreicht)
- Wissenskarte komprimieren (100-200 Tokens max)
- Good Practices cappen (Top 3 statt alle)
- Curriculum-Chunks begrenzen (500 Tokens max pro Tool-Call)
- Caching: Gleicher Prompt → gleiche Antwort (für häufige Patterns)

## Lücken aus Code-Review (2026-02-17)

Diese 5 Punkte wurden beim Abgleich Plan ↔ Codebase identifiziert:

### Lücke 1: `conversation_id` fehlt in Material-Pipeline
- `MaterialRequest` hat kein `conversation_id` Feld
- Sub-Agents können `get_full_context()` nicht aufrufen (kein Zugriff auf Chat)
- **Fix:** `conversation_id` zu `MaterialRequest` + allen Deps-Klassen hinzufügen
- **Betrifft:** Baustein 1 + 2

### Lücke 2: `get_full_context` nicht als Tool registriert
- Funktion existiert in `knowledge.py`, ist getestet
- KEIN Sub-Agent hat sie als Tool (nur `search_curriculum` + `get_good_practices`)
- **Fix:** Als drittes Tool in alle 12 Sub-Agents registrieren
- **Betrifft:** Baustein 1

### Lücke 3: Material-Learning-Agent bekommt keine Material-Struktur
- Analysiert nur Chat-Text, nicht die tatsächliche Aufgaben-Struktur
- `save_good_practice` speichert `{"signal": "positive", "rating": 4}` statt echte Aufgaben
- **Fix:** Material-ID + Struktur an Learning-Agent übergeben; bei positivem Signal die echten Aufgaben als Good Practice speichern
- **Betrifft:** Baustein 3 + 5

### Lücke 4: `continue_material` generiert komplett neu
- Nutzt `agent_sessions` für Material-Struktur, aber NICHT für `message_history`
- Sub-Agent hat null Erinnerung an seinen vorherigen Run
- **Fix:** `message_history` serialisieren + in agent_sessions speichern + beim Fortsetzen laden
- **Betrifft:** Baustein 2

### Lücke 5: Nicht alle Deps-Klassen haben Wissenskarte
- `DiffDeps` hat nur `teacher_id` + `teacher_context`, kein `wissenskarte` Feld
- Einige andere Agents könnten ähnlich unvollständig sein
- **Fix:** Alle Deps-Klassen vereinheitlichen (gemeinsame Basisklasse oder einheitliche Felder)
- **Betrifft:** Baustein 1

## Nicht im Scope (bewusst)

- ❌ Benchmark-Runner (Gemini hatte Recht: echte Lehrer-Nutzung > automatisierte Tests)
- ❌ Token-Optimierung (erst Qualität, dann Kosten)
- ❌ Scope-Erweiterung (class/school/global) — kommt wenn Nutzerbasis wächst
- ❌ Upload-Parsing (PDF→Struktur→Example) — Phase 3
- ❌ PDF-Export — DOCX reicht erstmal

## Gemini 2.5 Pro Review (2026-02-17)

### Bestätigt
- Alle 5 identifizierten Lücken korrekt
- Reihenfolge grundsätzlich sinnvoll
- Plan adressiert die richtigen strategischen Ziele

### Zusätzliche Risiken
1. **Serialisierung message_history**: Tool-Call-Objekte + Pydantic-Modelle in JSONB — bei Schema-Änderungen können alte Sessions nicht mehr deserialisiert werden → braucht robuste Fehlerbehandlung (expired statt crash)
2. **Kontextfenster-Explosion**: `get_full_context` mit 10 Nachrichten kann Token-Budget sprengen wenn Nachrichten groß sind → depth-Parameter einbauen
3. **Race Conditions bei Two-Phase**: User schickt Nachricht zwischen Rückfrage und continue → State-Sync-Problem
4. **Frontend muss Entwurf + Rückfragen darstellen können** — nicht nur Backend

### Offene Entscheidungsfragen

**E1: Was ist ein "Entwurf"?**
→ **ENTSCHIEDEN: B — LLM-natürlichsprachlich**
Sub-Agent beschreibt seinen Plan als Teil seines Reasonings: "Ich würde die Klausur so aufbauen: Aufgabe 1 behandelt X, Aufgabe 2 macht Y..." — wie ein guter Assistent. Kein extra LLM-Call, sondern Teil des Agent-Outputs. Hauptagent spielt das an den Lehrer zurück: "Soll ich so starten?"

**E2: Wie tief soll Kontext-Zugriff sein?**
→ **ENTSCHIEDEN: B — Flexibel mit 2 Stufen**
Sub-Agent kann Chat-Kontext in 2 Stufen abrufen:
- `get_conversation_context(depth="summary")` → kompakte Summary (~100-200 Tokens)
- `get_conversation_context(depth="full")` → letzte N Nachrichten (~500-1000 Tokens)
Agent entscheidet selbst wann er wie viel braucht.

**E3: Was lernen wir aus Iterationen?**
→ **ENTSCHIEDEN: B — Diff lernen**
Bei Iteration: Learning-Agent vergleicht Material vorher/nachher und extrahiert konkrete Änderungen (z.B. "Operator von Beurteilen→Erklären", "Punkte reduziert von 12→8"). Damit lernt das System WAS "leichter"/"schwerer"/"anders" konkret bedeutet.

### Fehlende Aspekte
1. **Testing-Strategie** für nicht-deterministische Multi-Turn-Flows
2. **Observability**: Strukturiertes Logging der Sub-Agent-Sessions (Tools, History)
3. **Fehler-Handling** für fehlgeschlagene `continue_material_generation` Calls
4. **Session-Cleanup**: Expired/failed Sessions aufräumen

### Korrigierte Reihenfolge (Gemini-Empfehlung)
Baustein 4 (Entwurf) und 2 (Multi-Turn) NICHT getrennt bauen — beide brauchen denselben Router-Umbau. Stattdessen:

1. **Tag 1 Vormittag**: Baustein 1 (Reasoning-Prompts + Tools) — sofortiger Mehrwert
2. **Tag 1 Nachmittag**: Baustein 3+5 (Feedback-Loop) — größter Langfrist-Hebel
3. **Tag 2**: Router-Schnittstelle umbauen → MaterialResult Union-Type → Baustein 4 (Entwurf) darauf aufsetzen
4. **Tag 3**: Baustein 2 (Multi-Turn Rückfragen) auf der neuen Schnittstelle

## Gemini Review #2 — Codebase-Audit (2026-02-17)

### Deps-Klassen Audit (ALLE Agents)
| Agent | wissenskarte | conversation_id | fach |
|-------|:---:|:---:|:---:|
| KlausurDeps | ✅ | ❌ | ✅ |
| **DiffDeps** | **❌** | **❌** | **❌** |
| EscapeRoomDeps | ✅ | ❌ | ✅ |
| MysteryDeps | ✅ | ❌ | ✅ |
| HilfekarteDeps | ✅ | ❌ | ✅ |
| LernsituationDeps | ✅ | ❌ | ✅ |
| LernspielDeps | ✅ | ❌ | ✅ |
| VersuchsanleitungDeps | ✅ | ❌ | ✅ |
| StundenplanungDeps | ✅ | ❌ | ✅ |
| PodcastDeps | ✅ | ❌ | ✅ |
| GespraechssimulationDeps | ✅ | ❌ | ✅ |
| h5p_agent | n/a | n/a | n/a |

→ ALLE 11 brauchen `conversation_id`. DiffDeps braucht komplett-Fix.

### Tool-Registrierung Audit
| Tool | Vorhanden bei | Fehlt bei |
|------|--------------|-----------|
| search_curriculum | 11/11 Agents | — |
| get_good_practices | 10/11 | DiffAgent |
| get_conversation_context | **0/11** | **ALLE** |
| get_teacher_preferences | **0/11** | **ALLE** |

### Zusätzliche Findings
1. **`services/material_service.py` fehlt im Plan** — muss angepasst werden für Draft/Confirm Flow
2. **`h5p_agent` steht komplett außerhalb** — keine Deps, keine Tools, eigener Flow
3. **Pydantic AI `output_type` ist fix** — Agent kann nicht ENTWEDER ExamStructure ODER ClarificationRequest zurückgeben → Workaround nötig (Union-Type oder Exception)
4. **`patch_material_task` wird obsolet** durch neuen continue-Flow → entfernen
5. **"Diff lernen" (E3=B) braucht eigenen LLM-Call** — Learning-Agent bekommt beide Strukturen (vorher/nachher) und extrahiert den semantischen Unterschied

### Entschiedene Rückfragen
R1: h5p_agent → **AUCH UPGRADEN** (gleiche Architektur wie alle anderen)
R2: `patch_material_task` + altes `continue_material` → **LÖSCHEN**, neuer Flow ersetzt beides
R3: message_history → **pydantic-ai intern** (`model_dump()`/`model_validate()`) + robuste Fehlerbehandlung (Deserialisierung fehlschlägt → Session "expired", Agent startet frisch)

## Gemini Review #3 — Finale Prüfung (2026-02-17)

### Konzeptionelle Lücken gefunden
1. **"Diff lernen" nicht abgebildet** — Learning-Agent bekommt die Material-Strukturen (alt/neu) gar nicht. Braucht eigenen LLM-Call der zwei JSONs vergleicht.
2. **h5p_agent ist kein pydantic-ai Agent** — simples Funktions-Pattern, muss komplett refactored werden um in die neue Architektur zu passen. Mehr Aufwand als gedacht.
3. **`continue_material` darf nicht gelöscht werden** — muss BLEIBEN aber intern umgebaut werden auf den neuen Router-Flow. Umbenennung in `iterate_on_material` empfohlen. `patch_material_task` kann weg.

### Zeitschätzung: 3 Tage NICHT realistisch → 5-6 Tage
- Baustein 1 (Reasoning): 1 Tag ✅ (wie geplant)
- Baustein 3+5 (Feedback + Diff-Lernen): 1 Tag (statt 3h)
- Baustein 4+2 (Entwurf + Multi-Turn): 1.5 Tage (statt 6h)
- E2E Testing: 1 Tag (statt halber Tag)
- h5p_agent Refactoring: 0.5 Tage (nicht eingeplant gewesen)

### Technische Empfehlungen (übernommen)

**Two-Phase Return → Exception-basiert (statt Union-Type)**
```python
class ClarificationNeededError(Exception):
    def __init__(self, question: str, options: list[str] | None = None):
        self.question = question
        self.options = options
```
Sub-Agent `raise`t die Exception → Router fängt sie ab → State speichern → Rückfrage an Hauptagent. Eleganter als Union-Type, kein Wrapper-Modell nötig.

**BaseMaterialDeps Klasse**
```python
@dataclass
class BaseMaterialDeps:
    teacher_id: str
    conversation_id: str
    fach: str
    wissenskarte: str
    teacher_context: str = ""
```
Alle 12 Agents erben davon. Einmal bauen, überall konsistent.

**Pilot-First Strategie**
Klausur-Agent als Pilot — kompletter Flow (Reasoning, Rückfrage, Entwurf, Feedback) NUR für diesen einen Agent. Wenn das Pattern steht → auf die anderen 11 ausrollen.

### State Brittleness Mitigation
- Schema-Versionierung in Pydantic-Modellen
- Defensive Deserialisierung: `try/except ValidationError` → Session "expired", Agent startet frisch
- Sessions verfallen nach 1h automatisch

## Erfolgskriterien

Wann ist das fertig?
1. Sub-Agent ruft eigenständig Tools auf (sichtbar im Log)
2. Sub-Agent stellt Rückfrage wenn kritische Info fehlt
3. Lehrer sieht Entwurf im Chat bevor DOCX kommt
4. Nach 3 Downloads: Good Practices in DB sichtbar
5. 4. Klausur desselben Lehrers ist spürbar besser als die 1.
