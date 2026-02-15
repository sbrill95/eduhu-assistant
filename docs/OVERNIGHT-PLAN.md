# Overnight Plan — 2026-02-16 (v2)

## Steffens Aufträge (vollständig)

### A. Flows testen & fixen

#### A1. Onboarding-Flow neuer Lehrer
- [ ] Neuen Account anlegen, einloggen
- [ ] Curriculum hochladen → wird es im Chat verwendet?
- [ ] Auto-Erkennung: Ist das ein Curriculum? (Format-Check)
- [ ] Klar definiertes Curriculum → kein Schulform nötig
- [ ] Upload-Feedback sinnvoll?

#### A2. Memory-System Stresstest
- [ ] Viele Memories erzeugen (verschiedene Fächer, Klassen, Themen)
- [ ] Priorisierung testen: Kommen die wichtigsten Memories?
- [ ] Alte vs. neue Memories: Recency Boost?
- [ ] Über mehrere Chats: Erinnert sich der Agent korrekt?

#### A3. Zusammenfassungs-Job
- [ ] Existiert ein Cron-Job für Chat-Zusammenfassungen?
- [ ] Wenn ja: Qualität prüfen
- [ ] Wenn nein: Wurde das nur konzipiert aber nicht gebaut?

#### A4. Klausur + Differenzierung mit Kontext
- [ ] Mit vielen Memories: Stellt der Agent noch Schärfungsfragen?
- [ ] AFB-Verteilung korrekt?
- [ ] Differenzierung: Fragt er nach Form? (Niveau, Umfang, etc.)

#### A5. H5P Full Flow
- [ ] "Erstelle Physik-Übung Klasse 8 Optik"
- [ ] QR-Card wird angezeigt?
- [ ] Link öffnen → Schüler-Seite laden
- [ ] Übungen durchspielbar?
- [ ] Mehrere Übungstypen (MultiChoice, Blanks, TrueFalse)

### B. UI/UX Verbesserungen

#### B1. "Materialien" Menü-Item entfernen
- [ ] Prüfen was MaterialPage macht
- [ ] Wenn überflüssig: aus Navigation entfernen

#### B2. Denk-/Agent-Indikator verbessern
- [ ] Kontrast erhöhen (aktuell zu blass)
- [ ] Wechselnde Texte für verschiedene Tätigkeiten
- [ ] z.B. "📚 Lehrplan wird durchsucht..." → "📝 Material wird erstellt..."

#### B3. Brave Search Quellenangaben
- [ ] Wenn web_search Tool verwendet: Quellen als Fußnoten
- [ ] Klickbare Links am Ende der Bubble
- [ ] Format: [1] Titel — url

#### B4. Curriculum-Nutzungs-Hinweis
- [ ] Wenn curriculum_search Tool verwendet: Hinweis anzeigen
- [ ] z.B. "📖 Basierend auf: Physik Sachsen Kl. 8"

#### B5. Visuelle Überprüfung
- [ ] Alle Seiten screenshots, prüfen auf:
  - Kaputte Layouts
  - Unsinnige Elemente
  - Kontrast-Probleme
  - Mobile-Tauglichkeit

### C. Qualitätstests als verschiedene Lehrer

#### C1. Physik-Lehrer (Klasse 8-10, Sachsen)
- Curriculum: Physik Sachsen
- Tests: Klausur Optik, Differenzierung Mechanik, H5P Elektrizität

#### C2. Deutsch-Lehrer (Klasse 5-7, Berlin)
- Kein Curriculum
- Tests: Arbeitsblatt Grammatik, Klausur Textanalyse

#### C3. Bio-Lehrer (Abendschule, Gesamtschule)
- Tests: Memory über Klassensituation, angepasste Materialien

### D. Neues Feature: Bildgenerierung (Gemini Imagen)

#### D1. Backend
- [ ] Gemini Imagen API researchen (Modell, Endpoint, Kosten)
- [ ] `image_agent.py` — Prompt → Bild generieren
- [ ] Tool `generate_image` im Hauptagent
- [ ] Regenerierung/Anpassung: "Mach X anders" → neues Bild
- [ ] Bild als Base64 oder URL zurückgeben

#### D2. Frontend
- [ ] Bild in Chat-Bubble anzeigen (inline)
- [ ] Download-Button
- [ ] Share-Option (Link kopieren oder in Material einbetten)

#### D3. Workflow
- [ ] "Erstelle ein Bild für mein Arbeitsblatt: Wasserkreislauf"
- [ ] Agent generiert → zeigt Preview → Lehrer sagt "Mehr Wolken"
- [ ] Agent regeneriert → Lehrer zufrieden → Download/Einbetten

## Regeln
- **NUR Gemini + MiniMax für Code-Änderungen**
- **Playwright für alle visuellen Tests**
- **Jeden Fix sofort committen und pushen**
- **Qualität > Quantität — lieber 3 Flows perfekt als 10 halb**
