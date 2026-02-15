# 🧪 Teststrategie eduhu-assistant

## Überblick: Test-Pyramide

```
              ┌─────────────────────┐
          E2E │  Playwright (Browser)│  ← Wenige, langsame, teure Tests
              │  Echte App im Browser│
              └─────────┬───────────┘
                        │
         ┌──────────────┴──────────────┐
    Integ│  API-Routen + Agent-Logik   │  ← Mittlere Anzahl, schnell, kein LLM
    ation│  FastAPI TestClient + Mocks │
         └──────────────┬──────────────┘
                        │
    ┌───────────────────┴───────────────────┐
Unit│  Reine Funktionen (DOCX, Chunking,   │  ← Viele, blitzschnell, kostenlos
    │  Models, H5P, Suggestions, Prompts)  │
    └───────────────────────────────────────┘
```

---

## 1️⃣ Unit Tests (`test_unit.py`)

**Was wird getestet?** Reine Logik ohne Netzwerk, ohne DB, ohne LLM.

| Kategorie | Was | Warum |
|---|---|---|
| **Pydantic Models** | Validierung von `LoginRequest`, `ChatRequest`, `ProfileUpdate`, `MaterialRequest`, `ExamStructure` | Sicherstellen dass API-Input korrekt validiert wird |
| **Material Type Resolution** | `resolve_material_type("Klassenarbeit") → "klausur"` | Alle Synonyme (test, prüfung, klassenarbeit) müssen korrekt gemappt werden |
| **DOCX-Generierung** | `generate_exam_docx()`, `generate_diff_docx()` | DOCX ist valider ZIP, enthält Thema, alle Aufgaben, Erwartungshorizont, Notenschlüssel |
| **Differenzierung** | `generate_diff_docx()` enthält 3 Niveaus (Basis/Mittel/Erweitert) | Kernfunktion der Differenzierung muss stimmen |
| **Chunking** | `chunk_text()` mit kurzen/langen Texten, Overlap | Lehrplan-PDFs müssen korrekt aufgeteilt werden |
| **H5P-Generierung** | `generate_multichoice`, `generate_blanks`, `generate_truefalse`, `generate_drag_text` | H5P-JSON muss valide Struktur haben |
| **System Prompt** | Statische Blöcke enthalten Rückfrage-Instruktionen, Tool-Liste, Download-Link-Hinweis | KI-Verhalten wird über Prompt gesteuert — falsche Prompts = falsche KI |
| **Suggestions** | `build_suggestions()` mit Profil/Memories/Defaults | Personalisierte Chat-Vorschläge müssen funktionieren |

**Ausführen:**
```bash
cd backend
python -m pytest tests/test_unit.py -v
```

---

## 2️⃣ Integration Tests (`test_integration.py`)

**Was wird getestet?** API-Routen via FastAPI TestClient, DB durch FakeDB ersetzt, LLM gemockt.

| Kategorie | Was | Warum |
|---|---|---|
| **Health** | `GET /api/health` → 200 | Basis-Smoke-Test |
| **Auth** | Login mit korrektem/falschem/leerem Passwort | Login-Flow muss sicher funktionieren |
| **Profile CRUD** | Profil lesen, aktualisieren, partielles Update | PATCH darf nur angegebene Felder ändern |
| **Auth Gate** | Alle geschützten Endpoints ohne `X-Teacher-ID` → 401 | Sicherheitskritisch |
| **Cross-Teacher** | Anderer Lehrer greift auf fremdes Profil zu → 403 | Datenisolation |
| **Chat** | Nachricht senden erstellt Conversation, Antwort hat `assistant`-Rolle | Kernfunktion |
| **Curriculum** | Liste leer, Upload von Nicht-PDF → 400, Oversized → 400 | Input-Validierung |
| **Material API** | Generate → MaterialResponse, Download 404 für unbekannte ID | Material-Pipeline komplett |
| **Error Handling** | `RuntimeError` → 500 (ohne Details), `ValueError` → 400 | Keine internen Fehler leaken |

**Ausführen:**
```bash
cd backend
python -m pytest tests/test_integration.py -v
```

---

## 2b️⃣ Agent-Logik Tests (`test_agents.py`)

**Was wird getestet?** System Prompt Assembly, Memory Agent, Material Service Pipeline — alles mit gemocktem LLM.

| Kategorie | Was | Warum |
|---|---|---|
| **System Prompt** | 4-Block-Aufbau: Identity + Tools + Context + Summary | Smart Preloading: Profil-Daten, Memories, Curricula MÜSSEN im Prompt landen |
| **Prompt für neuen User** | Neuer Lehrer bekommt trotzdem gültigen Prompt | Kein Crash bei leerem Profil |
| **Memory Agent** | Extrahiert Memories aus Chat, speichert in DB | Langzeit-Gedächtnis funktioniert |
| **Memory Agent Fehler** | LLM-Timeout → kein Crash, nur Log | Resilienz |
| **Material Pipeline** | `generate_material()` → Typ-Auflösung → Agent → DOCX → DB | Gesamte Pipeline durchgetestet |
| **DOCX DB Fallback** | Wenn DOCX nicht auf Disk, wird aus DB geladen | Render-Redeploy darf Downloads nicht zerstören |

