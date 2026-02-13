# eduhu Assistant — Frontend Developer Briefing

> **Version:** 1.0 — 13. Februar 2026
> **Status:** MVP / Prototyp
> **Auftraggeber:** eduhu GmbH

---

## 1. Produktvision

**eduhu** ist ein KI-Assistent für Lehrkräfte an deutschen Schulen. Der Assistent hilft bei täglichen Aufgaben: Materialerstellung, Dokumentation, Unterrichtsplanung, Elternkommunikation.

Das Kernprodukt ist ein **Chat-Interface** — Lehrer:innen sprechen mit der KI-Eule wie mit einem kompetenten Kollegen. Die Eule versteht den Schulkontext, kennt Lehrpläne und generiert direkt nutzbare Materialien.

### Zielgruppe
- Lehrkräfte an deutschen Schulen (Klasse 1-13)
- Alter: 25-65 Jahre
- Tech-Affinität: mittel (WhatsApp ja, Terminal nein)
- Hauptdevice: Laptop (Schule), Smartphone (unterwegs)

### Kernversprechen
> "Dein KI-Kollege im Lehrerzimmer — versteht was du brauchst, liefert was du nutzen kannst."

---

## 2. Scope & Phasen

### Phase 1 — MVP (dieses Briefing)
- **Chat-Interface** als einziger Screen
- Login (einfache Passwort-Auth)
- Nachrichten senden & empfangen (Text, Dateien, Bilder)
- KI-Antworten mit Markdown-Rendering
- Auswahl-Chips für strukturierte Interaktion
- Responsive (Desktop + Mobile)

### Phase 2 — Three-Tab Layout (später)
- **Home:** Personalisierte Empfehlungen, Quick-Actions, Tagesübersicht
- **Chat:** Das bestehende Chat-Interface
- **Bibliothek:** Generierte Materialien, Vorlagen, History

### Phase 3 — Erweiterungen (Zukunft)
- Profil-Sync (Fächer, Klassen, Lehrplan)
- Datei-Management (Upload & generierte Dokumente)
- Kollaboration (Material mit Kolleg:innen teilen)

**Dieses Briefing deckt Phase 1 ab.** Das Design soll aber so angelegt sein, dass Phase 2+3 ohne Rewrite möglich sind.

---

## 3. Tech Stack

| Bereich | Technologie | Bemerkung |
|---|---|---|
| **Framework** | Vite + React 19 + TypeScript (strict) | Schneller Build, modernes React |
| **Styling** | Tailwind CSS 4 | Utility-first, Design-Tokens über Config |
| **UI-Bibliothek** | shadcn/ui (optional) | Nur als Basis, stark angepasst |
| **State** | React State + Context | Kein Redux — App ist nicht komplex genug |
| **Routing** | React Router v7 | Für spätere Tab-Navigation |
| **Markdown** | react-markdown + rehype/remark | Für KI-Antworten |
| **Backend** | Cloudflare Workers / Functions | Serverless, Edge-basiert |
| **Datenbank** | Supabase (PostgreSQL) | Auth, Chat-History, Materialien |
| **KI-API** | Anthropic Claude (via Backend-Proxy) | Nie direkt vom Frontend! |
| **Deployment** | Cloudflare Pages | Auto-Deploy aus Git |
| **Tests** | Playwright (E2E) + Vitest (Unit) | E2E ist Pflicht |

### Projekt-Setup
```bash
npm create vite@latest eduhu-assistant -- --template react-ts
cd eduhu-assistant
npm install tailwindcss @tailwindcss/vite react-router-dom react-markdown
npm install -D playwright @playwright/test
```

### Verzeichnisstruktur
```
eduhu-assistant/
├── src/
│   ├── components/       # Wiederverwendbare UI-Komponenten
│   │   ├── chat/         # Chat-spezifische Komponenten
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChipSelector.tsx
│   │   │   ├── FilePreview.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Header.tsx
│   │   │   └── BottomNav.tsx    # Vorbereitet für Phase 2
│   │   └── ui/           # Basis-Komponenten (Button, Input, Card)
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── lib/
│   │   ├── api.ts        # Backend-API Calls
│   │   ├── auth.ts       # Login/Session
│   │   └── types.ts      # TypeScript Interfaces
│   ├── hooks/
│   │   ├── useChat.ts    # Chat-State & Logik
│   │   └── useAuth.ts    # Auth-State
│   ├── App.tsx
│   ├── index.css         # Tailwind + globale Styles
│   └── main.tsx
├── functions/            # Cloudflare Workers (Backend)
│   ├── api/
│   │   ├── auth/
│   │   │   └── login.ts
│   │   └── chat/
│   │       ├── send.ts
│   │       └── history.ts
│   └── lib/
│       └── api-helpers.ts
├── public/
│   ├── favicon.svg       # eduhu Eule
│   └── owl-avatar.svg    # Chat-Avatar
├── supabase/
│   └── migrations/
│       └── 001_initial.sql
├── tests/
│   └── e2e/
├── docs/
│   └── DESIGN-SYSTEM.md
├── tailwind.config.ts
├── playwright.config.ts
└── package.json
```

