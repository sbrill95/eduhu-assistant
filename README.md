# eduhu 🦉 — KI-Unterrichtsassistent

Ein KI-gestützter Assistent für Lehrkräfte. Plant Unterricht, erstellt Materialien, kennt den Lehrplan.

## Features

- **💬 Chat** — Natürlicher Dialog mit Claude Sonnet (Pydantic AI)
- **📚 Curriculum RAG** — Lehrpläne hochladen (PDF), semantische Suche via pgvector
- **🧠 Memory** — Merkt sich Fach, Klassen, Präferenzen automatisch
- **🔍 Web-Recherche** — Brave Search für aktuelle Materialien
- **📝 Zusammenfassungen** — Komprimiert lange Gespräche automatisch
- **⚙️ Profil** — Bundesland, Schulform, Fächer, Jahrgangsstufen

## Tech Stack

**Frontend:** Vite + React 19 + TypeScript + Tailwind 4 + Cloudflare Pages  
**Backend:** Python 3.12 + FastAPI + Pydantic AI + httpx  
**DB:** Supabase (PostgreSQL + pgvector)  
**AI:** Claude Sonnet 4 (Anthropic) + OpenAI Embeddings  
**Search:** Brave API  

## Lokal starten

```bash
# Backend
cd backend
cp .env.example .env  # Credentials eintragen
uv sync
uv run uvicorn app.main:app --port 8000 --reload

# Frontend (separates Terminal)
npm install
npm run dev  # Vite proxy → localhost:8000
```

Öffne http://localhost:5173

## Deployment

- **Frontend:** Cloudflare Pages (auto-deploy from Git)
- **Backend:** Render (render.yaml Blueprint)

## Accounts (Demo)

| Name | Passwort |
|------|----------|
| Demo-Lehrer | demo123 |
| Christopher | leopard26 |
| Michelle | otter26 |
| Steffen | krake26 |

## Architektur

```
Browser → Cloudflare Pages (React)
              ↓ /api/*
         FastAPI (Render)
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
 Supabase  Claude   Brave Search
 (pgvector) (Sonnet)  (Web)
```

### Agent-Architektur (Drei-Zonen-Modell)

- **Zone 1 (Always-On):** Profil, Memories, Wissenskarte — im System Prompt
- **Zone 2 (Smart-Preload):** Curriculum Chunks via pgvector — bei Bedarf
- **Zone 3 (On-Demand):** Web-Recherche, tiefe Lehrplan-Analyse

### Sub-Agents

- **Memory Agent** — Extrahiert Scope×Category Memories nach jeder Antwort (async)
- **Curriculum Agent** — Embedding-basierte Lehrplan-Suche
- **Research Agent** — Brave Search Integration
- **Summary Agent** — Komprimiert Gespräche >10 Nachrichten

## Lizenz

Proprietär — © 2026 eduhu
