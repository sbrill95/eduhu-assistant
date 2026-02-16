# eduhu — KI-Unterrichtsassistent

Ein KI-gestützter Assistent, der deutsche Lehrkräfte bei Unterrichtsplanung, Materialerstellung, Lehrplan-Integration und Leistungsbewertung unterstützt.

## Features

### Chat-Interface
- Natürlicher Dialog mit Claude Sonnet 4 (Pydantic AI)
- Markdown-Rendering mit Syntax-Highlighting
- Vorschlags-Chips für Schnellaktionen
- Konversationshistorie mit Seitenleiste

### Materialerstellung
- **Klausuren** — Automatische Aufgaben mit AFB-Verteilung (I/II/III), DOCX-Export
- **Differenzierung** — Drei Niveaustufen (Basis/Mittel/Erweitert) zum gleichen Thema
- **Interaktive Übungen (H5P)** — Multiple Choice, Lückentext, Wahr/Falsch, Drag & Drop
  - Teilbar via Zugangscodes (z.B. `tiger42`) — Schüler brauchen keinen Account

### Lehrplan-RAG
- PDF-Upload von Lehrplänen (Bundesland-spezifisch)
- Automatisches Chunking + Embedding (OpenAI text-embedding-3-small)
- Semantische Suche via pgvector — Agent ruft relevante Abschnitte bei Bedarf ab

### Memory-System
- Automatische Extraktion von Lehrer-Präferenzen (Fächer, Klassen, Probleme)
- Scope-Modell: self | class | school | student
- Preferences werden im System-Prompt beim nächsten Request geladen

### Web-Recherche
- Brave Search API für aktuelle Informationen
- Aktuelle Lehr-Methoden, Materialquellen, Kontext

### Profil & Zusammenfassungen
- Bundesland, Schulform, Fächer, Jahrgangsstufen
- Automatische Chat-Komprimierung bei langen Gesprächen

---

## Tech Stack

| Schicht | Technologie |
|---------|-------------|
| **Frontend** | React 19 · TypeScript · Vite 7 · Tailwind CSS 4 |
| **Backend** | Python 3.12 · FastAPI · Pydantic AI |
| **LLM** | Claude Sonnet 4 (Chat + Materialien) · Haiku (Sub-Agents) |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Datenbank** | Supabase (PostgreSQL + pgvector) |
| **Web-Suche** | Brave Search API |
| **Deployment** | Cloudflare Pages (FE) · Render (BE) · Supabase Cloud (DB) |

---

## Lokal starten

### Voraussetzungen

- Node.js 20+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python-Paketmanager)
- Supabase-Projekt mit pgvector Extension
- API-Keys: Anthropic, OpenAI, Brave (optional)

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
BRAVE_API_KEY=...
LOGFIRE_TOKEN=...

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
    │   ├── remember → user_memories
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
├── functions/              # Cloudflare Workers (alternativer BE)
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
