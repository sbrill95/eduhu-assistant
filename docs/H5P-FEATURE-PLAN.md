# H5P Feature — Architektur-Plan

## Vision

Lehrer erstellt im Chat interaktive Übungen → Übungen landen auf einer Klassen-Seite → Schüler:innen öffnen per Access-Code → machen Übungen im Browser.

## User Flow

### Lehrer-Seite (Chat)
```
Lehrer: "Erstelle eine Multiple-Choice-Übung zu Photosynthese, Klasse 7"
→ H5P-Agent erstellt Übung
→ System: "Übung erstellt! Noch keine Klassen-Seite vorhanden."
→ System: "Klassen-Seite 'tiger42' angelegt. Schüler:innen erreichen sie unter eduhu-assistant.pages.dev/s/tiger42"
→ Card erscheint auf der Klassen-Seite

Lehrer: "Erstelle noch einen Lückentext zum gleichen Thema"
→ Zweite Übung wird zu tiger42 hinzugefügt
```

### Schüler-Seite
```
1. Schüler öffnet eduhu-assistant.pages.dev/s/tiger42
   (oder: eduhu-assistant.pages.dev → gibt Code "tiger42" ein)
2. Sieht Cards mit Übungen:
   [📝 Photosynthese — Multiple Choice]  [📝 Photosynthese — Lückentext]
3. Klickt auf Card → H5P-Übung öffnet sich im Browser
4. Macht die Übung → Ergebnis wird angezeigt
```

## Access Codes

- Format: **Nomen + 2 Ziffern** (z.B. "tiger42", "wolke17", "stern88")
- Einfach zu merken, diktierbar, kindgerecht
- Pool: ~200 deutsche Nomen × 100 Zahlen = 20.000 Kombinationen
- Später: Code änderbar (z.B. nach Schuljahresende)

## Datenmodell

### Neue Tabellen

```sql
-- Klassen-Seiten (Landing Pages)
CREATE TABLE exercise_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  teacher_id UUID REFERENCES teachers(id),
  access_code TEXT UNIQUE NOT NULL,  -- "tiger42"
  title TEXT,                         -- "Biologie 7a"
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Einzelne Übungen auf einer Seite
CREATE TABLE exercises (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id UUID REFERENCES exercise_pages(id) ON DELETE CASCADE,
  teacher_id UUID REFERENCES teachers(id),
  title TEXT NOT NULL,                -- Auto-generiert: "Photosynthese — Multiple Choice"
  h5p_content JSONB NOT NULL,         -- H5P content.json
  h5p_type TEXT NOT NULL,             -- "H5P.MultiChoice", "H5P.Blanks", etc.
  sort_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Optional: Schüler-Ergebnisse (Phase 2)
CREATE TABLE exercise_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exercise_id UUID REFERENCES exercises(id),
  score REAL,                         -- 0.0 - 1.0
  max_score REAL,
  duration_seconds INTEGER,
  completed_at TIMESTAMPTZ DEFAULT now()
);
```

## Agent-Architektur

### H5P-Agent (neuer Sub-Agent)
- **Modell**: Haiku (kostengünstig, reicht für strukturierte Outputs)
- **Input**: Fach, Klasse, Thema, Übungstyp (oder "automatisch wählen")
- **Output**: H5P content.json + Metadaten
- **Kontext**: Übernimmt aus Chat (Profil, Thema, vorherige Übungen)

### Unterstützte H5P-Typen (Phase 1)
1. **H5P.MultiChoice** — Multiple Choice (eine oder mehrere richtige)
2. **H5P.Blanks** — Lückentext
3. **H5P.TrueFalse** — Richtig/Falsch
4. **H5P.DragText** — Text-Zuordnung (Drag & Drop)
5. **H5P.MarkTheWords** — Wörter markieren

### Workflow im Main-Agent
```
Lehrer fragt nach Übung
→ Main-Agent ruft Tool `generate_exercise` auf
→ Tool delegiert an H5P-Agent
→ H5P-Agent generiert content.json
→ System prüft: Hat Lehrer schon eine Seite für diese Klasse?
  → Nein: Erstelle exercise_page mit neuem Access-Code
  → Ja: Füge Übung zu bestehender Seite hinzu
→ Rückgabe an Lehrer: Titel + Link + Access-Code
```

## Frontend

### Neue Routen
- `/s/:code` — Schüler-Landing-Page (öffentlich, kein Login)
- `/s/:code/:exerciseId` — Einzelne H5P-Übung (öffentlich)
- `/exercises` — Lehrer: Übersicht eigener Übungs-Seiten (authentifiziert)

### H5P Rendering
- **h5p-standalone** (npm) oder **Lumi Player** für Browser-Rendering
- H5P content.json wird vom Backend geladen, Player rendert client-side
- Kein H5P-Server nötig — nur JSON + statischer Player

### Schüler-Seite Design
- Warm, einladend, eduhu-Design (#C8552D, #F5F0EB)
- Access-Code-Eingabe auf Startseite (groß, zentral)
- Cards mit:
  - Übungs-Titel (auto-generiert)
  - Übungs-Typ-Icon (📝 MC, 🔤 Lückentext, etc.)
  - Optional: Schwierigkeitsgrad

## API Endpoints (neu)

```
# Lehrer (authentifiziert)
POST /api/exercises/generate     — H5P-Übung via Agent erstellen
GET  /api/exercises/pages        — Eigene Übungs-Seiten auflisten
POST /api/exercises/pages        — Neue Seite manuell anlegen
PATCH /api/exercises/pages/:id   — Seite bearbeiten (Code ändern, Titel)
DELETE /api/exercises/:id        — Übung entfernen

# Schüler (öffentlich)
GET /api/public/pages/:code      — Seite + Übungen laden (per Access-Code)
GET /api/public/exercises/:id    — H5P content.json für Player
POST /api/public/results         — Ergebnis speichern (Phase 2)
```

## Phasen

### Phase 1: MVP
- H5P-Agent (MultiChoice + Blanks)
- exercise_pages + exercises Tabellen
- Access-Code-Generierung
- Schüler-Landing-Page mit H5P-Player
- Chat-Integration ("Erstelle Übung...")
- Lehrer sieht eigene Seiten

### Phase 2: Erweiterung
- Weitere H5P-Typen (DragText, TrueFalse, MarkTheWords)
- Ergebnis-Tracking (exercise_results)
- Lehrer sieht Schüler-Ergebnisse
- Übungen sortieren/umordnen
- Access-Code ändern

### Phase 3: Hub
- DOCX-Downloads auf gleicher Seite
- Zeitgesteuerte Freigabe
- Passwortschutz pro Seite (optional)
- QR-Code-Generierung für Access-Code

## Offene Fragen
1. H5P-Player: h5p-standalone vs. Lumi vs. eigene Implementierung?
2. Speicher: H5P content als JSONB in Supabase oder als .h5p-Dateien in Storage?
3. Brauchen wir echte .h5p-Dateien (ZIP) oder reicht JSON + Player?
4. Ergebnis-Tracking: Anonym oder mit Schüler-Identifikation?

→ Research-Agent arbeitet gerade an diesen Fragen.
