# Code Quality Plan — eduhu-assistant

## Kontext
Die Codebase wurde zu ~90% von KI-Agents generiert (Cline+GLM, Gemini, Claude).
Bekannte Risiken bei KI-generiertem Code:
- Fehlende Edge-Case-Abdeckung (KI testet eigene Annahmen, nicht reale Szenarien)
- Security Anti-Patterns (hardcoded secrets, fehlende Auth-Checks, SQL injection)
- Error Handling nur "Happy Path" (try/except pass, leere catch-Blöcke)
- Architektur-Drift (inkonsistente Patterns, Copy-Paste-Duplikation)
- Stale Imports / Dead Code
- Typ-Unsicherheit (Any-Types, fehlende Validierung)
- Race Conditions bei async/concurrent Code

## 10-Stufen Code Quality Check

### Stufe 1: Static Analysis — Sofort automatisierbar
- [ ] `ruff check backend/` (Python Linter — Imports, Style, Bugs)
- [ ] `ruff format --check backend/` (Formatierung)
- [ ] `npx tsc -b` (TypeScript Strict Mode)
- [ ] `npx eslint src/` (Frontend Linting)
- **Ziel:** 0 Errors, 0 Warnings

### Stufe 2: Security Audit
- [ ] Suche nach hardcoded Secrets (`grep -rn "sk-ant\|eyJ\|password" backend/ src/`)
- [ ] Auth-Check auf ALLEN Endpoints (X-Teacher-ID mandatory?)
- [ ] CORS-Konfiguration prüfen (zu offen?)
- [ ] Rate Limiting vorhanden?
- [ ] Input Validation auf allen POST/PATCH Endpoints
- [ ] SQL Injection via Supabase REST (PostgREST ist safe, aber direkte Queries?)
- **Ziel:** Keine P0 Security Issues

### Stufe 3: Error Handling Audit
- [ ] Suche nach `except:` / `except Exception:` ohne Logging
- [ ] Suche nach `pass` in except-Blöcken
- [ ] HTTP Error Responses: Sind sie konsistent? (immer `{"detail": "..."}`)
- [ ] Frontend: Werden API-Fehler dem User angezeigt?
- [ ] Timeout-Handling bei externen API-Calls (Anthropic, ElevenLabs, Brave, Pixabay)
- **Ziel:** Kein stiller Fehler, immer User-Feedback

### Stufe 4: Dead Code & Import Audit
- [ ] Unbenutzte Imports entfernen (ruff + eslint erledigen das)
- [ ] Unbenutzte Funktionen/Variablen finden
- [ ] Verwaiste Dateien (nicht importiert, nicht geroutet)
- [ ] `lib_versions` Dict in h5p.py (jetzt unused → entfernen)
- **Ziel:** Kein toter Code

### Stufe 5: Typ-Sicherheit
- [ ] Python: `mypy backend/` oder `pyright` (Type Checking)
- [ ] Suche nach `Any` Types, `dict` ohne Typ-Parameter
- [ ] Pydantic Models: Sind alle API-Inputs validiert?
- [ ] TypeScript: `strict: true` in tsconfig?
- **Ziel:** Typ-Fehler minimieren

### Stufe 6: API Contract Testing
- [ ] Jeder Endpoint: Request/Response Schema dokumentiert?
- [ ] Jeder Endpoint: Was bei fehlendem Auth? (→ 401)
- [ ] Jeder Endpoint: Was bei ungültiger Input? (→ 422)
- [ ] Jeder Endpoint: Was bei nicht gefundener Ressource? (→ 404)
- [ ] OpenAPI/Swagger Spec generieren und prüfen (`/docs` Endpoint)
- **Ziel:** Konsistente API-Verträge

### Stufe 7: Concurrency & Race Conditions
- [ ] `asyncio.gather` Stellen prüfen — was wenn einer failt?
- [ ] Memory-Agent: Was bei gleichzeitigen Schreibzugriffen?
- [ ] Chat: Doppelklick auf Send → zwei gleichzeitige Requests?
- [ ] Material Generation: Was bei Timeout während Generation?
- [ ] SSE Stream: Was bei Client-Disconnect?
- **Ziel:** Kein Datenverlust bei parallelen Requests

### Stufe 8: Performance & Skalierung
- [ ] N+1 Queries (Schleifen mit einzelnen DB-Calls)
- [ ] Große Payloads (Memory mit 200+ Entries im System-Prompt)
- [ ] Agent Knowledge: Skaliert bei 100+ Entries pro Lehrer?
- [ ] DOCX als base64 in PostgreSQL (→ Supabase Storage)
- [ ] Image-Serving: Werden alte generierte Bilder je gelöscht?
- **Ziel:** Keine Performance-Bottlenecks bei 50+ Lehrern

### Stufe 9: Frontend UX Quality
- [ ] Alle Loading States vorhanden? (Spinner, Skeleton)
- [ ] Alle Error States vorhanden? (Toast, Inline-Error)
- [ ] Mobile Responsive? (320px - 768px)
- [ ] Accessibility? (ARIA Labels, Keyboard Navigation)
- [ ] Empty States? (Keine Konversationen, Kein Curriculum)
- **Ziel:** Keine "weißen Seiten" bei Edge Cases

### Stufe 10: E2E Integration Tests
- [ ] Login → Chat → Material → DOCX Download
- [ ] Login → Chat → H5P Übungen → Schüler-Link testen
- [ ] Login → Profil ausfüllen → Suggestions aktualisiert
- [ ] Login → Curriculum Upload → RAG-Suche im Chat
- [ ] Memory: Konversation 1 → Info geben → Konversation 2 → Info abrufen
- [ ] Multi-Turn: Material erstellen → "Ändere Aufgabe 2" → Neue Version
- **Ziel:** Alle Kern-Flows automatisiert

## Priorisierung
1. **Stufe 1-2 (Security + Static)** — JETZT, vor Tester-Zugang
2. **Stufe 3-4 (Error Handling + Dead Code)** — Diese Woche
3. **Stufe 6-7 (API + Concurrency)** — Vor Beta
4. **Stufe 5,8,9,10 (Types, Perf, UX, E2E)** — Iterativ

## Bekannte Agent-Fehler in dieser Codebase
(Aus bisherigen Reviews + Erfahrung)
1. **Gemini erfindet Imports** — Funktionen/Module die nicht existieren
2. **GLM Copy-Paste-Duplikation** — Gleicher Code in mehreren Dateien
3. **Fehlende Error-Propagation** — try/except schluckt Fehler
4. **Inkonsistente Naming** — `teacher_id` vs `user_id` vs `id`
5. **Hardcoded Magic Numbers** — Token-Limits, Timeouts ohne Konstanten
6. **Fehlende Cleanup** — Generierte Bilder/Audio werden nie gelöscht
7. **DOCX in DB** — Base64-encoded in PostgreSQL statt Object Storage
8. **Auth nur per Header** — Kein JWT, kein Session-Token, leicht fälschbar