---

## 4. Design System

Vollständige Referenz: **`docs/EDUHU-DESIGN-SYSTEM.md`** (separat)

### Kurzfassung

**Farbpalette:**
- Primary: `#C8552D` (Burnt Orange)
- Text: `#2D2018` (Dunkelbraun) — nie reines Schwarz
- Background: `#F5F0EB` (Warmes Creme)
- Cards: `#FFFFFF` mit Shadow statt Border
- Soft/Hover: `#FADDD0` (Helles Peach)

**Typografie:**
- Font: Inter (oder DM Sans)
- Headlines: Bold/Black, Braun
- Body: Regular, 14-16px
- Section Labels: 12px, UPPERCASE, Orange, letter-spacing 0.1em

**Radius:** Cards 16px, Buttons 14px, Inputs 14px
**Shadows:** `0 2px 8px rgba(0,0,0,0.06)` für Cards

**Ton:** Warm, einladend, professionell. Nie kalt oder steril.

### Tailwind Config
```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#C8552D',
          hover: '#A8461F',
          soft: '#FADDD0',
        },
        text: {
          strong: '#2D2018',
          DEFAULT: '#3A3530',
          secondary: '#6B6360',
          muted: '#9E9A96',
        },
        bg: {
          page: '#F5F0EB',
          card: '#FFFFFF',
          'card-dark': '#3A2E2A',
          subtle: '#F0EDEA',
        },
        border: {
          DEFAULT: '#D9D3CD',
          focus: '#C8552D',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
        btn: '14px',
        input: '14px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.06)',
        elevated: '0 4px 16px rgba(0,0,0,0.10)',
      },
    },
  },
  plugins: [],
} satisfies Config;
```

---

## 5. Screens & User Flows

### 5.1 Login

```
┌─────────────────────────────┐
│         [eduhu Logo]         │
│        🦉 + "eduhu"         │
│                              │
│   ┌───────────────────────┐  │
│   │ Dein Passwort          │  │
│   └───────────────────────┘  │
│                              │
│   ┌───────────────────────┐  │
│   │     Anmelden    →     │  │
│   └───────────────────────┘  │
│                              │
│   Powered by eduhu GmbH      │
└─────────────────────────────┘
```

**Verhalten:**
- Passwort-Eingabe → POST `/api/auth/login`
- Erfolg: Redirect zu `/chat`
- Fehler: Inline-Fehlermeldung unter dem Input
- Session in `localStorage` (teacher_id, name, token)
- Kein "Registrieren" — Accounts werden vom Admin angelegt

### 5.2 Chat (Hauptscreen)

```
┌──────────────────────────────────────┐
│  🦉 eduhu          [Lehrer-Name] ☰  │  ← Header
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────┐        │
│  │ 🦉 Hallo Michelle! 👋    │        │  ← KI-Nachricht (links)
│  │ Was kann ich heute für    │        │
│  │ dich tun?                 │        │
│  └──────────────────────────┘        │
│                                      │
│  ┌─────────┐ ┌──────────────┐       │  ← Suggestion Chips
│  │ 📝 Quiz │ │ 📋 Doku      │       │
│  └─────────┘ └──────────────┘       │
│  ┌─────────────────┐ ┌──────┐       │
│  │ 📖 Zusammenfass. │ │ 💡   │       │
│  └─────────────────┘ └──────┘       │
│                                      │
│         ┌──────────────────────┐     │
│         │ Erstelle ein Quiz    │     │  ← User-Nachricht (rechts)
│         │ für Mathe Klasse 8a  │     │
│         └──────────────────────┘     │
│                                      │
│  ┌──────────────────────────┐        │
│  │ 🦉 Klar! Zu welchem      │        │
│  │ Thema? Hier ein paar     │        │
│  │ Vorschläge:               │        │
│  │                           │        │
│  │ ┌────────┐ ┌───────────┐ │        │  ← Inline-Chips
│  │ │Brüche  │ │Geometrie  │ │        │
│  │ └────────┘ └───────────┘ │        │
│  │ ┌────────────┐           │        │
│  │ │Prozentrechn.│          │        │
│  │ └────────────┘           │        │
│  └──────────────────────────┘        │
│                                      │
│  ┌──────────────────────────┐        │
│  │ 🦉 Hier ist dein Quiz:   │        │
│  │                           │        │
│  │ ┌──────────────────────┐ │        │  ← Datei-Attachment
│  │ │ 📄 Quiz_Brüche_8a.pdf│ │        │
│  │ │    ⬇️ Herunterladen   │ │        │
│  │ └──────────────────────┘ │        │
│  │                           │        │
│  │ Soll ich Änderungen      │        │
│  │ machen?                   │        │
│  └──────────────────────────┘        │
│                                      │
├──────────────────────────────────────┤
│ ┌──────────────────────────┐  📎 ⬆  │  ← Input-Leiste
│ │ Nachricht eingeben...     │        │
│ └──────────────────────────┘        │
└──────────────────────────────────────┘
```

