# QA-Checkliste & Testplan — eduhu-assistant

> **Zweck:** Diese Checkliste ist für einen externen QA-Agenten. Er soll jeden Punkt systematisch prüfen, Bugs dokumentieren und Fixes vorschlagen. Die Liste basiert auf einer gründlichen Codeanalyse und bekannten Qualitätsproblemen von KI-generiertem Code.

---

## Inhaltsverzeichnis

1. [Bereits identifizierte Bugs (Sofort-Fixes)](#1-bereits-identifizierte-bugs-sofort-fixes)
2. [Startup & Konfiguration](#2-startup--konfiguration)
3. [Authentifizierung & Session](#3-authentifizierung--session)
4. [Chat-Workflow (Multi-Turn)](#4-chat-workflow-multi-turn)
5. [Conversation-Management](#5-conversation-management)
6. [Profil-Management](#6-profil-management)
7. [Curriculum Upload & RAG](#7-curriculum-upload--rag)
8. [Material-Generierung (Klausur & Differenzierung)](#8-material-generierung-klausur--differenzierung)
9. [Memory-System](#9-memory-system)
10. [Frontend-UI & UX](#10-frontend-ui--ux)
11. [API-Robustheit & Error-Handling](#11-api-robustheit--error-handling)
12. [Sicherheit](#12-sicherheit)
13. [Performance & Skalierung](#13-performance--skalierung)
14. [Datenintegrität & Edge Cases](#14-datenintegrität--edge-cases)
15. [Integration & End-to-End Workflows](#15-integration--end-to-end-workflows)

---

## 1. Bereits identifizierte Bugs (Sofort-Fixes)

Diese Bugs wurden bei der Code-Analyse gefunden und müssen zuerst behoben werden:

### BUG-001: DOCX-Download schlägt fehl nach DB-Fallback
- **Datei:** `backend/app/main.py:504-517`
- **Problem:** Wenn die Datei nicht auf der Disk liegt, wird `load_docx_from_db()` aufgerufen. Aber die Funktion schreibt die Datei zwar auf Disk, das Ergebnis `docx_bytes` wird aber ignoriert. Danach versucht `FileResponse(path=str(docx_path))` die Datei zu servieren — das funktioniert zwar nach dem Re-Cache, ABER: wenn `load_docx_from_db()` `None` zurückgibt, wird `HTTPException(404)` geworfen, und danach trotzdem `FileResponse` ausgeführt (kein `return` nach dem raise? — Nein, raise bricht ab, das ist OK). **Aber:** Wenn `load_docx_from_db` erfolgreich ist und die Datei schreibt, fehlt ein expliziter Check ob die Datei nach dem Schreiben wirklich existiert.
- **Prüfen:** Was passiert, wenn die DB-Verbindung funktioniert aber `docx_base64` leer/korrupt ist?

### BUG-002: `__import__("httpx")` Anti-Pattern
- **Datei:** `backend/app/main.py:383`
- **Problem:** `async with __import__("httpx").AsyncClient() as client:` — das ist ein unübliches Anti-Pattern. httpx wird oben im File gar nicht importiert (in der delete_curriculum-Funktion). Wenn httpx nicht installiert ist, gibt es einen kryptischen Fehler.
- **Fix:** Normalen Import `import httpx` am Dateianfang verwenden.

### BUG-003: Keine Autorisierungsprüfung bei Chat-History
- **Datei:** `backend/app/main.py:216-229`
- **Problem:** `GET /api/chat/history?conversation_id=xyz` — es wird NICHT geprüft, ob der anfragende User überhaupt Eigentümer der Conversation ist. Jeder der eine `conversation_id` kennt, kann die gesamte Chat-History lesen.
- **Schwere:** HOCH — Datenleck

### BUG-004: Keine Autorisierungsprüfung bei Conversation-Update
- **Datei:** `backend/app/main.py:280-289`
- **Problem:** `PATCH /api/chat/conversations/{id}` — kein `teacher_id`-Check. Jeder kann beliebige Conversations umbenennen.
- **Schwere:** MITTEL

### BUG-005: CORS Allow-All in Produktion
- **Datei:** `backend/app/main.py:77-83`
- **Problem:** `allow_origins=["*"]` — der Kommentar sagt "Restrict in production", aber es gibt keinen Mechanismus dafür. In Produktion können beliebige Domains API-Requests machen.
- **Schwere:** HOCH

### BUG-006: Passwort-Login ohne Hashing
- **Datei:** `backend/app/main.py:91-108`
- **Problem:** Passwörter werden als Klartext in der DB gespeichert und bei Login per `eq.{password}` verglichen. Kein Hashing, kein Salt.
- **Hinweis:** Für MVP/Demo evtl. OK, aber muss dokumentiert sein.

### BUG-007: httpx.AsyncClient wird bei jedem Request neu erstellt
- **Datei:** `backend/app/db.py` — jede Funktion erstellt `async with httpx.AsyncClient() as client:`
- **Problem:** TCP-Connection-Overhead bei jedem einzelnen DB-Call. Bei einem Chat-Request werden 5-8 DB-Calls gemacht = 5-8 neue TCP-Verbindungen.
- **Fix:** Shared AsyncClient als Singleton oder per-Request.

### BUG-008: Fire-and-Forget Task ohne Exception-Handling
- **Datei:** `backend/app/main.py:195-199`
- **Problem:** `asyncio.create_task(run_memory_agent(...))` — wenn der Task eine unhandled Exception wirft, wird diese silent verschluckt (Python loggt eine Warnung, aber der Task-Fehler kann leicht übersehen werden).
- **Fix:** Task-Error-Callback registrieren.

---

## 2. Startup & Konfiguration

### 2.1 Environment-Variablen
- [ ] **TEST:** Starte Backend OHNE `ANTHROPIC_API_KEY` → Erwartung: Klare Fehlermeldung, kein Crash
- [ ] **TEST:** Starte Backend OHNE `SUPABASE_URL` → Erwartung: Klare Fehlermeldung
- [ ] **TEST:** Starte Backend OHNE `OPENAI_API_KEY` → Erwartung: App startet, aber Curriculum-Upload gibt klaren Fehler
- [ ] **TEST:** Starte Backend OHNE `BRAVE_API_KEY` → Erwartung: App startet, Web-Search gibt Fallback
- [ ] **TEST:** Starte Backend mit ungültiger `SUPABASE_URL` (z.B. `https://invalid.supabase.co`) → Erwartung: Verständlicher Fehler
- [ ] **PRÜFEN:** Werden Secrets in Logs geloggt? Suche in `main.py`, `config.py`, `db.py` nach Log-Statements die Keys/Tokens ausgeben könnten.

### 2.2 Server-Start
- [ ] **TEST:** `uv run uvicorn app.main:app --reload` startet ohne Fehler
- [ ] **TEST:** `GET /api/health` gibt `{"status": "ok"}` zurück
- [ ] **TEST:** `GET /api/debug/imports` gibt `{"errors": [], "ok": true}` zurück
- [ ] **PRÜFEN:** Wird `eduhu.log` Datei erstellt? Wo? Relative Pfade können problematisch sein bei verschiedenen Arbeitsverzeichnissen.

### 2.3 Frontend-Start
- [ ] **TEST:** `npm run dev` startet ohne Fehler
- [ ] **TEST:** Frontend erreichbar unter `http://localhost:5173`
- [ ] **TEST:** `npm run build` erzeugt ohne Fehler ein dist-Verzeichnis
- [ ] **PRÜFEN:** Vite-Proxy konfiguriert? Werden `/api/*`-Requests an Backend weitergeleitet?

---

## 3. Authentifizierung & Session

### 3.1 Login-Flow
- [ ] **TEST: Gültiger Login** → Passwort `demo123` eingeben → Erwartung: Redirect zu `/chat`, Name "Demo-Lehrer" sichtbar
- [ ] **TEST: Ungültiger Login** → Passwort `falsch` eingeben → Erwartung: Fehlermeldung, KEIN Redirect
- [ ] **TEST: Leeres Passwort** → Leeres Feld absenden → Erwartung: Fehlermeldung, kein Server-Crash
- [ ] **TEST: Passwort mit Leerzeichen** → `" demo123 "` (mit Spaces) → Erwartung: Login funktioniert (`.strip()` ist implementiert)
- [ ] **TEST: SQL-Injection im Passwort** → `'; DROP TABLE teachers; --` → Erwartung: Kein Schaden (Supabase REST API parametrisiert, aber verifizieren!)
- [ ] **TEST: Extrem langes Passwort** → 10.000 Zeichen → Erwartung: Kein Crash, höchstens Fehler

### 3.2 Session-Persistenz
- [ ] **TEST:** Nach Login → Tab schließen → Tab wieder öffnen → Erwartung: Noch eingeloggt (localStorage)
- [ ] **TEST:** Nach Login → localStorage manuell löschen → `/chat` aufrufen → Erwartung: Redirect zu Login
- [ ] **TEST:** localStorage-Inhalt manipulieren (ungültige `teacher_id`) → Erwartung: API-Calls scheitern gracefully
- [ ] **PRÜFEN:** Gibt es Session-Expiry? (Antwort: Nein — ist das für MVP akzeptabel?)

### 3.3 Logout
- [ ] **TEST:** Logout-Button vorhanden und funktional?
- [ ] **TEST:** Nach Logout → `/chat` direkt aufrufen → Erwartung: Redirect zu Login
- [ ] **TEST:** Nach Logout → Browser-Back-Button → Erwartung: Kein Zugriff auf geschützte Seiten

### 3.4 Multi-User
- [ ] **TEST:** Login als "Demo-Lehrer" in Browser A, Login als "Christopher" in Browser B → Erwartung: Unabhängige Sessions, unterschiedliche Daten
- [ ] **TEST:** Zwei gleiche Logins in zwei Tabs → Erwartung: Kein Datenkonflikt

---

## 4. Chat-Workflow (Multi-Turn)

### 4.1 Erste Nachricht (Neue Conversation)
- [ ] **TEST:** Welcome-Screen sichtbar mit Eule-Emoji, Begrüßung und Suggestion-Chips
- [ ] **TEST:** Suggestion-Chips anklickbar → Nachricht wird gesendet
- [ ] **TEST:** Eigene Nachricht tippen → Senden → Typing-Indicator erscheint → KI-Antwort kommt → Typing-Indicator verschwindet
- [ ] **PRÜFEN:** Wird eine neue `conversation_id` zurückgegeben?
- [ ] **PRÜFEN:** Wird die Conversation in der Sidebar sichtbar?
- [ ] **PRÜFEN:** Wird der Conversation-Titel aus den ersten 80 Zeichen der Nachricht generiert?

### 4.2 Multi-Turn Gespräch (Kontext-Bewahrung)
- [ ] **TEST: 2-Turn Kontext:**
  1. Nachricht: "Ich unterrichte Physik in Klasse 10"
  2. Nachricht: "Erstelle eine Aufgabe zum letzten Thema"
  → Erwartung: KI erinnert sich an Physik/Klasse 10
- [ ] **TEST: 5-Turn Kontext:**
  1. "Ich plane eine Stunde zu Optik"
  2. "Was sind die Lernziele dafür?"
  3. "Erstelle 3 Aufgaben dazu"
  4. "Mach Aufgabe 2 schwieriger"
  5. "Fasse zusammen, was wir besprochen haben"
  → Erwartung: Kohärenter, sich aufbauender Dialog
- [ ] **TEST: 20+ Nachrichten Kontext:**
  → Prüfe: Funktioniert die Zusammenfassung (Summary-Agent)?
  → Prüfe: Werden nur die letzten 20 Nachrichten geladen?
  → Prüfe: Geht dabei wichtiger Kontext verloren?

### 4.3 Schnelles Senden
- [ ] **TEST:** Nachricht senden, bevor KI-Antwort kommt → Erwartung: Button ist disabled, keine Doppel-Requests
- [ ] **TEST:** Nachricht senden → sofort nächste → Erwartung: Ordentliche Reihenfolge
- [ ] **TEST:** 3 Nachrichten in schneller Folge → Erwartung: Keine Race-Condition, Nachrichten in richtiger Reihenfolge

### 4.4 Leere / Grenz-Nachrichten
- [ ] **TEST:** Leere Nachricht senden → Erwartung: Button disabled, kein API-Call
- [ ] **TEST:** Nur Leerzeichen senden → Erwartung: Wird als leer behandelt
- [ ] **TEST:** Sehr lange Nachricht (5000 Zeichen) → Erwartung: Wird gesendet, KI antwortet
- [ ] **TEST:** Nachricht mit Markdown (`**bold**`, `# heading`, Code-Blöcke) → Erwartung: KI versteht es, Antwort wird korrekt gerendert
- [ ] **TEST:** Nachricht mit Sonderzeichen (`äöü`, `€`, Emojis 🦉, `<script>alert(1)</script>`) → Erwartung: Korrekt verarbeitet, kein XSS

### 4.5 KI-Antwort-Rendering
- [ ] **TEST:** KI-Antwort mit Markdown → Erwartung: Fett, Kursiv, Listen, Code werden korrekt gerendert
- [ ] **TEST:** KI-Antwort mit Code-Block → Erwartung: Syntax-Highlighting (react-syntax-highlighter)
- [ ] **TEST:** KI-Antwort mit langer Tabelle → Erwartung: Scrollbar oder responsive
- [ ] **TEST:** KI-Antwort mit Links → Erwartung: Klickbar, öffnen in neuem Tab

### 4.6 Tool-Nutzung durch KI
- [ ] **TEST: Curriculum-Search:** "Was sagt der Lehrplan zu Optik?" (nachdem Curriculum hochgeladen)
  → Erwartung: KI nutzt `search_curriculum` Tool, zitiert Lehrplaninhalte
- [ ] **TEST: Web-Search:** "Welche aktuellen Methoden gibt es für Inklusion?"
  → Erwartung: KI nutzt `search_web` Tool, gibt aktuelle Infos
- [ ] **TEST: Remember:** "Merk dir, dass meine Klasse 10a Probleme mit Bruchrechnung hat"
  → Erwartung: KI nutzt `remember` Tool, bestätigt
  → Dann in neuem Gespräch: "Was weißt du über meine Klasse 10a?"
  → Erwartung: KI erinnert sich
- [ ] **TEST: Material via Chat:** "Erstelle eine Klassenarbeit zu Optik für Klasse 10, 45 Minuten"
  → Erwartung: KI nutzt `generate_material` Tool, gibt Download-Link
  → Download-Link anklicken → DOCX wird heruntergeladen

---

## 5. Conversation-Management

### 5.1 Sidebar
- [ ] **TEST:** Nach Chat-Start erscheint Conversation in der Sidebar
- [ ] **TEST:** Klick auf alte Conversation → History wird geladen, Nachrichten angezeigt
- [ ] **TEST:** "Neuer Chat" Button → Leerer Chat, Welcome-Screen
- [ ] **TEST:** Zwischen Conversations wechseln → Korrekte Nachrichten für jede
- [ ] **PRÜFEN:** Werden Conversations nach `updated_at` sortiert? (neueste zuerst?)

### 5.2 Conversation löschen
- [ ] **TEST:** Conversation löschen → Bestätigung? → Conversation verschwindet
- [ ] **TEST:** Aktive Conversation löschen → Erwartung: Redirect zu neuem Chat
- [ ] **TEST:** Conversation löschen → Nachrichten auch gelöscht? (DB-Check)
- [ ] **TEST:** Conversation löschen → Session-Logs auch gelöscht?

### 5.3 Mobile Sidebar
- [ ] **TEST:** Auf mobiler Breite → Sidebar versteckt, "☰ Gespräche" Button sichtbar
- [ ] **TEST:** Button klicken → Sidebar öffnet als Overlay
- [ ] **TEST:** Conversation auswählen → Sidebar schließt, Chat geladen
- [ ] **TEST:** Overlay-Hintergrund klicken → Sidebar schließt

---

## 6. Profil-Management

### 6.1 Profil laden
- [ ] **TEST:** `/profile` aufrufen → Bestehende Daten werden geladen
- [ ] **TEST:** Neuer Benutzer → Leeres Profil, alle Felder editierbar

### 6.2 Profil speichern
- [ ] **TEST:** Bundesland ändern → Speichern → Seite neu laden → Änderung gespeichert
- [ ] **TEST:** Schulform ändern → Speichern → Verifizieren
- [ ] **TEST:** Fächer ändern (kommasepariert?) → Speichern → Als Array in DB?
- [ ] **TEST:** Jahrgänge ändern → Speichern → Als Zahlen-Array in DB?
- [ ] **TEST:** Mehrere Felder gleichzeitig ändern → Alle korrekt gespeichert
- [ ] **TEST:** Leere Felder speichern → Erwartung: Keine Fehler, null/leere Arrays

### 6.3 Profil-Auswirkung auf KI
- [ ] **TEST:** Profil ausfüllen (z.B. Fach: "Deutsch", Bundesland: "NRW") → Chat → Frage stellen
  → Erwartung: KI berücksichtigt Profildaten in Antwort
- [ ] **TEST:** Profil ändern → Neuen Chat starten → KI nutzt aktualisiertes Profil?

### 6.4 Profil-Validierung
- [ ] **TEST:** Ungültige Jahrgangs-Zahl (z.B. -1, 99, "abc") → Erwartung: Validierungsfehler
- [ ] **TEST:** Extrem langer Fachname (1000 Zeichen) → Erwartung: Kein Crash
- [ ] **TEST:** Bundesland mit Sonderzeichen → Erwartung: Kein Crash

---

## 7. Curriculum Upload & RAG

### 7.1 PDF-Upload
- [ ] **TEST: Gültiges PDF** → Upload mit Fach + Jahrgang → Erwartung: Erfolg, Chunks-Anzahl angezeigt
- [ ] **TEST: Leeres PDF** (keine Textlayer) → Erwartung: Fehlermeldung "PDF enthält keinen extrahierbaren Text"
- [ ] **TEST: Nicht-PDF** (z.B. .docx, .jpg hochladen) → Erwartung: Fehlermeldung "Nur PDF-Dateien"
- [ ] **TEST: Großes PDF** (> 20 MB) → Erwartung: Fehlermeldung "Datei zu groß"
- [ ] **TEST: PDF knapp unter 20 MB** → Erwartung: Upload funktioniert, evtl. langsam
- [ ] **TEST: PDF mit Sonderzeichen im Dateinamen** (`Lehrplan (NRW) — Physik.pdf`) → Kein Crash
- [ ] **TEST: Gleichen Lehrplan nochmal hochladen** (gleicher Fach+Jahrgang) → Erwartung: Upsert, alte Chunks gelöscht

### 7.2 Ingestion-Pipeline
- [ ] **PRÜFEN:** Wird `pdfplumber` im async-Kontext korrekt genutzt? (Es ist synchron — kann den Event-Loop blockieren!)
- [ ] **PRÜFEN:** Chunking: Werden Chunks korrekt mit Overlap erstellt?
- [ ] **PRÜFEN:** Embeddings: Batching korrekt bei > 100 Chunks?
- [ ] **PRÜFEN:** Werden alte Chunks vor Re-Ingestion korrekt gelöscht?
- [ ] **PRÜFEN:** Was passiert wenn OpenAI API während Embedding-Erstellung ausfällt? Ist der Status dann "processing" forever?

### 7.3 Curriculum-Liste
- [ ] **TEST:** Liste zeigt alle hochgeladenen Curricula
- [ ] **TEST:** Status korrekt (active/processing)
- [ ] **TEST:** Löschen eines Curriculums → Verschwindet aus Liste + Chunks gelöscht

### 7.4 RAG-Suche (im Chat testen)
- [ ] **TEST:** Curriculum hochladen → Chat: "Was sagt der Lehrplan zu [Thema aus PDF]?"
  → Erwartung: Relevante Chunks werden gefunden und zitiert
- [ ] **TEST:** Frage zu Thema das NICHT im Curriculum ist → Erwartung: "Keine passenden Inhalte gefunden"
- [ ] **TEST:** Embedding-Search scheitert → Keyword-Fallback funktioniert?
- [ ] **TEST:** Mehrere Curricula hochgeladen → Suche findet aus dem richtigen

---

## 8. Material-Generierung (Klausur & Differenzierung)

### 8.1 Klausur via MaterialPage
- [ ] **TEST:** Material-Seite öffnen → "Klausur" auswählen → Fach/Klasse/Thema eingeben → Generieren
  → Erwartung: Vorschau mit Aufgaben, Punkten, AFB-Levels
- [ ] **TEST:** Download-Button → DOCX wird heruntergeladen
- [ ] **TEST:** DOCX öffnen in Word/LibreOffice → Korrekte Formatierung, alle Aufgaben, Erwartungshorizont, Notenschlüssel
- [ ] **TEST:** Klausur mit "Dauer: 90 Minuten" → Erwartung: Mehr/komplexere Aufgaben
- [ ] **TEST:** Klausur mit Zusatz-Anweisungen → Erwartung: KI berücksichtigt sie

### 8.2 Differenzierung via MaterialPage
- [ ] **TEST:** "Differenzierung" auswählen → Generieren
  → Erwartung: 3 Niveaus (Basis, Mittel, Erweitert)
- [ ] **TEST:** DOCX → 3 separate Abschnitte mit farblich unterschiedlichen Headings
- [ ] **TEST:** Jedes Niveau hat eigene Aufgaben mit steigender Schwierigkeit
- [ ] **TEST:** Hilfestellungen vorhanden bei Basis-Niveau?

### 8.3 Material via Chat (Tool-Aufruf)
- [ ] **TEST:** "Erstelle eine Klausur für Deutsch Klasse 8 zum Thema Kurzgeschichten"
  → Erwartung: KI ruft `generate_material` auf, gibt Download-Link zurück
- [ ] **TEST:** Download-Link aus Chat anklicken → DOCX heruntergeladen
- [ ] **TEST:** "Erstelle differenziertes Material für Mathe Klasse 5 zu Bruchrechnung"
  → Erwartung: Differenzierungs-Material

### 8.4 Inhaltliche Qualität
- [ ] **PRÜFEN:** Haben alle Aufgaben sinnvolle Beschreibungen?
- [ ] **PRÜFEN:** Stimmt die Gesamtpunktzahl (Summe der Einzelpunkte)?
- [ ] **PRÜFEN:** Ist der Notenschlüssel realistisch?
- [ ] **PRÜFEN:** Sind AFB-Stufen korrekt zugeordnet? (I=Reproduktion, II=Transfer, III=Reflexion)
- [ ] **PRÜFEN:** Erwartungshorizont passt zu Aufgaben?
- [ ] **PRÜFEN:** Differenzierung: Basis wirklich einfacher als Erweitert?

### 8.5 Edge Cases Material
- [ ] **TEST:** Leeres Thema → Erwartung: Validierungsfehler
- [ ] **TEST:** Unbekanntes Fach ("Quantenphilosophie") → Erwartung: KI versucht es trotzdem
- [ ] **TEST:** Material-Generierung fehlschlägt (z.B. API-Timeout) → Erwartung: Verständliche Fehlermeldung
- [ ] **TEST:** Zwei gleichzeitige Material-Generierungen → Keine Konflikte, beide korrekt gespeichert

---

## 9. Memory-System

### 9.1 Automatische Extraktion
- [ ] **TEST:** Im Chat erwähnen: "Meine Klasse 10a hat 28 Schüler und wir arbeiten gerade an Optik"
  → DB-Check: Wurden Memories extrahiert? (user_memories Tabelle)
  → Erwartung: Mindestens scope=class, category=..., key="Klasse 10a", value beinhaltet "28 Schüler"
- [ ] **TEST:** Im Chat: "Ich bevorzuge praxisnahen Unterricht"
  → DB-Check: Memory mit scope=self, category=preference
- [ ] **TEST:** Mehrere Gespräche → Memories akkumulieren sich, werden bei Relevanz genutzt

### 9.2 Explizites Merken
- [ ] **TEST:** "Merk dir: Ich bin allergisch gegen Frontalunterricht"
  → Erwartung: KI bestätigt mit "Gemerkt: ..."
  → DB-Check: Memory mit source="explicit", importance=0.9

### 9.3 Memory-Nutzung
- [ ] **TEST:** Neues Gespräch starten → "Was weißt du über mich?"
  → Erwartung: KI listet gespeicherte Informationen
- [ ] **TEST:** Nach Memory-Speicherung → System-Prompt enthält Memories?
  → Prüfe in Logs: System-Prompt beinhaltet "## Was du über diese Lehrkraft weißt"

### 9.4 Memory-Robustheit
- [ ] **PRÜFEN:** Was passiert wenn Memory-Agent (fire-and-forget) abstürzt?
  → Erwartung: Chat-Antwort kommt trotzdem, nur Memory fehlt
- [ ] **PRÜFEN:** Memory-Agent gibt ungültiges JSON zurück → Wird das abgefangen?
- [ ] **PRÜFEN:** Memory-Upsert schlägt fehl (DB-Fehler) → Wird geloggt?
- [ ] **PRÜFEN:** Können zwei gleichzeitige Memory-Agents (parallel-Requests) Konflikte verursachen?

---

## 10. Frontend-UI & UX

### 10.1 Responsive Design
- [ ] **TEST:** Desktop (1920x1080) → Layout korrekt, Sidebar sichtbar
- [ ] **TEST:** Tablet (768px) → Layout passt sich an
- [ ] **TEST:** Mobile (375px) → Sidebar versteckt, Mobile-Toggle sichtbar
- [ ] **TEST:** Orientierungswechsel (Portrait → Landscape) → Kein Layout-Bruch

### 10.2 Visuelles Design
- [ ] **PRÜFEN:** Farben entsprechen Design-System? (`#C8552D` Primary, `#F5F0EB` Background)
- [ ] **PRÜFEN:** Schriftart "Inter" wird geladen?
- [ ] **PRÜFEN:** Eule-Avatar bei KI-Nachrichten sichtbar?
- [ ] **PRÜFEN:** User-Nachrichten rechts, KI-Nachrichten links?
- [ ] **PRÜFEN:** Typing-Indicator korrekt animiert?

### 10.3 Navigation
- [ ] **TEST:** Alle Navigations-Links funktional (Chat, Profil, Curriculum, Material)
- [ ] **TEST:** Browser-Back/Forward → Korrekte Seiten
- [ ] **TEST:** URL direkt eingeben (z.B. `/chat`) → Entweder Login-Redirect oder korrekte Seite
- [ ] **TEST:** 404-Seiten → Redirect zu Login

### 10.4 Auto-Scroll
- [ ] **TEST:** Neue Nachricht → Chat scrollt automatisch nach unten
- [ ] **TEST:** User scrollt hoch → Neue Nachricht kommt → Wird trotzdem nach unten gescrollt?
  → Frage: Ist das gewünscht? (UX-Diskussion nötig)
- [ ] **TEST:** Typing-Indicator → Chat scrollt runter

### 10.5 Accessibility
- [ ] **PRÜFEN:** Alle Buttons haben aria-labels?
- [ ] **PRÜFEN:** Kontrast-Ratio für Text auf Background ausreichend?
- [ ] **PRÜFEN:** Textarea: Enter = Send, Shift+Enter = Newline → Korrekt?
- [ ] **PRÜFEN:** Focus-Management nach Senden (Cursor zurück ins Textfeld?)

---

## 11. API-Robustheit & Error-Handling

### 11.1 Backend-Fehler
- [ ] **TEST:** Backend nicht erreichbar → Frontend zeigt "schiefgelaufen" Meldung (nicht weißer Bildschirm)
- [ ] **TEST:** Backend gibt 500 zurück → Frontend zeigt Fehlermeldung
- [ ] **TEST:** Backend timeout (KI braucht > 60s) → Was passiert? httpx Timeout?
- [ ] **PRÜFEN:** Alle API-Calls in `api.ts` haben Error-Handling?
  → `getConversations()` gibt leeres Array zurück bei Fehler — OK
  → `sendMessage()` wirft Error — wird in ChatPage gefangen — OK
  → `deleteCurriculum()` → Kein Error-Handling! Failure wird silent ignoriert
  → `updateProfile()` → Kein Response-Check! Failure wird silent ignoriert

### 11.2 Supabase-Fehler
- [ ] **TEST:** Was passiert wenn Supabase Down ist?
  → Erwartung: Alle DB-Operationen geben verständliche Fehler
- [ ] **PRÜFEN:** `db.py` — `r.raise_for_status()` ist überall vorhanden → Fehler propagieren korrekt?
- [ ] **PRÜFEN:** Wird bei `select(single=True)` mit 406-Response korrekt `None` zurückgegeben?
- [ ] **PRÜFEN:** Was passiert bei Network-Timeout in db.py? (kein Timeout gesetzt!)

### 11.3 KI-API-Fehler
- [ ] **TEST:** Anthropic API Key ungültig → Erwartung: `500 KI-Antwort fehlgeschlagen: AuthenticationError`
- [ ] **TEST:** Anthropic Rate-Limit erreicht → Erwartung: Klare Fehlermeldung, kein Retry-Loop
- [ ] **TEST:** OpenAI API Key ungültig → Curriculum-Upload scheitert mit klarer Meldung
- [ ] **TEST:** Brave API Key ungültig → Web-Search gibt Fallback/Fehler

### 11.4 Unerwartete Eingaben
- [ ] **TEST:** `POST /api/chat/send` mit fehlendem `teacher_id` → Erwartung: 422 Validation Error
- [ ] **TEST:** `POST /api/chat/send` mit leerem `message` → Erwartung: 422 oder sinnvoller Fehler
- [ ] **TEST:** `GET /api/profile/nonexistent-uuid` → Erwartung: 404
- [ ] **TEST:** `DELETE /api/curriculum/nonexistent-id` → Erwartung: Kein Crash, leerer Erfolg

---

## 12. Sicherheit

### 12.1 Authentifizierung
- [ ] **PRÜFEN:** Kein API-Endpoint schützt sich durch Token/Session-Validierung — ALLE Endpoints sind frei zugänglich wenn man `teacher_id` kennt
  → `/api/chat/send` → braucht nur `teacher_id`
  → `/api/profile/{teacher_id}` → kein Auth-Check
  → `/api/curriculum/list` → braucht nur `teacher_id`
  → **SCHWERE: HOCH** für Produktion, akzeptabel für Demo
- [ ] **PRÜFEN:** `teacher_id` ist UUID → schwer zu erraten, ABER nicht unmöglich

### 12.2 Injection
- [ ] **TEST:** SQL/NoSQL-Injection über Passwort-Feld
- [ ] **TEST:** XSS über Chat-Nachricht (`<img src=x onerror=alert(1)>`)
  → Erwartung: react-markdown escaped HTML → kein XSS
- [ ] **TEST:** XSS über Conversation-Titel (wird er unescaped angezeigt?)
- [ ] **TEST:** Path Traversal bei Material-Download (`/api/materials/../../etc/passwd/docx`)
  → Prüfe: `material_id` wird direkt in Dateipfad eingefügt!
- [ ] **PRÜFEN:** `curriculum_id` in URL-Parameter für Supabase REST → Ist `eq.{value}` sicher gegen Injection?

### 12.3 Daten-Exposition
- [ ] **PRÜFEN:** Error-Messages an Frontend → Enthalten sie Stack-Traces oder interne Details?
  → `main.py:178`: `f"KI-Antwort fehlgeschlagen: {type(e).__name__}"` → gibt Classname preis → gering
  → `main.py:492`: `f"Materialerstellung fehlgeschlagen: {type(e).__name__}: {str(e)}"` → gibt vollständigen Fehlertext preis!
- [ ] **PRÜFEN:** `/api/debug/imports` sollte in Produktion NICHT erreichbar sein!
- [ ] **PRÜFEN:** Supabase Service-Role-Key (voller Admin-Zugang) wird im Backend genutzt — das ist OK solange das Backend nicht kompromittiert wird

### 12.4 Rate-Limiting
- [ ] **PRÜFEN:** Kein Rate-Limiting auf KEINEM Endpoint → DoS möglich
  → Besonders kritisch: `/api/chat/send` (verursacht KI-API-Kosten!)
  → Besonders kritisch: `/api/curriculum/upload` (verursacht Embedding-Kosten!)
  → Besonders kritisch: `/api/materials/generate` (verursacht KI-API-Kosten!)

---

## 13. Performance & Skalierung

### 13.1 Chat-Latenz
- [ ] **MESSEN:** Zeit von Nachricht senden bis Antwort:
  → Erste Nachricht (neue Conversation)
  → Nachfolge-Nachrichten (bestehende Conversation)
  → Nach 20+ Nachrichten (History-Laden + Agent)
- [ ] **PRÜFEN:** Wird der System-Prompt bei JEDEM Request neu gebaut? (4-5 DB-Calls!)
  → `build_system_prompt()` → `build_block3_context()` → 4 separate DB-Selects
  → + History-Laden + User-Message-Insert + Summary-Check
  → = mindestens 7-8 DB-Calls pro Chat-Request, jeder mit eigenem TCP-Handshake

### 13.2 Curriculum Upload Performance
- [ ] **MESSEN:** Upload-Dauer für ein 10-seitiges PDF
- [ ] **MESSEN:** Upload-Dauer für ein 100-seitiges PDF
- [ ] **PRÜFEN:** Chunks werden EINZELN eingefügt (Zeile 200 in ingestion.py) statt als Batch → Sehr langsam bei vielen Chunks!
  → Bei 100 Chunks = 100 separate HTTP-Requests an Supabase + 1 Embedding-Request

### 13.3 Gleichzeitige Nutzung
- [ ] **TEST:** 3 User gleichzeitig chatten → Keine Konflikte?
- [ ] **TEST:** Gleichzeitiger Chat + Curriculum-Upload → Kein Blocking?
- [ ] **PRÜFEN:** Singleton-Agent (`_agent`) → Thread-safe? (Pydantic AI Agent ist stateless, sollte OK sein)

---

## 14. Datenintegrität & Edge Cases

### 14.1 Conversation-Konsistenz
- [ ] **TEST:** User sendet Nachricht → Backend crasht nach User-Message-Speicherung aber VOR KI-Antwort → Was zeigt der Chat?
  → Erwartung: User-Nachricht in DB, keine KI-Antwort → Inkonsistenz möglich
- [ ] **PRÜFEN:** Gibt es Transaktionen? (Nein — jeder DB-Call ist einzeln)
- [ ] **TEST:** Conversation löschen während Chat aktiv → Erwartung: Kein Crash, klare Fehlermeldung

### 14.2 Material-Konsistenz
- [ ] **TEST:** Material generiert → Server neustart → Download noch möglich?
  → Disk-Cache in `/tmp` wird bei Reboot gelöscht → DB-Fallback muss greifen
- [ ] **PRÜFEN:** `MATERIALS_DIR = Path("/tmp/materials")` → Auf Windows ist `/tmp` kein Standardpfad!
  → **BUG auf Windows!**

### 14.3 Memory-Konsistenz
- [ ] **TEST:** Memory-Upsert mit gleichem Key → Wird Value überschrieben?
- [ ] **TEST:** Maximale Anzahl Memories → Kein Limit in Code → System-Prompt wächst endlos?
  → `system_prompt.py:68` lädt max 30 Memories → OK
  → Aber `user_memories`-Tabelle hat kein Limit → wächst unbegrenzt

### 14.4 UUID-Handling
- [ ] **PRÜFEN:** `conversation_id` wird als String durch die gesamte Kette gereicht → Wird es je als UUID validiert?
- [ ] **TEST:** Ungültige UUID als `conversation_id` senden → Erwartung: DB-Fehler, saubere Fehlermeldung
- [ ] **TEST:** Ungültige UUID als `teacher_id` → Erwartung: Sauberer Fehler

### 14.5 Encoding
- [ ] **TEST:** PDF mit Umlauten (ä, ö, ü) → Korrekt extrahiert und gespeichert?
- [ ] **TEST:** Chat-Nachricht mit Chinesisch/Arabisch → Korrekt verarbeitet?
- [ ] **TEST:** DOCX-Dateiname mit Umlauten → Download funktional?

---

## 15. Integration & End-to-End Workflows

### Workflow A: Kompletter Lehrer-Onboarding-Flow
```
1. Login als "Demo-Lehrer" (demo123)
2. → Profil ausfüllen: NRW, Gymnasium, Physik, Klasse 10-12
3. → Curriculum hochladen: Physik-Lehrplan NRW (Test-PDF)
4. → Chat: "Hallo, ich bin neu hier"
5. → Chat: "Was steht im Lehrplan zu Optik?"
6. → Chat: "Erstelle eine Klassenarbeit zu Optik, Klasse 10, 45 Minuten"
7. → Download DOCX prüfen
8. → Neues Gespräch: "Was weißt du über mich?"
9. → Logout → Re-Login → Daten noch da?
```
**Erwartung:** Alles funktioniert end-to-end, KI kennt Profil und Curriculum.

### Workflow B: Multi-Session Kontext
```
Session 1:
1. Login als Christopher
2. Chat: "Ich unterrichte Deutsch in Klasse 8. Wir lesen gerade 'Die Welle'."
3. Chat: "Merk dir, dass Schülerin Anna besondere Förderung braucht."
4. Schließe Tab

Session 2 (neuer Tab):
5. Login als Christopher
6. Neuer Chat: "Woran haben wir zuletzt gearbeitet?"
7. → Erwartung: KI erinnert sich an 'Die Welle' (über Memory)
8. Chat: "Erstelle differenziertes Material für die nächste Stunde"
9. → Erwartung: Material berücksichtigt das Thema 'Die Welle'
```

### Workflow C: Material-Iteration
```
1. Chat: "Erstelle eine Klausur Physik Klasse 11, Thema Mechanik"
2. → KI generiert Klausur, Download-Link
3. Chat: "Mach Aufgabe 2 anspruchsvoller"
4. → Erwartung: KI kann nicht die DOCX modifizieren, aber kann eine neue Version erstellen
5. Chat: "Erstelle das Material nochmal, aber mit mehr AFB-III-Aufgaben"
6. → KI generiert neues Material
7. Download beider Versionen → Vergleich
```

### Workflow D: Fehlertoleranz
```
1. Login → Chat starten
2. Backend herunterfahren → Nachricht senden
3. → Erwartung: Fehlermeldung im Chat, kein weißer Bildschirm
4. Backend wieder starten → Nachricht senden
5. → Erwartung: Funktioniert wieder, vorherige Nachrichten noch da
```

### Workflow E: Curriculum + Chat Integration
```
1. KEIN Curriculum hochgeladen
2. Chat: "Was sagt der Lehrplan zu Optik?"
3. → Erwartung: KI sagt, dass noch kein Lehrplan hochgeladen ist
4. Curriculum hochladen
5. Selbe Frage nochmal
6. → Erwartung: Jetzt findet die Suche Ergebnisse
```

### Workflow F: Gleichzeitige Aktionen
```
1. In Tab A: Chat-Nachricht senden (wartet auf KI-Antwort)
2. In Tab B: Material generieren
3. → Erwartung: Beides funktioniert parallel
4. In Tab A: Antwort kommt
5. In Tab B: Material kommt
```

### Workflow G: Profilbasierte Suggestions
```
1. Login (leeres Profil)
2. → Erwartung: Default-Suggestions auf Welcome-Screen
3. Profil ausfüllen (Mathe, Klasse 5-7)
4. Neuer Chat
5. → Erwartung: Personalisierte Suggestions (z.B. "Plane eine Mathestunde Klasse 5")
6. Einige Gespräche führen über Bruchrechnung
7. Neuer Chat
8. → Erwartung: Suggestions basierend auf Memories + Profil
```

---

## Zusammenfassung: Prioritäten

### KRITISCH (Blockiert sinnvolle Nutzung)
1. BUG-003: Fehlende Auth bei Chat-History (Datenleck)
2. BUG-005: CORS Allow-All
3. `/tmp/materials` funktioniert nicht auf Windows
4. Kein Rate-Limiting (KI-API-Kosten-Risiko)

### HOCH (Stark beeinträchtigt)
5. BUG-007: Kein Shared httpx Client (Performance)
6. BUG-002: `__import__("httpx")` Anti-Pattern
7. Chunks einzeln eingefügt statt Batch
8. Kein Timeout in db.py
9. Error-Details an Frontend exponiert

### MITTEL (Sollte behoben werden)
10. BUG-004: Fehlende Auth bei Conversation-Update
11. BUG-006: Klartext-Passwörter
12. BUG-008: Fire-and-forget ohne Error-Callback
13. `pdfplumber` blockiert Event-Loop (synchron)
14. `deleteCurriculum()` und `updateProfile()` im Frontend ohne Error-Handling
15. `/api/debug/imports` in Produktion erreichbar

### NIEDRIG (Nice-to-have)
16. Session-Expiry fehlt
17. Profil-Eingabe-Validierung
18. Accessibility-Verbesserungen
19. Auto-Scroll-Verhalten bei hochgescrolltem Chat

---

## Anleitung für den QA-Agenten

1. **Starte mit Abschnitt 1** (Bekannte Bugs) — verifiziere und fixe diese zuerst
2. **Dann Abschnitt 2-3** (Startup + Auth) — Basis muss funktionieren
3. **Dann Abschnitt 4** (Chat Multi-Turn) — Kernfunktionalität
4. **Dann die Workflows** (Abschnitt 15) — End-to-End Validierung
5. **Dann Security + Performance** (Abschnitt 11-13) — Härtung
6. **Für jeden gefundenen Bug:** Erstelle einen Fix oder dokumentiere ihn mit Datei, Zeile, Problem, Vorschlag
7. **Nutze die Checkbox-Notation** `[x]` um abgearbeitete Punkte zu markieren

> Generiert am 2026-02-14 auf Basis einer vollständigen Code-Analyse und Recherche zu häufigen Qualitätsproblemen in KI-generiertem Code.
