# Smart Agents — Entwicklungsplan

> Stand: 2026-02-17
> Basiert auf: SMART-AGENTS-PLAN.md (3x Gemini-reviewed)

## Strategie

**Pilot-First**: Klausur-Agent komplett umbauen → Pattern validieren → auf 11 weitere ausrollen.
**Delegation**: Gemini Pro für Multi-File-Änderungen, GLM/MiniMax für Einzel-Dateien.
**Claude = Orchestrator**: Plant, reviewt, testet. Schreibt keinen Code.

## Tag 1: Foundation + Reasoning (Baustein 1)

### Task 1.1: BaseMaterialDeps + Models (30 Min)
**Engine:** Gemini Pro
**Dateien:** `models.py`, neues `agents/base.py`
**Was:**
- `BaseMaterialDeps` dataclass erstellen (teacher_id, conversation_id, fach, wissenskarte, teacher_context)
- `conversation_id: str` zu `MaterialRequest` hinzufügen
- `ClarificationNeededError` Exception in models.py definieren

### Task 1.2: knowledge.py erweitern (30 Min)
**Engine:** Gemini Pro
**Dateien:** `agents/knowledge.py`
**Was:**
- `get_full_context()` um `depth`-Parameter erweitern ("summary" vs "full")
  - summary: Nur Conversation-Summary aus session_logs (~100-200 Tokens)
  - full: Letzte 10 Nachrichten (~500-1000 Tokens)
- `get_teacher_preferences()` als formatierte String-Rückgabe (für Tool-Output)

### Task 1.3: Klausur-Agent Pilot (1h)
**Engine:** Gemini Pro
**Dateien:** `agents/klausur_agent.py`
**Was:**
- `KlausurDeps` → erbt von `BaseMaterialDeps`
- Neuer System-Prompt mit Reasoning-Workflow + Entwurf-Logik + Rückfrage-Regeln
- 2 neue Tools registrieren: `get_conversation_context_tool`, `get_teacher_preferences_tool`
- Testen: Agent ruft eigenständig Tools auf (Log prüfen)

### Task 1.4: Material-Router conversation_id durchreichen (30 Min)
**Engine:** Gemini Pro
**Dateien:** `agents/material_router.py`
**Was:**
- `conversation_id` aus `MaterialRequest` in alle Deps-Objekte durchreichen
- Alle 12 Agent-Instanziierungen anpassen

### Task 1.5: Restliche 10 Agents — Deps + Tools + Prompts (2-3h)
**Engine:** Gemini Pro (Batch, je 2-3 Agents pro Call)
**Dateien:** Alle 10 verbleibenden `*_agent.py`
**Was pro Agent:**
- Deps → erbt von `BaseMaterialDeps`
- System-Prompt ersetzen (Reasoning-Workflow Vorlage)
- `get_conversation_context_tool` + `get_teacher_preferences_tool` registrieren
- DiffAgent: zusätzlich `get_good_practices_tool` nachrüsten

### Task 1.6: h5p_agent Refactoring (2h)
**Engine:** Gemini Pro
**Dateien:** `agents/h5p_agent.py`
**Was:**
- Von Funktions-Pattern auf pydantic-ai Agent umbauen
- H5PDeps (erbt BaseMaterialDeps)
- System-Prompt + Tools (search_curriculum, get_good_practices, get_conversation_context, get_teacher_preferences)
- Output-Type beibehalten (H5P JSON-Struktur)

### Task 1.7: Smoke-Test Tag 1
**Engine:** Claude (manuell)
- Server starten, Klausur generieren
- Logs prüfen: Ruft Agent eigenständig Tools auf?
- Andere Material-Typen stichprobenartig testen

---

## Tag 2: Feedback-Loop (Baustein 3+5)