---

## 6. Komponenten-Spezifikation

### 6.1 ChatMessage

Zwei Varianten: **AI** (links) und **User** (rechts).

```tsx
interface ChatMessage {
  id: string;
  role: 'assistant' | 'user';
  content: string;           // Markdown-fähig
  attachments?: Attachment[];
  chips?: Chip[];            // Auswahl-Optionen
  timestamp: string;         // ISO 8601
}

interface Attachment {
  type: 'file' | 'image';
  url: string;
  name: string;
  mimeType: string;
  size?: number;             // bytes
}

interface Chip {
  id: string;
  label: string;
  icon?: string;             // Emoji
}
```

**AI-Nachricht (links):**
- Avatar: Eule-Icon (32x32px), rund
- Bubble: `bg-card`, `shadow-card`, `rounded-card`
- Max-Width: 80% (Desktop), 90% (Mobile)
- Text: Markdown gerendert (Fettschrift, Listen, Code, Links)
- Attachments: File-Card innerhalb der Bubble
- Chips: Horizontal scrollbar, unterhalb des Texts

**User-Nachricht (rechts):**
- Keine Avatar
- Bubble: `bg-primary`, Text weiß, `rounded-card`
- Max-Width: 70%
- Nur Plain-Text (kein Markdown nötig)

**Zeitstempel:**
- Unter der Bubble, `text-muted`, `text-xs`
- Format: "14:32" (heute) oder "Mo, 14:32" (diese Woche) oder "12. Feb, 14:32"

### 6.2 ChatInput

```
┌────────────────────────────────────┐
│ 📎  │ Nachricht eingeben...    │ ⬆ │
└────────────────────────────────────┘
```

- **Textarea** (nicht Input): Wächst mit Inhalt, max 5 Zeilen
- **Attachment-Button** (📎): Öffnet Datei-Picker (PDF, Bilder, Dokumente)
- **Send-Button** (⬆): Primary-Farbe, nur aktiv wenn Input nicht leer
- **Enter** sendet, **Shift+Enter** neue Zeile
- **Disabled** während KI antwortet (mit Typing-Indicator)

### 6.3 ChipSelector

Horizontale Liste von auswählbaren Optionen.

```tsx
interface ChipSelectorProps {
  chips: Chip[];
  onSelect: (chip: Chip) => void;
  layout?: 'wrap' | 'scroll';  // wrap: Umbruch, scroll: horizontal scrollbar
}
```

**Styling:**
- Background: `bg-card` oder `bg-bg-subtle`
- Border: `1.5px solid border-DEFAULT`
- Border-Radius: `rounded-btn` (14px)
- Padding: `8px 16px`
- Text: `text-sm font-medium text-text-strong`
- Hover: `bg-primary-soft border-primary`
- Active/Selected: `bg-primary text-white`
- Optional Emoji-Icon links vom Label

**Verhalten:**
- Klick sendet den Chip-Text als User-Nachricht
- Chips verschwinden nach Auswahl (einmalig)
- Können auch persistente Actions sein (z.B. "Neues Thema")

### 6.4 TypingIndicator

Zeigt an, dass die KI "denkt".

```
┌──────────────────┐
│ 🦉  ● ● ●        │
└──────────────────┘
```

