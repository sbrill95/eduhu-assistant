# eduhu — KI-Unterrichtsassistent

Ein KI-gestützter Assistent, der deutsche Lehrkräfte bei Unterrichtsplanung, Materialerstellung, Lehrplan-Integration und Leistungsbewertung unterstützt.

## Features

### Chat-Interface
- Natürlicher Dialog mit Claude Sonnet 4 (Pydantic AI)
- Markdown-Rendering mit Syntax-Highlighting
- Vorschlags-Chips für Schnellaktionen
- Konversationshistorie mit Seitenleiste

### Materialerstellung (12 Typen)
- **Klausuren** — AFB-Verteilung (I/II/III), DOCX-Export, Einzelaufgaben nachträglich anpassbar
- **Differenzierung** — Drei Niveaustufen (Basis/Mittel/Erweitert)
- **Hilfekarten** — Schritt-für-Schritt-Hilfen für schwächere Schüler
- **Mystery** — Informationskarten-Methode mit Leitfrage, Card-Layout DOCX
- **Escape Room** — Narrative + verkettete Rätsel + Lehrkraft-Lösungsseite
- **Lernsituation** — Handlungsorientierte Szenarien (Berufsschule)
- **Lernspiel** — Kreative Spiele mit Regeln + Material
- **Versuchsanleitung** — Experiment-Arbeitsblätter mit Sicherheitshinweisen
- **Stundenplanung** — Verlaufsplan-Tabelle (Phase/Zeit/Inhalt/Methode/Material)
- **Podcast** — Multi-Voice-Skript mit Regieanweisungen → ElevenLabs Audio
- **Gesprächssimulation** — Patienten-/Kundendialog mit Verzweigungen → Audio
- **Interaktive Übungen (H5P)** — Multiple Choice, Lückentext, Wahr/Falsch, Drag & Drop, QuestionSet
  - Teilbar via Zugangscodes (z.B. `tiger42`) + QR-Codes — Schüler brauchen keinen Account
- **Multi-Turn Iteration** — "Ändere Aufgabe 2" funktioniert auf jedes generierte Material

### Bilder
- **Bildgenerierung** — KI-Bilder via Gemini Imagen (iterativ bearbeitbar)
- **Bildersuche** — Lizenzfreie Fotos via Pixabay für Arbeitsblätter und Präsentationen

### Classroom-Tools
- **Countdown-Timer** — Visuelle Timer für Arbeitsphasen
- **Quick Polls** — Abstimmungen mit QR-Code, öffentliche Schüler-Seite (`/poll/:code`)
- **Zufalls-Tools** — Schüler auswählen, Gruppen einteilen, Würfeln
- **Todos** — Aufgabenliste im Chat, interaktive Todo-Cards mit Fälligkeitsdaten

### Audio & Sprache
- **Spracheingabe** — Mikrofon-Button, Whisper-Transkription
- **Vorlesen** — Web Speech TTS auf jeder Assistenten-Nachricht
- **ElevenLabs TTS** — Hochwertige Sprachsynthese für Podcasts + Dialoge
- **Audio-Sharing** — Generierte Audios teilbar via Zugangscode (`/audio/:code`)
- **YouTube-Quiz** — YouTube-URL → Transkript → Quiz (MC, Wahr/Falsch, Lückentext)

### Wissensquellen
- **Lehrplan-RAG** — PDF-Upload, Chunking + Embedding (OpenAI), pgvector-Suche
- **Web-Recherche** — Brave Search API für aktuelle Informationen
- **Wikipedia** — Fachinhalte, Definitionen, historische Fakten direkt abrufbar

### Memory & Profil
- Automatische Extraktion von Lehrer-Präferenzen (Scope: self | class | school | student)
- Profil: Bundesland, Schulform, Fächer, Jahrgangsstufen
- Automatische Chat-Komprimierung bei langen Gesprächen
- Onboarding-Modal beim ersten Login
- **Wissenskarte** — Agent-spezifisches Wissen (Generic Profiles, Good Practices, Teacher Preferences)
- SSE Streaming mit Live Tool-Call-Indikatoren
- Datei-Upload (Bilder via Claude Vision, PDFs via PyMuPDF)

