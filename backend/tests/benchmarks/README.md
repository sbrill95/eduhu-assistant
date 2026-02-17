# Eduhu-Assistant Benchmarks

Automatisierte Benchmarks für die eduhu-assistant App basierend auf dem JTBD-Framework aus `docs/quality/BENCHMARK-JOBS.md`.

## Übersicht

Es gibt drei Benchmark-Suites mit unterschiedlichem Umfang:

| Suite | Tests | Dauer | Zweck |
|-------|-------|-------|-------|
| **Quick** | 10 | ~2 Min | Schneller Smoke-Test, 1 Test pro Kernfunktion |
| **Medium** | 30 | ~10 Min | Tier 1+2 komplett (Kern-Features + Differenzierung) |
| **Full** | 65+ | ~30 Min | Alle Jobs J01-J13 mit allen Sub-Operationen |

## Installation

```bash
cd ~/eduhu-assistant/backend
source .venv/bin/activate
uv add pydantic-evals pytest pytest-asyncio httpx
```

## Konfiguration

Die Benchmarks nutzen folgende Umgebungsvariablen (mit Fallback-Werten):

```bash
# Optional: Basis-URL der API (default: https://eduhu-assistant.onrender.com)
export BENCHMARK_BASE_URL="https://eduhu-assistant.onrender.com"

# Optional: Teacher-ID für Tests (default: a4d218bd-4ac8-4ce3-8d41-c85db8be6e32)
export BENCHMARK_TEACHER_ID="a4d218bd-4ac8-4ce3-8d41-c85db8be6e32"

# Optional: Timeouts in Sekunden
export BENCHMARK_TIMEOUT_GENERATE=120  # Material-Generierung
export BENCHMARK_TIMEOUT_CHAT=120      # Chat-Nachrichten
export BENCHMARK_TIMEOUT_SIMPLE=30     # Einfache API-Calls
```

## Ausführung

### Quick Benchmark (10 Tests, ~2 Min)

```bash
cd ~/eduhu-assistant/backend
source .venv/bin/activate
python -m pytest tests/benchmarks/benchmark_quick.py -v
```

### Medium Benchmark (30 Tests, ~10 Min)

```bash
python -m pytest tests/benchmarks/benchmark_medium.py -v
```

### Full Benchmark (65+ Tests, ~30 Min)

```bash
python -m pytest tests/benchmarks/benchmark_full.py -v
```

### Alle Benchmarks

```bash
python -m pytest tests/benchmarks/ -v
```

### Einzelner Test

```bash
python -m pytest tests/benchmarks/benchmark_quick.py::TestBenchmarkQuick::test_j01_1_klausur_generate -v
```

### Mit Output

```bash
python -m pytest tests/benchmarks/benchmark_quick.py -v -s
```

## Architektur

```
tests/benchmarks/
├── __init__.py
├── README.md                    # Diese Datei
├── conftest.py                  # Shared fixtures (API client, teacher_id, etc.)
├── evaluators/                  # Custom Evaluators
│   ├── __init__.py
│   ├── api_eval.py             # APIGenerateEval, ChatEval, DOCXDownloadEval, H5PAccessEval
│   └── db_eval.py              # MemoryCheckEval
├── benchmark_quick.py           # 10 Tests (~2 Min)
├── benchmark_medium.py          # 30 Tests (~10 Min)
└── benchmark_full.py            # 65+ Tests (~30 Min)
```

## Custom Evaluators

### APIGenerateEval
Ruft `POST /api/materials/generate` auf und prüft:
- HTTP Status Code
- Response Content (optional: enthält bestimmten Text)
- Antwortzeit

### ChatEval
Ruft `POST /api/chat/send` auf und prüft:
- HTTP Status Code
- Response Content
- Konversations-ID für Multi-Turn Tests

### DOCXDownloadEval
Ruft `GET /api/materials/{id}/docx` auf und prüft:
- HTTP Status Code
- Content-Type (DOCX)
- Dateigröße

### H5PAccessEval
Ruft `GET /api/public/pages/{code}` auf und prüft:
- HTTP Status Code
- Seite ist erreichbar