- Drei pulsierende Punkte in Primary-Farbe
- Animation: Sequential fade (0.4s delay zwischen Dots)
- Gleiche Bubble-Styles wie AI-Nachricht
- Erscheint sofort nach User-Nachricht
- Verschwindet wenn AI-Antwort kommt

### 6.5 FilePreview

Innerhalb einer AI-Nachricht.

```
┌──────────────────────────┐
│ 📄  Quiz_Brüche_8a.pdf   │
│     2.4 MB · PDF          │
│                           │
│  ┌─────────────────────┐  │
│  │  ⬇️ Herunterladen    │  │
│  └─────────────────────┘  │
└──────────────────────────┘
```

- Card-in-Card: `bg-bg-subtle`, `rounded-badge` (8px)
- File-Icon basierend auf MIME-Type (📄 PDF, 🖼 Bild, 📊 Excel)
- Dateiname: `font-medium`, abgeschnitten mit Ellipsis wenn zu lang
- Größe + Typ: `text-xs text-muted`
- Download-Button: Ghost-Style
- Bilder: Inline-Preview (max-height 300px, klickbar für Fullscreen)

### 6.6 Header

```
┌──────────────────────────────────────┐
│  🦉 eduhu          Michelle B.  ☰   │
└──────────────────────────────────────┘
```

- Links: Eule-Logo + "eduhu" Wordmark
- Rechts: Lehrer-Name (abgekürzt) + Hamburger-Menü
- Menü enthält: "Neuer Chat", "Chat-Verlauf", "Abmelden"
- Sticky top, `bg-card`, `shadow-subtle`
- Height: 56px (Mobile), 64px (Desktop)

### 6.7 AppShell

Wrapper für die gesamte App.

```tsx
function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-dvh flex-col bg-bg-page">
      <Header />
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
      {/* Phase 2: <BottomNav /> */}
    </div>
  );
}
```

- Nutzt `h-dvh` (dynamic viewport height) für Mobile-Browser
- Main-Bereich füllt verfügbaren Platz
- BottomNav ist vorbereitet aber auskommentiert

---

## 7. API-Spezifikation

### 7.1 Auth

**POST `/api/auth/login`**
```json
// Request
{ "password": "geheim123" }

// Response 200
{ 
  "teacher_id": "uuid",
  "name": "Michelle Berger",
  "token": "session-token"
}

// Response 401
{ "error": "Falsches Passwort." }
```

### 7.2 Chat

**POST `/api/chat/send`**
```json
// Request
{
  "message": "Erstelle ein Quiz für Mathe Klasse 8a",
  "conversation_id": "uuid",       // optional, null = neuer Chat
  "attachments": [                  // optional
    { "name": "aufgabe.pdf", "data": "base64..." }
  ]
}

// Response 200 (Streaming via ReadableStream)
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "Klar! Zu welchem Thema?",
    "chips": [
      { "id": "1", "label": "Brüche", "icon": "🔢" },
      { "id": "2", "label": "Geometrie", "icon": "📐" }
    ],
    "attachments": []
  }
}
```

**GET `/api/chat/history?conversation_id=uuid`**
```json
// Response 200
{
  "conversation_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Hallo Michelle! 👋",
      "timestamp": "2026-02-13T14:32:00Z",
      "chips": [],
      "attachments": []
    }
  ]
}
```

**GET `/api/chat/conversations`**
```json
// Response 200
[
  {
    "id": "uuid",
    "title": "Quiz Mathe 8a",        // Auto-generiert aus erstem Message
    "last_message": "Hier ist dein Quiz!",
    "updated_at": "2026-02-13T14:35:00Z"
  }
]
```

### 7.3 Dateien

**GET `/api/files/:id`**
- Gibt die Datei zum Download zurück
- Auth-Header erforderlich

---

## 8. Datenmodell (Supabase)

```sql
-- Lehrer
CREATE TABLE teachers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  password TEXT NOT NULL,  -- Phase 1: Plaintext, später: bcrypt
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Konversationen
CREATE TABLE conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  teacher_id UUID REFERENCES teachers(id) ON DELETE CASCADE,
  title TEXT,              -- Auto-generiert
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Nachrichten
CREATE TABLE messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  chips JSONB,             -- Auswahl-Optionen (nullable)
  attachments JSONB,       -- Datei-Referenzen (nullable)
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Dateien
CREATE TABLE files (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  teacher_id UUID REFERENCES teachers(id) ON DELETE CASCADE,
  conversation_id UUID REFERENCES conversations(id),
  name TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  size_bytes INTEGER,
  storage_path TEXT NOT NULL,  -- Supabase Storage Pfad
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indizes
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_conversations_teacher ON conversations(teacher_id, updated_at DESC);
CREATE INDEX idx_files_conversation ON files(conversation_id);

-- RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Für den Prototyp: Alles erlauben (später einschränken)
CREATE POLICY "allow_all" ON conversations FOR ALL USING (true);
CREATE POLICY "allow_all" ON messages FOR ALL USING (true);
CREATE POLICY "allow_all" ON files FOR ALL USING (true);
```