---

## Tech Stack

| Schicht | Technologie |
|---------|-------------|
| **Frontend** | React 19 · TypeScript · Vite 7 · Tailwind CSS 4 |
| **Backend** | Python 3.12 · FastAPI · Pydantic AI |
| **LLM** | Claude Sonnet 4 (Chat + 6 Agents) · Haiku 3.5 (Memory + 6 Agents) |
| **TTS** | ElevenLabs (Multilingual v2) · Web Speech API (Frontend) |
| **Bildgenerierung** | Gemini Imagen (Google) · Pixabay (Stockfotos) |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Sprache** | OpenAI Whisper (Transkription) |
| **Datenbank** | Supabase (PostgreSQL + pgvector) |
| **Web-Suche** | Brave Search API · Wikipedia |
| **Deployment** | Cloudflare Pages (FE) · Render (BE) · Supabase Cloud (DB) |

---

## Lokal starten

### Voraussetzungen

- Node.js 20+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python-Paketmanager)
- Supabase-Projekt mit pgvector Extension
- API-Keys: Anthropic, OpenAI, Gemini (optional), Brave (optional), Pixabay (optional)

### Backend

```bash
cd backend
cp .env.example .env   # Credentials eintragen (siehe unten)
uv sync
uv run uvicorn app.main:app --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev            # Vite Dev-Server auf :5173, Proxy → localhost:8000
```

Dann: http://localhost:5173

### Environment Variables

**Backend (`backend/.env`):**

```env
# Pflicht
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Optional
GEMINI_API_KEY=...           # Bildgenerierung (Gemini Imagen)
PIXABAY_API_KEY=...          # Bildersuche (Stockfotos)
BRAVE_API_KEY=...            # Web-Recherche
LOGFIRE_TOKEN=...            # Observability

# Konfiguration
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
SUB_AGENT_TIMEOUT_SECONDS=120
```

**Frontend (`frontend/.env`):**

```env
VITE_API_URL=https://eduhu-assistant-api.onrender.com  # Produktion
# Lokal: Vite-Proxy übernimmt das (kein VITE_API_URL nötig)
```

---

## Architektur

```
Browser (React 19)
    │
    │ /api/*
    ▼
FastAPI (Render)
    │
    ├── Main Agent (Sonnet) ── Chat + Tool-Dispatch
    │   ├── search_curriculum → pgvector-Suche
    │   ├── search_web → Brave API
    │   ├── search_wikipedia → Wikipedia API
    │   ├── search_images → Pixabay (Stockfotos)
    │   ├── generate_image → Gemini Imagen
    │   ├── remember → user_memories
    │   ├── manage_todos → Todo-CRUD
    │   ├── create_poll / poll_results → Abstimmungen
    │   ├── classroom_tools → Zufall, Gruppen, Würfel
    │   ├── set_timer → Countdown-Timer
    │   ├── patch_material_task → Einzelaufgabe ändern
    │   └── generate_material → Material Router
    │       ├── Klausur Agent (Sonnet) → DOCX
    │       ├── Diff Agent (Sonnet) → DOCX
    │       └── H5P Agent (Haiku) → JSON
    │
    ├── Memory Agent (async) → Preferences extrahieren
    ├── Summary Agent (async) → Chat komprimieren
    └── Learning Agent (async) → Qualitäts-Feedback
    │
    ▼
Supabase (PostgreSQL + pgvector)
```

### Drei-Zonen-Kontext-Modell

| Zone | Inhalt | Laden |
|------|--------|-------|
| **Zone 1 — Always-On** | Profil, Memories, Wissenskarte | Jeder Request (~2K Tokens) |
| **Zone 2 — Smart Preload** | Curriculum Chunks, Good Practices | Bei Bedarf per Tool Call |
| **Zone 3 — On-Demand** | Web-Recherche, tiefe Analyse | Nur wenn explizit angefordert |

