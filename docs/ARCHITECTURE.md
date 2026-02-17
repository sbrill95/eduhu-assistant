# Architektur — eduhu Assistant

> Letzte Aktualisierung: Februar 2026

## Inhaltsverzeichnis

- [Systemübersicht](#systemübersicht)
- [Tech Stack](#tech-stack)
- [Systemdiagramm](#systemdiagramm)
- [Frontend](#frontend)
- [Backend (FastAPI)](#backend-fastapi)
- [Multi-Agent-Architektur](#multi-agent-architektur)
- [Drei-Zonen-Kontext-Modell](#drei-zonen-kontext-modell)
- [Datenbank](#datenbank)
- [API-Routen](#api-routen)
- [Deployment](#deployment)
- [Verzeichnisstruktur](#verzeichnisstruktur)
- [Weiterführende Docs](#weiterführende-docs)

---

## Systemübersicht

eduhu ist ein KI-gestützter Unterrichtsassistent für deutsche Lehrkräfte. Das System besteht aus drei Hauptschichten:

1. **Frontend** — React 19 SPA mit Chat-Interface, Lehrplan-Upload und Profilseiten
2. **Backend** — FastAPI-Server mit Multi-Agent-Orchestrierung (Pydantic AI)
3. **Datenbank** — Supabase (PostgreSQL + pgvector) für Persistence und Vektorsuche

---

## Tech Stack

| Schicht | Technologie | Zweck |
|---------|-------------|-------|
| Frontend | React 19, TypeScript, Vite 7, Tailwind 4 | SPA mit Chat-UI |
| Backend | Python 3.12, FastAPI, Pydantic AI | API + Agent-Orchestrierung |
| LLM | Claude Sonnet 4 (Haupt-Agent), Haiku (Sub-Agents) | KI-Konversation + Materialgenerierung |
| Embeddings | OpenAI text-embedding-3-small (1536d) | Lehrplan-Vektorsuche |
| Datenbank | Supabase PostgreSQL + pgvector | Daten + Vektorspeicher |
| Web-Suche | Brave Search API, Wikipedia API | Aktuelle Recherche + Fachinhalte |
| Bildgenerierung | Gemini Imagen (Google) | KI-Bilder für Materialien |
| Bildersuche | Pixabay API | Lizenzfreie Stockfotos |
| Sprache→Text | OpenAI Whisper | Sprachnachrichten-Transkription |
| Dokument-Export | python-docx | DOCX-Generierung |
| Interaktive Übungen | H5P (h5p-standalone) | Lückentexte, Multiple Choice, etc. |
| Deployment | Cloudflare Pages (FE), Render (BE), Supabase Cloud (DB) | Hosting |

---

## Systemdiagramm

```
┌─────────────────────────────────────────────────────────┐
│                   BROWSER (React 19)                    │
│                                                         │
│  ChatPage · CurriculumPage · ProfilePage · MaterialPage │
│  ExercisePage (/s/:code) · PollPage (/poll/:code)       │
└─────────────────┬───────────────────────────────────────┘
                  │ /api/* (fetch)
                  ▼
┌─────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Render)                  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │            Routers (REST-Endpunkte)                │  │
│  │  auth · chat · curriculum · profile · materials    │  │
│  │  h5p · todos · transcribe · images                 │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│  ┌───────────────────▼───────────────────────────────┐  │
│  │          Agent-Orchestrierung (Pydantic AI)        │  │
│  │                                                     │  │
│  │  Main Agent (Sonnet) ─── Chat + Tool-Dispatch      │  │
│  │    ├─ search_curriculum ──→ Curriculum Agent        │  │
│  │    ├─ search_web ─────────→ Research Agent (Brave)  │  │
│  │    ├─ search_wikipedia ───→ Wikipedia API           │  │
│  │    ├─ search_images ──────→ Pixabay API             │  │
│  │    ├─ generate_image ─────→ Gemini Imagen           │  │
│  │    ├─ remember ───────────→ Memory-Tabelle          │  │
│  │    ├─ manage_todos ───────→ Todo-CRUD               │  │
│  │    ├─ create_poll ────────→ Abstimmungen            │  │
│  │    ├─ classroom_tools ────→ Zufall/Gruppen/Würfel   │  │
│  │    ├─ set_timer ──────────→ Countdown               │  │
│  │    ├─ patch_material_task → Aufgabe editieren       │  │
│  │    └─ generate_material ──→ Material Router         │  │
│  │                               ├─ Klausur Agent (S)  │  │
│  │                               ├─ Diff Agent (S)     │  │
│  │                               └─ H5P Agent (H)      │  │
│  │                                                     │  │
│  │  Async Post-Processing (Fire-and-Forget):           │  │
│  │    ├─ Memory Agent (Haiku) → Preferences extrah.    │  │
│  │    ├─ Summary Agent (Haiku) → Chat komprimieren     │  │
│  │    └─ Learning Agent (Haiku) → Qualitäts-Feedback   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────┬───────────────┬───────────────┬───────┘
                  │               │               │
                  ▼               ▼               ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐
    │ Supabase │ │Anthropic │ │  Brave   │ │ Gemini  │ │ Pixabay │
    │PostgreSQL│ │ Claude   │ │ Search   │ │ Imagen  │ │  API    │
    │+pgvector │ │Sonnet/H  │ │  API     │ │  API    │ │         │
    └──────────┘ └──────────┘ └──────────┘ └─────────┘ └─────────┘
                      │
               ┌──────┴──────┐
               │ OpenAI API  │
               │Embeddings + │
               │  Whisper    │
               └─────────────┘
```

---

## Frontend

### Tech-Details

- **Framework:** React 19 mit Hooks (kein Redux — App-State reicht aus)
- **Build:** Vite 7 mit HMR und Proxy (`/api` → `localhost:8000`)
- **Styling:** Tailwind CSS 4 mit Custom Design Tokens (siehe `EDUHU-DESIGN-SYSTEM.md`)
- **Routing:** React Router v7

### Routing-Tabelle

| Pfad | Komponente | Zugang |
|------|------------|--------|
| `/` | `LoginPage` | Öffentlich |
| `/chat` | `ChatPage` | Authentifiziert |
| `/curriculum` | `CurriculumPage` | Authentifiziert |
| `/profile` | `ProfilePage` | Authentifiziert |
| `/material` | `MaterialPage` | Authentifiziert |
| `/s` | `ExerciseAccessPage` | Öffentlich (Schüler) |
| `/s/:code` | `ExercisePage` | Öffentlich (Schüler) |
| `/poll/:code` | `PollPage` | Öffentlich (Schüler) |

### Komponenten-Übersicht

```
src/
├── components/
│   ├── chat/
│   │   ├── ChatMessage.tsx      # Nachricht (AI/User), Markdown-Rendering
│   │   ├── ChatInput.tsx        # Textarea + Datei-Upload + Spracheingabe + Senden
│   │   ├── ChipSelector.tsx     # Vorschlags-Chips (Schnellaktionen)
│   │   ├── TypingIndicator.tsx  # Animierter Lade-Indikator
│   │   ├── TodoCard.tsx         # Interaktive Todo-Liste im Chat
│   │   ├── ImageCard.tsx        # KI-generierte Bilder (Vollbild, Download, Teilen)
│   │   ├── QRCard.tsx           # QR-Code-Karte für Übungen/Polls
│   │   └── CountdownTimer.tsx   # Visueller Countdown für Arbeitsphasen
│   ├── layout/
│   │   ├── Header.tsx           # App-Header mit Navigation
│   │   └── ConversationSidebar.tsx  # Gesprächsliste + Neu/Löschen
│   └── exercises/
│       └── H5PPlayer.tsx        # H5P-Standalone-Integration
├── pages/
│   ├── ChatPage.tsx             # Haupt-Chat-Interface
│   ├── LoginPage.tsx            # Passwort-Login
│   ├── CurriculumPage.tsx       # PDF-Upload + Verwaltung
│   ├── ProfilePage.tsx          # Profil bearbeiten
│   ├── MaterialPage.tsx         # Generierte Materialien
│   ├── ExerciseAccessPage.tsx   # Code-Eingabe für Schüler
│   ├── ExercisePage.tsx         # H5P-Player für Schüler
│   └── PollPage.tsx             # Abstimmungs-Seite für Schüler
├── hooks/
│   └── useChat.ts               # Zentraler Chat-State (Messages, API-Calls)
└── lib/
    ├── api.ts                   # API-Client (fetch-Wrapper)
    ├── auth.ts                  # Login/Logout, Token-Handling
    └── types.ts                 # TypeScript-Interfaces
```

### State Management

Die App nutzt `useChat()` als zentralen Hook für den Chat-State:

- `messages` — Nachrichtenliste der aktuellen Konversation
- `conversationId` — Aktive Konversations-ID
- `isTyping` — Ladeindikator
- `suggestions` — Profilbasierte Vorschlagschips
- `sendMessage(text, convId)` — Nachricht senden + Antwort empfangen
- `loadConversation(convId)` — Konversation wechseln

Auth-State (`teacher_id`, `token`) wird in `localStorage` gespeichert (Phase 1 — kein JWT).

---

## Backend (FastAPI)

### Verzeichnisstruktur

```
backend/
├── app/
│   ├── main.py           # FastAPI-App, CORS, Startup
│   ├── config.py          # Settings aus .env (Pydantic BaseSettings)
│   ├── db.py              # Supabase-Client-Wrapper
│   ├── deps.py            # Dependency Injection (get_current_teacher_id)
│   ├── models.py          # Pydantic Request/Response-Models
│   ├── exceptions.py      # Exception-Handler
│   │
│   ├── agents/            # Pydantic AI Agents
│   │   ├── main_agent.py          # Haupt-Chat-Agent (Sonnet)
│   │   ├── klausur_agent.py       # Klausur-Generierung (Sonnet)
│   │   ├── differenzierung_agent.py # Differenzierung (Sonnet)
│   │   ├── h5p_agent.py           # Interaktive Übungen (Haiku)
│   │   ├── curriculum_agent.py    # Lehrplan-RAG-Suche
│   │   ├── research_agent.py      # Web-Recherche (Brave)
│   │   ├── memory_agent.py        # Präferenz-Extraktion (Haiku)
│   │   ├── summary_agent.py       # Chat-Komprimierung (Haiku)
│   │   ├── image_agent.py         # Bildgenerierung (Gemini Imagen)
│   │   ├── pixabay_agent.py       # Bildersuche (Pixabay)
│   │   ├── material_router.py     # Agent-Orchestrierung
│   │   ├── system_prompt.py       # Dynamischer System-Prompt-Builder
│   │   └── llm.py                 # Modell-Instanziierung
│   │
│   ├── routers/           # FastAPI Endpoints
│   │   ├── auth.py        # Login
│   │   ├── chat.py        # Chat-Send, History, Conversations, Streaming
│   │   ├── curriculum.py  # Upload, List, Delete
│   │   ├── profile.py     # Get, Update, Suggestions
│   │   ├── materials.py   # Download + Einzelaufgaben-Patch
│   │   ├── h5p.py         # Übungs-Generierung + Public Access
│   │   ├── todos.py       # Todo-CRUD
│   │   ├── transcribe.py  # Whisper Sprache→Text
│   │   └── images.py      # Generierte Bilder ausliefern
│   │
│   └── services/
│       └── material_service.py  # Material-Generierung + DOCX-Export
│
├── curricula/             # Sample-Lehrpläne (PDFs)
├── pyproject.toml         # Python Dependencies (uv)
└── Procfile               # Render Deployment
```

### Request-Lifecycle (Chat)

```
POST /api/chat/send { message, conversation_id? }
  │
  ├─ 1. Auth: get_current_teacher_id (X-Teacher-ID Header)
  ├─ 2. Conversation erstellen/laden
  ├─ 3. User-Nachricht in DB speichern
  ├─ 4. Letzte 20 Nachrichten als History laden
  ├─ 5. System-Prompt bauen (Profil + Memories + Wissenskarte)
  │
  ├─ 6. Main Agent (Sonnet) aufrufen
  │     ├─ Tool Calls (optional):
  │     │   ├─ search_curriculum(query) → pgvector-Suche
  │     │   ├─ search_web(query) → Brave API
  │     │   ├─ search_wikipedia(query) → Wikipedia API
  │     │   ├─ search_images(query) → Pixabay
  │     │   ├─ generate_image(prompt) → Gemini Imagen
  │     │   ├─ remember(key, value) → user_memories
  │     │   ├─ manage_todos(action, text) → Todo-CRUD
  │     │   ├─ create_poll(question, options) → Abstimmung
  │     │   ├─ classroom_tools(action) → Zufall/Gruppen/Würfel
  │     │   ├─ set_timer(minutes) → Countdown
  │     │   ├─ patch_material_task(id, index) → Aufgabe editieren
  │     │   └─ generate_material(...) → Material Router
  │     │       ├─ klausur_agent → ExamStructure → DOCX
  │     │       ├─ diff_agent → DiffStructure → DOCX
  │     │       └─ h5p_agent → H5PContent → JSON
  │     └─ Antwort (Markdown-String mit Rich Cards)
  │
  ├─ 7. Assistant-Nachricht in DB speichern
  ├─ 8. Async Fire-and-Forget:
  │     ├─ memory_agent → Preferences extrahieren
  │     ├─ summary_agent → Chat komprimieren (wenn >10 Msg)
  │     └─ learning_agent → Qualitätssignale extrahieren
  │
  └─ 9. Response: { conversation_id, message: { content, chips?, attachments? } }
```

---

## Multi-Agent-Architektur

### Agent-Übersicht

| Agent | Modell | Aufgabe | Trigger |
|-------|--------|---------|---------|
| **Main Agent** | Sonnet 4 | Chat, Tool-Dispatch (15 Tools) | Jede Nachricht |
| **Klausur Agent** | Sonnet 4 | Klausuren generieren (AFB I-III) | `generate_material(type="klausur")` |
| **Differenzierung Agent** | Sonnet 4 | 3-stufige Differenzierung | `generate_material(type="differenzierung")` |
| **H5P Agent** | Haiku | Interaktive Übungen | `generate_exercise(...)` |
| **Image Agent** | — (Gemini API) | KI-Bildgenerierung | `generate_image(prompt)` |
| **Pixabay Agent** | — (API-Call) | Lizenzfreie Bildersuche | `search_images(query)` |
| **Curriculum Agent** | — (DB-Query) | pgvector-Lehrplansuche | `search_curriculum(query)` |
| **Research Agent** | — (API-Call) | Brave Web-Recherche | `search_web(query)` |
| **Memory Agent** | Haiku | Lehrer-Präferenzen extrahieren | Async nach jeder Antwort |
| **Summary Agent** | Haiku | Chat komprimieren | Async wenn >10 Nachrichten |
| **Learning Agent** | Haiku | Qualitätssignale aus Feedback | Async nach Material-Feedback |

### Material Router (Orchestrierung)

Der `material_router.py` fungiert als Dispatcher:

1. Empfängt `MaterialRequest` vom Main Agent
2. Lädt Kontextdaten (Wissenskarte, Lehrer-Präferenzen, Curriculum-Chunks)
3. Routet zum passenden Spezialisten-Agent
4. Verarbeitet strukturierte Ausgabe → DOCX / H5P JSON
5. Speichert Ergebnis in Supabase Storage
6. Gibt Download-Link + Zusammenfassung zurück

### Pydantic AI Agent-Muster

```python
# Beispiel: Aufbau eines Agents
agent = Agent(
    model=get_sonnet(),
    system_prompt=build_system_prompt,  # Dynamisch
    tools=[search_curriculum, search_web, remember, generate_material],
    result_type=str,                     # Markdown-Antwort
    deps_type=AgentDeps,                 # teacher_id, db, settings
)
```

---

## Drei-Zonen-Kontext-Modell

Das System organisiert Kontext in drei Zonen nach Latenz und Kosten:

### Zone 1 — Always-On (~2K Tokens)

Im System Prompt bei jedem Request enthalten:

- Lehrer-Profil (Name, Fächer, Klassen, Bundesland)
- Letzte Memories aus `user_memories`
- Wissenskarte (Schlüsselkonzepte)
- Präferenzen (Format, Stil, Differenzierungsansätze)

### Zone 2 — Smart Preload (~2-5K Tokens)

Wird per Tool Call geladen, wenn der Agent es für nötig hält:

- Curriculum Chunks (pgvector-Suche, Top 5)
- Good-Practice-Beispiele
- Zuvor generierte Materialien (ähnliches Thema)

### Zone 3 — On-Demand (variabel)

Wird nur bei expliziter Anfrage oder Tool-Aufruf geladen:

- Web-Recherche (Brave API)
- Vollständige Konversationshistorie
- Tiefe Lehrplan-Analyse (mehrere Chunks, cross-referencing)

```
Kosten/Latenz ──────────────────────────────────────────►

  Zone 1              Zone 2                Zone 3
  ┌──────────┐       ┌──────────────┐      ┌──────────┐
  │ Profil   │       │ Curriculum   │      │ Web-     │
  │ Memories │       │ Chunks       │      │ Recherche│
  │ Prefs    │       │ Good Practic.│      │ Deep     │
  │ Wissens- │       │ Alte Materi. │      │ Analysis │
  │ karte    │       │              │      │          │
  └──────────┘       └──────────────┘      └──────────┘
  Immer geladen       Bei Bedarf (Tool)     Explizit angefordert
  ~2K Tokens          ~2-5K Tokens          variabel
```

---

## Datenbank

### Schema (Supabase PostgreSQL + pgvector)

```sql
-- Lehrer & Profile
teachers         (id UUID PK, name TEXT, password TEXT, created_at TIMESTAMPTZ)
user_profiles    (id UUID PK FK→teachers, bundesland TEXT, schulform TEXT,
                  faecher TEXT[], jahrgaenge INT[])

-- Konversationen & Nachrichten
conversations    (id UUID PK, user_id UUID FK→teachers, title TEXT,
                  created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)
messages         (id UUID PK, conversation_id UUID FK→conversations,
                  role TEXT, content TEXT, metadata JSONB,
                  created_at TIMESTAMPTZ)

-- Memory-System
user_memories    (id UUID PK, user_id UUID FK→teachers,
                  scope TEXT,      -- 'self' | 'class' | 'school' | 'student'
                  category TEXT,   -- z.B. 'preference', 'observation'
                  key TEXT,        -- z.B. '10a_probleme'
                  value TEXT,      -- Frei-Text
                  importance FLOAT,
                  updated_at TIMESTAMPTZ)

-- Curriculum RAG
curriculum_chunks (id UUID PK, curriculum_id UUID, teacher_id UUID,
                   fach TEXT, bundesland TEXT, section_title TEXT,
                   text TEXT, embedding VECTOR(1536),
                   created_at TIMESTAMPTZ)

-- Session-Logs
session_logs     (id UUID PK, conversation_id UUID, summary TEXT,
                  knowledge_extracts JSONB, created_at TIMESTAMPTZ)

-- H5P Übungen
exercise_pages   (id UUID PK, teacher_id UUID FK→teachers,
                  title TEXT, access_code TEXT UNIQUE,
                  created_at TIMESTAMPTZ)
exercises        (id UUID PK, page_id UUID FK→exercise_pages,
                  h5p_content JSONB, h5p_type TEXT,
                  title TEXT, created_at TIMESTAMPTZ)

-- Todos
todos            (id UUID PK, teacher_id UUID FK→teachers,
                  text TEXT, done BOOLEAN DEFAULT false,
                  due_date DATE, priority TEXT DEFAULT 'normal',
                  completed_at TIMESTAMPTZ,
                  created_at TIMESTAMPTZ)

-- Abstimmungen
polls            (id UUID PK, teacher_id UUID FK→teachers,
                  question TEXT, options JSONB,   -- TEXT[]
                  votes JSONB,                    -- {option: count}
                  access_code TEXT UNIQUE, active BOOLEAN DEFAULT true,
                  created_at TIMESTAMPTZ)
```

### Indizes

```sql
-- Vektorsuche (Cosine Similarity)
CREATE INDEX idx_chunks_embedding
  ON curriculum_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Nachrichten nach Konversation + Zeit
CREATE INDEX idx_messages_conversation
  ON messages (conversation_id, created_at);

-- Konversationen nach User + letzte Aktualisierung
CREATE INDEX idx_conversations_user
  ON conversations (user_id, updated_at DESC);

-- Unique Access Code für Schüler
CREATE UNIQUE INDEX idx_exercise_pages_code
  ON exercise_pages (access_code);
```

---

## API-Routen

### Authentifizierung

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `POST` | `/api/auth/login` | Passwort-Login → `teacher_id` |

### Chat

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `POST` | `/api/chat/send` | Nachricht senden, Agent-Antwort erhalten |
| `GET` | `/api/chat/history?conversation_id=` | Nachrichten einer Konversation |
| `GET` | `/api/chat/conversations` | Alle Konversationen des Lehrers |
| `DELETE` | `/api/chat/conversations/:id` | Konversation löschen |

### Curriculum

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `POST` | `/api/curriculum/upload` | PDF hochladen → Chunking → Embeddings |
| `GET` | `/api/curriculum/list` | Hochgeladene Lehrpläne auflisten |
| `DELETE` | `/api/curriculum/:id` | Lehrplan entfernen |

### Profil

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/profile/:teacher_id` | Profil abrufen |
| `PATCH` | `/api/profile/:teacher_id` | Profil aktualisieren |
| `GET` | `/api/suggestions` | Profilbasierte Vorschläge |

### Materialien

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/materials/:id/download` | Generiertes Material (DOCX) herunterladen |

### H5P Übungen

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `POST` | `/api/exercises/generate` | Übung generieren |
| `GET` | `/api/exercises/pages` | Übungsseiten des Lehrers |
| `POST` | `/api/exercises/pages` | Neue Übungsseite erstellen |

### Todos

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/todos` | Alle Todos auflisten (Filter: `?done=false`) |
| `POST` | `/api/todos` | Neues Todo erstellen |
| `PATCH` | `/api/todos/:id` | Todo aktualisieren (Text, Status, Datum) |
| `DELETE` | `/api/todos/:id` | Todo löschen |

### Bilder

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/images/:id` | Generiertes Bild ausliefern |

### Sprache

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `POST` | `/api/transcribe` | Audio-Datei transkribieren (Whisper) |

### Öffentlich (Schüler-Zugang)

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/public/pages/:code` | Übungen per Zugangscode laden |
| `GET` | `/api/public/exercises/:id` | H5P-Content für Player |
| `GET` | `/api/public/poll/:code` | Abstimmung laden |
| `POST` | `/api/public/poll/:code/vote` | Stimme abgeben |

### System

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| `GET` | `/api/health` | Health-Check |
| `POST` | `/api/admin/memory-cleanup` | Memory-Bereinigung |

---

## Deployment

### Produktions-Setup

```
                    ┌─────────────────────┐
                    │   Cloudflare Pages   │
                    │   (React Frontend)   │
                    │   Auto-Deploy: Git   │
                    └─────────┬───────────┘
                              │ /api/*
                              ▼
                    ┌─────────────────────┐
                    │   Render.com        │
                    │   (FastAPI Backend)  │
                    │   Python 3.12       │
                    │   render.yaml       │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │ Supabase │ │Anthropic │ │ Brave  │ │ Gemini │ │Pixabay │
  │ Cloud    │ │ API      │ │ Search │ │ Imagen │ │  API   │
  │PostgreSQL│ │          │ │  API   │ │  API   │ │        │
  │+pgvector │ │          │ │        │ │        │ │        │
  │+Storage  │ └──────────┘ └────────┘ └────────┘ └────────┘
  └──────────┘
                    │
             ┌──────┴──────┐
             │ OpenAI API  │
             │Embeddings + │
             │  Whisper    │
             └─────────────┘
```

### Lokale Entwicklung

```bash
# Backend
cd backend
cp .env.example .env   # Credentials eintragen
uv sync
uv run uvicorn app.main:app --port 8000 --reload

# Frontend (separates Terminal)
cd frontend
npm install
npm run dev            # Vite Dev-Server mit Proxy → localhost:8000
```

Vite-Proxy-Konfiguration (`vite.config.ts`):
```typescript
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

---

## Verzeichnisstruktur

```
eduhu-assistant/
├── frontend/                # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── components/      # Chat, Layout, Exercises
│   │   ├── pages/           # Route-Seiten
│   │   ├── hooks/           # useChat (zentraler State)
│   │   └── lib/             # API-Client, Auth, Types
│   ├── public/              # Static Assets + H5P-Bibliotheken
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                 # FastAPI + Python 3.12
│   ├── app/
│   │   ├── agents/          # Pydantic AI Agents (Multi-Agent)
│   │   ├── routers/         # REST-Endpunkte
│   │   ├── services/        # Business-Logik
│   │   ├── main.py          # App-Setup
│   │   ├── config.py        # Settings (.env)
│   │   ├── db.py            # Supabase-Client
│   │   └── models.py        # Pydantic-Models
│   ├── curricula/           # Sample-Lehrpläne
│   └── pyproject.toml
│
├── supabase/
│   └── migrations/          # SQL-Migrationen
│
└── docs/                    # Dokumentation
    ├── ARCHITECTURE.md      # ← Dieses Dokument
    ├── EDUHU-ASSISTANT-BRIEFING.md
    ├── AGENT-ARCHITEKTUR-V2.md
    ├── EDUHU-DESIGN-SYSTEM.md
    ├── H5P-FEATURE-PLAN.md
    ├── JOBS-TO-BE-DONE.md
    ├── MATERIAL-AGENT-RESEARCH.md
    ├── QA-CHECKLIST.md
    └── WISSENSKARTE-KONZEPT.md
```

---

## Weiterführende Docs

| Dokument | Inhalt |
|----------|--------|
| [EDUHU-ASSISTANT-BRIEFING.md](./EDUHU-ASSISTANT-BRIEFING.md) | Produktvision, UI-Specs, API-Verträge |
| [AGENT-ARCHITEKTUR-V2.md](./AGENT-ARCHITEKTUR-V2.md) | Multi-Turn Agents, Wissenskarte, State Machine |
| [EDUHU-DESIGN-SYSTEM.md](./EDUHU-DESIGN-SYSTEM.md) | Farben, Typografie, Komponenten-Specs |
| [H5P-FEATURE-PLAN.md](./H5P-FEATURE-PLAN.md) | Interaktive Übungen, Architektur, Datenmodell |
| [JOBS-TO-BE-DONE.md](./JOBS-TO-BE-DONE.md) | User Needs aus 5 Perspektiven |
| [MATERIAL-AGENT-RESEARCH.md](./MATERIAL-AGENT-RESEARCH.md) | Material-Generierung, AFB-Taxonomie |
| [WISSENSKARTE-KONZEPT.md](./WISSENSKARTE-KONZEPT.md) | Knowledge-Map-Struktur, Aggregation |
| [QA-CHECKLIST.md](./QA-CHECKLIST.md) | Testszenarien, Akzeptanzkriterien |
| [OVERNIGHT-PLAN.md](./OVERNIGHT-PLAN.md) | Overnight-Entwicklungsplan |