### Task 2.1: Download-Signal implementieren (1h)
**Engine:** Gemini Pro
**Dateien:** `routers/materials.py`, `agents/material_learning_agent.py`
**Was:**
- `GET /api/materials/{id}/docx`: Nach Download fire-and-forget Call an Learning-Agent
- Learning-Agent bekommt: teacher_id, material_id, material_type, signal="download"
- Learning-Agent lädt Material-Struktur aus `generated_materials` Tabelle

### Task 2.2: Iteration-Signal implementieren (1h)
**Engine:** Gemini Pro
**Dateien:** `agents/main_agent.py` (continue_material), `agents/material_learning_agent.py`
**Was:**
- `continue_material` Tool: VOR Neugenerierung → Feedback-Signal "iteration" + Änderungsanweisung speichern
- Alte Material-Struktur aus agent_sessions laden

### Task 2.3: Good Practice Auto-Save (1h)
**Engine:** Gemini Pro
**Dateien:** `agents/material_learning_agent.py`, `agents/knowledge.py`
**Was:**
- Bei Download-Signal: Material-Struktur aus DB laden
- Einzelne Aufgaben/Abschnitte als `good_practice` in `agent_knowledge` speichern
- Embedding generieren (text-embedding-3-small) für RAG-Suche
- quality_score basierend auf Signal setzen (download=0.7, explizit positiv=0.9)

### Task 2.4: Diff-Learning Agent (2h)
**Engine:** Gemini Pro
**Dateien:** `agents/material_learning_agent.py`
**Was:**
- Neue Funktion `run_diff_learning(old_structure, new_structure, anweisung)`
- Haiku-Call: Vergleiche zwei JSON-Strukturen, extrahiere konkrete Änderungen
- Output: Liste von Präferenz-Updates (z.B. "bevorzugt AFB II über AFB III")
- Speichere als `preference` in `agent_knowledge`

### Task 2.5: Learning-Agent Refactoring (1h)
**Engine:** Gemini Pro
**Dateien:** `agents/material_learning_agent.py`
**Was:**
- `run_material_learning()` überarbeiten: Bekommt jetzt auch material_id + structure
- Dispatch: download → Good Practice speichern, iteration → Diff-Learning, explizit positiv → beides

### Task 2.6: Smoke-Test Tag 2
**Engine:** Claude (manuell)
- Klausur generieren → downloaden → Logs prüfen: Good Practice in DB?
- Klausur iterieren → Logs prüfen: Diff-Learning gelaufen? Präferenz gespeichert?

---

## Tag 3-4: Entwurf + Multi-Turn (Baustein 4+2)

### Task 3.1: Router-Schnittstelle umbauen (2h)
**Engine:** Gemini Pro
**Dateien:** `agents/material_router.py`
**Was:**
- `run_material_agent()` gibt jetzt dict zurück: `{"type": "material"|"draft"|"clarification", ...}`
- ClarificationNeededError abfangen → State speichern → Rückfrage zurückgeben
- Entwurf-Flow: Material generieren → Zusammenfassung erstellen → als Draft zurückgeben
- `agent_sessions` um `message_history` Feld erweitern (JSONB)
- Serialisierung: `result.all_messages()` → `[m.model_dump() for m in messages]`
- Defensive Deserialisierung: try/except ValidationError → Session "expired"

### Task 3.2: Session-Fortsetzung implementieren (2h)
**Engine:** Gemini Pro
**Dateien:** `agents/material_router.py`
**Was:**
- Neue Funktion `continue_agent_session(session_id, user_input)`
- Session laden, message_history deserialisieren
- Agent mit `message_history` fortsetzen: `agent.run(prompt, deps=deps, message_history=history)`
- Ergebnis wieder als material/draft/clarification zurückgeben

### Task 3.3: Main-Agent Tools umbauen (2h)
**Engine:** Gemini Pro
**Dateien:** `agents/main_agent.py`
**Was:**
- `generate_material` Tool: Neuen Router-Return verarbeiten
  - type=draft → Entwurf im Chat zeigen, Session-ID merken
  - type=clarification → Rückfrage an Lehrer weiterleiten
  - type=material → DOCX generieren, Download-Link