**Ausführen:**
```bash
cd backend
python -m pytest tests/test_agents.py -v
```

---

## 2c️⃣ Security Tests (`test_security.py`)

**Was wird getestet?** Autorisierung, Input-Sanitization, Error-Leakage.

| Kategorie | Was | Warum |
|---|---|---|
| **Auth-Gate** | Alle Endpoints ohne Header → 401 | Kein unautorisierter Zugriff |
| **Cross-Teacher** | Teacher A kann nicht Profil/Daten von Teacher B lesen/ändern | Datenisolation |
| **Überlange Nachrichten** | 50.000 Zeichen → kein 500 | Resilienz gegen DoS |
| **SQL Injection** | `'; DROP TABLE teachers; --` als Teacher-ID | Supabase nutzt parametrisierte Queries, aber trotzdem testen |
| **Error Leakage** | Interne Fehler zeigen keine API-Keys oder Stacktraces | Sicherheit |

**Ausführen:**
```bash
cd backend
python -m pytest tests/test_security.py -v
```

---

## 3️⃣ E2E Tests (Playwright) (`simulated_teacher_flow.spec.ts`)

**Was wird getestet?** Echte Browser-Interaktion gegen laufende App.

| Test | Was | Warum |
|---|---|---|
| **Login (valid)** | Login → Redirect → `teacher_id` in localStorage | Basis-Flow |
| **Login (invalid)** | Falsches Passwort → Fehlermeldung, kein Redirect | Security |
| **Profil bearbeiten** | Bundesland-Dropdown → Speichern → Erfolgsmeldung | Profil-Daten landen in DB |
| **Chat senden** | Nachricht → AI-Antwort enthält Fachbegriffe | KI-Antwort kommt an |
| **Agent Rückfragen** | Vage Anfrage → Agent fragt zurück | Qualitätsmerkmal der KI |
| **Material + Download** | Explizite Klausur-Anfrage → DOCX-Download-Link → Datei laden | Kritischster Flow |
| **Conversation Persistence** | Seite neuladen → Chat noch da | Keine Datenverluste |
| **Backend Health** | `GET /api/health` → 200 | Smoke-Test |

### Voraussetzungen
```bash
# Frontend starten
npm run dev

# Backend starten  
cd backend && uvicorn app.main:app --reload

# Playwright installieren
npx playwright install
```

### Ausführen
```bash
# Alle E2E Tests
npx playwright test e2e/simulated_teacher_flow.spec.ts

# Einzelnen Test
npx playwright test -g "should generate exam"

# Mit Browser-UI
npx playwright test --headed

# Debug-Modus
npx playwright test --debug
```

### Umgebungsvariablen
```bash
BASE_URL=https://eduhu-assistant.pages.dev     # Für Prod-Tests
BACKEND_URL=https://eduhu-backend.onrender.com
TEACHER_PASSWORD=demo123
```

---

## 4️⃣ KI-Benchmarks (`benchmarks.py`)

**Was wird getestet?** Qualität der KI-Antworten gegen den **Live-Server**.

> ⚠️ Braucht echte API (Anthropic), kostet Tokens!

| Kategorie | Tests | Was wird geprüft |
|---|---|---|
| **Chat Quality** | 4 Szenarien + Agent Ask-Back | Antwort enthält Fachbegriffe, Rückfragen bei vagen Inputs |
| **Memory Agent** | 4 Tests inkl. Cross-Session | Infos werden gemerkt und abgerufen, auch über Session-Grenzen |
| **Curriculum RAG** | 2 Szenarien | Lehrplan-Chunks werden korrekt abgerufen |
| **Research Agent** | 2 Szenarien | Web-Recherche liefert Ergebnisse |
| **Material Generation** | 2 Tests (Klausur + Differenzierung) | Download-Link gültig, Niveaus erwähnt |
| **Smart Preloading** | 1 Test | Profil-Daten (Bundesland, Fächer) erscheinen in KI-Antwort |

### Ausführen
```bash
cd backend
python tests/benchmarks.py --password DEIN_PASSWORT
python tests/benchmarks.py --base-url https://eduhu-backend.onrender.com --password PASSWORT
```

---

## Gesamtübersicht — Wann was laufen lassen

| Phase | Tests | Dauer | Kosten |
|---|---|---|---|
| **Bei jedem Commit** | `test_unit.py` | ~2s | 0€ |
| **Bei jedem PR** | `test_unit.py` + `test_integration.py` + `test_agents.py` + `test_security.py` | ~5s | 0€ |
| **Vor Deployment** | Alle oben + E2E Playwright | ~3min | 0€ |
| **Nach Deployment** | KI-Benchmarks + E2E gegen Prod | ~5min | ~0.50€ |

### Alle lokalen Tests auf einmal:
```bash
cd backend
python -m pytest tests/ -v --tb=short
```