### MemoryCheckEval
Prüft ob ein Memory in der Datenbank gespeichert wurde (Placeholder-Implementierung).

## Test-Coverage

Basierend auf `docs/quality/BENCHMARK-JOBS.md`:

### Quick (10 Tests)
- J01.1 Klausur generieren
- J02.1 Differenzierung
- J03.1 H5P Übungen
- J04.1 Lehrplan durchsuchen
- J05.1 Stundenplanung
- J06.1 Memory merken
- J07.1 Elternbrief
- J08.1 Bildersuche
- J10.1 Podcast-Skript
- J11.1 Multi-Turn Kontext (2 Turns)

### Medium (30 Tests)
Quick + zusätzlich:
- J01: 5 Tests (AFB, Erwartungshorizont, Notenschlüssel, Punkte, Antwortzeit)
- J02: 3 Tests (3 Niveaus, unterscheidbar, gleiches Lernziel)
- J03: 4 Tests (MC, Zugangscode, QR, verschiedene Typen)
- J04: 3 Tests (Lehrplan finden, Kompetenzen, richtiger Lehrplan)
- J05: 3 Tests (Phasen, Methoden, Zeitangaben)
- J06: 3 Tests (explizit merken, implizit, Abruf)
- J11: 4 Tests (2-Turn, 5-Turn, Material-Iteration, Kontext nach 20)
- Q01-Q03: 3 globale Qualitätschecks
- J13: 2 Tests (Todo erstellen, Liste anzeigen)

### Full (65+ Tests)
Alle Jobs J01-J13 mit allen Sub-Operationen + Quality Checks Q01-Q06.

## Wichtige Hinweise

### Rate Limiting
Die Tests warten **5-8 Sekunden** zwischen API-Calls, da die App auf Render Free Tier läuft (512MB RAM).

### Timeouts
- **Material-Generierung**: 120s (Klausuren, Verlaufspläne, etc.)
- **Chat-Calls**: 120s (LLM braucht Zeit)
- **Einfache Calls**: 30s

### Multi-Turn Tests
Tests in J11 (Kontextbewahrung) nutzen `conversation_id` um Kontext über mehrere Turns zu erhalten.

### LLM Judge
Einige Tests (z.B. Fachliche Korrektheit, Niveaus unterscheidbar) sollten in der Zukunft einen LLM Judge verwenden. Aktuell sind sie als Basic-Checks implementiert.

## Nächste Schritte

1. **LLM Judge integrieren** für inhaltliche Bewertung:
   ```python
   from pydantic_evals.evaluators import LLMJudge
   
   judge = LLMJudge(
       instruction="Bewerte ob die Klausur eine sinnvolle AFB-Verteilung hat.",
       grading_key={"pass_criteria": "~30% AFB I, ~40% AFB II, ~30% AFB III"}
   )
   ```

2. **DOCX-Struktur-Checks** implementieren (z.B. mit `python-docx`)

3. **Supabase-Integration** für Memory-Tests (MemoryCheckEval)

4. **CI/CD Integration** (GitHub Actions):
   ```yaml
   - name: Run Quick Benchmark
     run: |
       cd backend
       source .venv/bin/activate
       python -m pytest tests/benchmarks/benchmark_quick.py -v
   ```

5. **Reporting** mit `pydantic-evals` Reporter:
   ```python
   from pydantic_evals.reporting import generate_report
   
   report = generate_report(results)
   report.save("benchmark_results.json")
   ```

## Troubleshooting

### ImportError: cannot import name 'Evaluator'
```bash
cd ~/eduhu-assistant/backend
source .venv/bin/activate
uv add pydantic-evals
```

### Connection Timeout
Erhöhe die Timeouts:
```bash
export BENCHMARK_TIMEOUT_GENERATE=180
export BENCHMARK_TIMEOUT_CHAT=180
```

### Rate Limiting Errors (429)
Erhöhe die Wartezeit zwischen Calls in den Evaluators (aktuell 5s).

## Kontakt

Bei Fragen zu den Benchmarks siehe:
- `docs/quality/BENCHMARK-JOBS.md` für Details zu den Jobs
- Pydantic Evals Docs: https://ai.pydantic.dev/evals/evaluators/overview/