- `continue_material` → umbenennen zu `iterate_on_material`, intern `continue_agent_session()` aufrufen
- Neues Tool `confirm_material` → DOCX aus gespeicherter Struktur generieren
- `patch_material_task` LÖSCHEN
- System-Prompt aktualisieren: Wann welches Tool nutzen

### Task 3.4: material_service.py anpassen (1h)
**Engine:** Gemini Pro
**Dateien:** `services/material_service.py`
**Was:**
- `generate_material()` Funktion: conversation_id Parameter hinzufügen
- Neuer Flow: Draft speichern (ohne DOCX) vs. Finalisieren (mit DOCX)
- `confirm_and_generate_docx(session_id)` Funktion

### Task 3.5: agent_sessions Tabelle erweitern (30 Min)
**Engine:** Claude (SQL direkt)
**Was:**
- `message_history JSONB` Spalte hinzufügen
- `schema_version INT DEFAULT 1` Spalte hinzufügen
- Index auf `(conversation_id, status)`

### Task 3.6: Smoke-Test Multi-Turn
**Engine:** Claude (manuell)
- Vager Auftrag → Entwurf im Chat? Bestätigen → DOCX?
- Sehr klarer Auftrag → Direkt DOCX?
- Rückfrage provozieren → Antworten → Fortsetzung funktioniert?
- Session-Expiry: 1h warten → graceful failure?

---

## Tag 5: E2E Testing + Feinschliff

### Task 5.1: Klausur-Agent E2E (2h)
**Engine:** Claude (manuell via API-Calls)
- Happy Path: Klarer Auftrag → direkt Material
- Draft Path: Vager Auftrag → Entwurf → Bestätigung → DOCX
- Clarification Path: Widersprüchlicher Auftrag → Rückfrage → Antwort → Material
- Iteration Path: Material → "Ändere Aufgabe 3" → neues Material
- Feedback Path: Download → Good Practice in DB?
- Diff Path: Iteration → Präferenz gelernt?

### Task 5.2: Alle 12 Agents Stichprobe (2h)
**Engine:** Claude (manuell)
- Je 1 Generierung pro Agent
- Logs prüfen: Tools aufgerufen? Wissenskarte genutzt?
- Entwurf-Logik: Funktioniert die weiche Abwägung?

### Task 5.3: Frontend-Check (1h)
**Engine:** Playwright
- Chat öffnen, Material anfordern
- Entwurf wird korrekt angezeigt?
- Rückfrage wird korrekt angezeigt?
- Bestätigung → DOCX-Link erscheint?

### Task 5.4: Production Deploy + Verify (1h)
- Git push → Render + Cloudflare deploy
- Production Smoke-Test
- Monitoring: Logfire prüfen

---

## Zusammenfassung

| Tag | Baustein | Tasks | Hauptrisiko |
|-----|----------|-------|-------------|
| 1 | Reasoning + Foundation | 7 Tasks | DiffDeps / h5p_agent Refactoring |
| 2 | Feedback-Loop | 6 Tasks | Diff-Learning Prompt-Qualität |
| 3-4 | Entwurf + Multi-Turn | 6 Tasks | State-Serialisierung / Race Conditions |
| 5 | E2E Testing | 4 Tasks | Nicht-deterministische Flows |

**Engine-Verteilung:**
- MiniMax 2.5: ~50% (Einzel-Datei Änderungen, Prompt-Refactoring, Tool-Registrierung)
- Gemini Pro: ~30% (Multi-File, komplexe Architektur-Änderungen wie Router-Umbau)
- Claude: Orchestrierung, SQL, manuelle Tests, Reviews
- GLM: Backup bei einfachen Fixes

**Gesamt: ~25-30 Coding-Tasks, 5 Tage**