Detaillierte Architektur-Docs: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)

---

## Projektstruktur

```
eduhu-assistant/
├── frontend/               # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── components/     # Chat, Layout, Exercises
│   │   ├── pages/          # Route-Seiten
│   │   ├── hooks/          # useChat (zentraler State)
│   │   └── lib/            # API-Client, Auth, Types
│   └── public/             # Static Assets + H5P-Bibliotheken
│
├── backend/                # FastAPI + Python 3.12
│   ├── app/
│   │   ├── agents/         # Pydantic AI Agents
│   │   ├── routers/        # REST-Endpunkte
│   │   ├── services/       # Business-Logik (Material-Export)
│   │   └── config.py       # Settings (.env)
│   └── pyproject.toml
│
├── supabase/migrations/    # DB-Schema
└── docs/                   # Dokumentation
```

---

## Deployment

| Komponente | Plattform | Konfiguration |
|------------|-----------|---------------|
| Frontend | Cloudflare Pages | Auto-Deploy aus Git, Vite Build |
| Backend | Render | `render.yaml` Blueprint, Python 3.12 |
| Datenbank | Supabase Cloud | PostgreSQL 15 + pgvector |

---

## Dokumentation

| Dokument | Beschreibung |
|----------|-------------|
| [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md) | Systemarchitektur, Datenbank, API-Routen, Deployment |
| [`docs/AGENT-ARCHITEKTUR-V2.md`](./docs/AGENT-ARCHITEKTUR-V2.md) | Multi-Turn Agents, Wissenskarte, State Machine |
| [`docs/EDUHU-ASSISTANT-BRIEFING.md`](./docs/EDUHU-ASSISTANT-BRIEFING.md) | Produktvision, UI-Specs, API-Verträge |
| [`docs/EDUHU-DESIGN-SYSTEM.md`](./docs/EDUHU-DESIGN-SYSTEM.md) | Farben, Typografie, Komponenten |
| [`docs/H5P-FEATURE-PLAN.md`](./docs/H5P-FEATURE-PLAN.md) | Interaktive Übungen, Architektur |
| [`docs/JOBS-TO-BE-DONE.md`](./docs/JOBS-TO-BE-DONE.md) | User Needs, Anforderungsanalyse |
| [`docs/MATERIAL-AGENT-RESEARCH.md`](./docs/MATERIAL-AGENT-RESEARCH.md) | Material-Generierung, AFB-Taxonomie |
| [`docs/WISSENSKARTE-KONZEPT.md`](./docs/WISSENSKARTE-KONZEPT.md) | Knowledge-Map-Struktur |
| [`docs/QA-CHECKLIST.md`](./docs/QA-CHECKLIST.md) | Testszenarien, Akzeptanzkriterien |
| [`docs/OVERNIGHT-PLAN.md`](./docs/OVERNIGHT-PLAN.md) | Overnight-Entwicklungsplan |
| [`docs/CODE-QUALITY-PLAN.md`](./docs/CODE-QUALITY-PLAN.md) | 10-Stufen Code Quality Checklist |
| [`docs/WORKFLOW-ANALYSIS.md`](./docs/WORKFLOW-ANALYSIS.md) | Analyse langer Workflows + Risiken |
| [`docs/GEMINI-REVIEW.md`](./docs/GEMINI-REVIEW.md) | Gemini 2.5 Pro Code Review |
| [`docs/MINIMAX-REVIEW.md`](./docs/MINIMAX-REVIEW.md) | MiniMax 2.5 Code Review |

---

## Demo-Accounts

| Name | Passwort |
|------|----------|
| Demo-Lehrer | demo123 |
| Christopher | leopard26 |
| Michelle | otter26 |
| Steffen | krake26 |

---

## Lizenz

Proprietär — © 2026 eduhu