---

## 9. Interaktionsdetails

### 9.1 Chat-Flow

```
User öffnet App
  → Login (wenn keine Session)
  → Chat-Screen
    → Eule begrüßt: "Hallo [Name]! 👋 Was kann ich heute für dich tun?"
    → Suggestion-Chips erscheinen:
        📝 Quiz erstellen
        📋 Dokumentation
        📖 Stunde zusammenfassen
        💡 Ideen für Unterricht
    → User tippt oder wählt Chip
    → Typing-Indicator erscheint
    → KI antwortet (ggf. mit Rückfragen + Chips)
    → Bei Datei-Generierung: Datei-Preview in Bubble
    → User kann weiter chatten oder neuen Chat starten
```

### 9.2 Streaming-Antworten

KI-Antworten sollen **gestreamt** werden (Wort für Wort erscheinen):

- Backend nutzt `ReadableStream` / Server-Sent Events
- Frontend rendert inkrementell (wie ChatGPT)
- Markdown wird erst gerendert wenn ein Absatz komplett ist
- Chips + Attachments erscheinen am Ende des Streams
- "Stop"-Button während des Streamings (optional für MVP)

### 9.3 Datei-Upload

- Klick auf 📎 → Native File-Picker
- Akzeptiert: PDF, JPG, PNG, DOCX (max 10MB)
- Upload-Fortschritt als Progress-Bar im Input-Bereich
- Nach Upload: Kleine Preview neben dem Textfeld
- Datei wird mit der nächsten Nachricht gesendet

### 9.4 Fehlerbehandlung

| Situation | Verhalten |
|---|---|
| KI-Timeout (>30s) | "Das dauert gerade etwas länger..." + Retry-Button |
| API-Fehler (500) | "Da ist etwas schiefgelaufen. Versuch's nochmal." in AI-Bubble |
| Offline | Banner oben: "Keine Internetverbindung" + Input deaktiviert |
| Session abgelaufen | Redirect zu Login mit Hinweis |
| Datei zu groß | Toast: "Datei ist zu groß (max. 10 MB)" |

---

## 10. Responsive Breakpoints

| Breakpoint | Breite | Layout-Änderungen |
|---|---|---|
| **Mobile** | < 640px | Volle Breite, kompaktere Bubbles, Chips scrollen horizontal |
| **Tablet** | 640-1024px | Max-Width 720px, zentriert |
| **Desktop** | > 1024px | Max-Width 800px, zentriert, mehr Whitespace |

Der Chat soll nie die volle Bildschirmbreite nutzen (auf Desktop) — maximal 800px, zentriert, mit warmem Hintergrund drumherum.

---

## 11. Animationen & Micro-Interactions

| Element | Animation | Dauer |
|---|---|---|
| Nachricht erscheint | Fade-in + slide-up (8px) | 200ms ease-out |
| Chips erscheinen | Staggered fade-in (50ms delay pro Chip) | 150ms each |
| Typing-Indicator | Pulse-Animation der 3 Dots | 1.2s infinite |
| Send-Button | Scale 0.95 on press | 100ms |
| Neue Nachricht (scroll) | Smooth scroll to bottom | 300ms |
| Datei-Upload | Progress-Bar fill | Real-time |
| Fehler-Toast | Slide-in von oben | 200ms, auto-hide 5s |

---

## 12. Eule (Maskottchen) — Richtlinien

Die Eule ist das Gesicht von eduhu. Sie erscheint als:

1. **Chat-Avatar:** 32x32px, rund, neben jeder AI-Nachricht
2. **Begrüßung:** Im ersten Message mit Emoji 👋
3. **Typing-Indicator:** Eule-Avatar + pulsierende Dots
4. **Login-Screen:** Größer (80x80px), über dem Login-Formular
5. **Leerer State:** "Frag mich etwas!" mit Eule-Illustration

**Persönlichkeit der Eule:**
- Freundlich und kompetent (nie herablassend)
- Spricht Lehrer:innen auf Augenhöhe an
- Nutzt gelegentlich Emojis (nicht übertreiben)
- Gibt konkrete, nutzbare Antworten (kein Gelaber)
- Fragt nach wenn unklar, statt zu raten

**Sprache:**
- Deutsch, Sie/Du je nach Lehrer-Präferenz (Standard: Du)
- Kurze Sätze, klare Struktur
- Fachbegriffe erklärt wenn nötig

---

## 13. Akzeptanzkriterien (MVP)

### Must Have ✅
- [ ] Login mit Passwort → Chat-Screen
- [ ] Nachrichten senden (Text)
- [ ] KI-Antworten empfangen und darstellen (Markdown)
- [ ] Suggestion-Chips (initial + inline)
- [ ] Typing-Indicator während KI denkt
- [ ] Chat-Verlauf bleibt erhalten (Supabase)
- [ ] Responsive (Mobile + Desktop)
- [ ] Eule als Avatar
- [ ] Fehlerbehandlung (Offline, Timeout, API-Error)
- [ ] Auto-Scroll bei neuen Nachrichten

### Should Have 🟡
- [ ] Datei-Upload (📎) und Datei-Preview in Antworten
- [ ] Streaming-Antworten (Wort für Wort)
- [ ] "Neuer Chat" starten
- [ ] Chat-History-Liste (Hamburger-Menü)
- [ ] Keyboard-Shortcuts (Enter/Shift+Enter)

### Nice to Have 🔵
- [ ] Dark Mode
- [ ] "Stop"-Button bei Streaming
- [ ] Nachrichten kopieren
- [ ] Code-Syntax-Highlighting in Antworten
- [ ] Sound bei neuer Nachricht

---

## 14. Brand Assets

Benötigte Assets (vom Design-Team oder zu erstellen):

| Asset | Format | Größe | Status |
|---|---|---|---|
| eduhu Logo (horizontal) | SVG | variabel | ✅ Vorhanden (Deck) |
| Eule-Avatar (Chat) | SVG | 32x32, 64x64 | ❌ Zu erstellen |
| Eule-Illustration (Login) | SVG | 80x80, 160x160 | ❌ Zu erstellen |
| Favicon | SVG + ICO | 32x32 | ❌ Zu erstellen |
| Open Graph Image | PNG | 1200x630 | ❌ Zu erstellen |
| Font: Inter | WOFF2 | — | ✅ Google Fonts |

---

## 15. Deployment & Workflow

### Git
- **Repo:** Neues GitLab-Repo (oder GitHub)
- **Branch-Strategie:** `main` = Production, Feature-Branches für neue Features
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`)

### CI/CD
- Cloudflare Pages: Auto-Deploy bei Push auf `main`
- Build: `npm run build` (Vite)
- Preview: Jeder Branch bekommt eine Preview-URL

### Environment Variables (Cloudflare Dashboard)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
```

### Lokale Entwicklung
```bash
# Frontend
npm run dev              # Vite auf :5173

# Backend (Cloudflare Workers)
npx wrangler pages dev   # auf :8788

# Beides zusammen
npm run dev:full         # package.json Script
```

---

## 16. Zeitschätzung

| Phase | Aufwand | Beschreibung |
|---|---|---|
| Setup & Scaffolding | 1 Tag | Projekt, Tailwind, Router, Supabase |
| Login | 0.5 Tage | Auth-Flow, Session |
| Chat UI (statisch) | 2 Tage | Messages, Input, Chips, Layout |
| Backend API | 2 Tage | Chat-Endpoints, Claude-Integration |
| Streaming | 1 Tag | SSE/ReadableStream |
| Datei-Upload/Download | 1 Tag | Upload, Preview, Supabase Storage |
| Polish & Responsive | 1 Tag | Animationen, Edge-Cases, Mobile |
| Testing | 1 Tag | Playwright E2E + manuelle Tests |
| **Gesamt MVP** | **~8-10 Tage** | |

---

## Anhang

### A. Referenzen
- [eduhu Design System](./EDUHU-DESIGN-SYSTEM.md)
- [Vite Docs](https://vitejs.dev)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/functions/)
- [Supabase JS Client](https://supabase.com/docs/reference/javascript)
- [react-markdown](https://github.com/remarkjs/react-markdown)

### B. Kontakt
- **Steffen Brill** — Gründer & Product
- **Claudius 🦑** — Tech Lead & KI-Orchestrierung
