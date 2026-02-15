# Jobs To Be Done — eduhu-assistant

## Überblick

Dieses Dokument beschreibt die Jobs To Be Done (JTBD) für den eduhu-assistant aus der Perspektive von Lehrkräften. Die Job Stories helfen dabei, die Anforderungen und Erwartungen an den KI-gestützten Assistenten zu verstehen und die Entwicklung an den tatsächlichen Bedürfnissen der Nutzer auszurichten.

Der eduhu-assistant unterstützt Lehrkräfte bei der Unterrichtsvorbereitung, Materialerstellung, Differenzierung und Prüfungsentwicklung durch KI-gestützte Tools mit Lehrplan-Integration und Personalisierung.

---

## Job Stories nach Kategorien

### 1. Unterrichtsvorbereitung

#### 1.1 Materialsuche und -erstellung
> **Wenn ich** eine neue Unterrichtseinheit planen muss,
> **möchte ich** auf Basis des Lehrplans automatisch passende Materialvorschläge erhalten,
> **damit ich** Zeit bei der Recherche spare und curricular konform arbeite.

> **Wenn ich** Material für eine spezifische Lerngruppe erstellen muss,
> **möchte ich** dem System Details zu Vorwissen und Leistungsstand mitteilen,
> **damit die** generierten Materialien optimal an meine Schüler:innen angepasst sind.

> **Wenn ich** als Referendarin meine erste Unterrichtsstunde vorbereite,
> **möchte ich** didaktische Hinweise und Begründungen zu den Materialien erhalten,
> **damit ich** meine Entscheidungen im Unterrichtsgespräch professionell begründen kann.

#### 1.2 Themenerschließung
> **Wenn ich** ein komplexes Thema in einem fremden Fach unterrichten muss,
> **möchte ich** fundierte Sachinformationen und didaktische Aufbereitungen erhalten,
> **damit ich** sicher und fachlich korrekt unterrichten kann.

> **Wenn ich** aktuelle Bezüge für meinen Unterricht benötige,
> **möchte ich** per Web-Recherche tagesaktuelle Beispiele finden,
> **damit der** Unterricht lebensnah und motivierend ist.

---

### 2. Prüfungserstellung

#### 2.1 Klausurentwicklung
> **Wenn ich** eine Klausur erstellen muss,
> **möchte ich** Aufgaben mit automatischer AFB-Verteilung (30% I / 40% II / 30% III) generieren lassen,
> **damit die** Prüfung den bildungspolitischen Anforderungen entspricht.

> **Wenn ich** eine Klausur fertiggestellt habe,
> **möchte ich** automatisch einen vollständigen Erwartungshorizont und Notenschlüssel erhalten,
> **damit ich** Zeit bei der Korrektur spare und fair bewerten kann.

> **Wenn ich** Prüfungsaufgaben überarbeiten möchte,
> **möchte ich** einzelne Aufgaben gezielt ändern können (patch_material_task),
> **damit ich** nicht die gesamte Klausur neu erstellen muss.

#### 2.2 Leistungsmessung
> **Wenn ich** verschiedene Aufgabentypen benötige,
> **möchte ich** zwischen Multiple-Choice, offenen Aufgaben und gemischten Formaten wählen können,
> **damit ich** unterschiedliche Kompetenzen angemessen prüfen kann.

> **Wenn ich** eine Prüfung für eine heterogene Lerngruppe erstelle,
> **möchte ich** Aufgaben mit unterschiedlichen Schwierigkeitsgraden erhalten,
> **damit alle** Schüler:innen ihrem Leistungsvermögen entsprechend gefordert werden.

---

### 3. Differenzierung & Individualisierung

#### 3.1 Niveaudifferenzierung
> **Wenn ich** Material für eine leistungsheterogene Klasse erstelle,
> **möchte ich** automatisch drei Niveaustufen (Basis / Mittel / Erweitert) generieren lassen,
> **damit alle** Schüler:innen auf ihrem Niveau arbeiten können.

> **Wenn ich** differenziertes Material einsetze,
> **möchte ich** dass die Lernziele für alle Niveaus identisch bleiben,
> **damit** gemeinsame Auswertung und Vergleichbarkeit gewährleistet sind.

#### 3.2 Anpassung an Lernvoraussetzungen
> **Wenn ich** Schüler:innen mit speziellen Förderbedarfen unterrichte,
> **möchte ich** Materialien mit angepasster Komplexität und Strukturierung erhalten,
> **damit** Barrierefreiheit und Teilhabe ermöglicht werden.

> **Wenn ich** eine Lerngruppe mit unterschiedlichen Sprachniveaus habe,
> **möchte ich** sprachsensibel aufbereitete Materialien generieren,
> **damit** Sprachlernende nicht aufgrund der Sprache am Fachlernen gehindert werden.

---

### 4. Interaktive Übungen (H5P)

#### 4.1 Übungserstellung
> **Wenn ich** meine Schüler:innen auf eine Klausur vorbereiten möchte,
> **möchte ich** interaktive H5P-Übungen erstellen können,
> **damit** Lernende selbstständig üben und unmittelbares Feedback erhalten.

> **Wenn ich** verschiedene Übungstypen benötige,
> **möchte ich** zwischen Multiple-Choice, Lückentext, Wahr/Falsch und Drag-Text wählen können,
> **damit ich** Abwechslung und passende Formate für meine Lernziele habe.

#### 4.2 Übungsbereitstellung
> **Wenn ich** Übungen für meine Schüler:innen bereitstellen möchte,
> **möchte ich** einen einfachen Zugangscode generieren können,
> **damit** Schüler:innen ohne komplexe Anmeldung üben können.

> **Wenn ich** den Lernfortschritt meiner Klasse verfolgen möchte,
> **möchte ich** sehen, welche Schüler:innen welche Übungen bearbeitet haben,
> **damit ich** gezielt unterstützen kann.

---

### 5. Lehrplanarbeit

#### 5.1 Curriculare Orientierung
> **Wenn ich** eine neue Unterrichtseinheit plane,
> **möchte ich** die relevanten Lehrplaninhalte direkt im Chat durchsuchen können (search_curriculum),
> **damit ich** sicherstelle, dass mein Unterricht curricular verankert ist.

> **Wenn ich** den Lehrplan meiner Schule hochlade,
> **möchte ich** dass das System ihn semantisch erschließt,
> **damit** ich präzise Suchergebnisse zu meinen spezifischen curricularen Vorgaben erhalte.

#### 5.2 Kompetenzorientierung
> **Wenn ich** kompetenzorientiert unterrichten möchte,
> **möchte ich** Vorschläge erhalten, welche Kompetenzen durch ein Thema gefördert werden,
> **damit ich** meinen Unterricht systematisch entwickeln kann.

> **Wenn ich** zwischen verschiedenen Bundesländern und Schulformen wechsle,
> **möchte ich** dass das System die entsprechenden Lehrpläne berücksichtigt,
> **damit** die Materialien zu meinem spezifischen Kontext passen.

---

### 6. Effizienz & Organisation

#### 6.1 Zeitersparnis
> **Wenn ich** am Sonntagabend noch Material für den Montag benötige,
> **möchte ich** innerhalb weniger Minuten fertige Arbeitsblätter als DOCX herunterladen,
> **damit ich** meine Freizeit schütze und dennoch gut vorbereitet in den Unterricht gehe.

> **Wenn ich** wiederkehrende Aufgabentypen erstelle,
> **möchte ich** dass das System meine Präferenzen speichert (remember),
> **damit ich** nicht jedes Mal die gleichen Anpassungen vornehmen muss.

#### 6.2 Personalisierung
> **Wenn ich** den Assistenten regelmäßig nutze,
> **möchte ich** dass er mein Profil (Bundesland, Schulform, Fächer) kennt,
> **damit** alle Vorschläge automatisch auf meinen Kontext zugeschnitten sind.

> **Wenn ich** bestimmte Stile oder Formate bevorzuge,
> **möchte ich** dass das System diese für zukünftige Materialien berücksichtigt,
> **damit** die Ergebnisse konsistent zu meinen gewohnten Materialien passen.

#### 6.3 Qualitätsicherung
> **Wenn ich** KI-generiertes Material erhalte,
> **möchte ich** Quellenangaben und Verweise auf den Lehrplan sehen,
> **damit ich** die fachliche Richtigkeit überprüfen kann.

> **Wenn ich** Material an Kolleg:innen weitergebe,
> **möchte ich** dass es professionell formatiert und sofort einsetzbar ist,
> **damit ich** keinen zusätzlichen Aufwand für die Aufbereitung habe.

---

## Priorisierung

### Must-Have (P0) — Kernfunktionen
1. **Klausurerstellung mit AFB-Verteilung** — Höchster Zeitspareffekt
2. **Differenziertes Material (3 Niveaus)** — Zentrale pädagogische Anforderung
3. **Lehrplan-Integration** — Notwendig für curriculare Konformität
4. **DOCX-Export** — Sofortige Einsatzbereitschaft

### Should-Have (P1) — Wichtige Funktionen
5. **H5P-Übungen** — Hoher Mehrwert für Selbstlernphasen
6. **Erwartungshorizont & Notenschlüssel** — Effizienz bei Korrekturen
7. **Personalisierung (Memory)** — Verbessert Nutzererfahrung signifikant

### Nice-to-Have (P2) — Ergänzende Funktionen
8. **Web-Recherche** — Für aktuelle Bezüge
9. **Einzelne Aufgaben ändern (Patch)** — Flexibilität bei Anpassungen
10. **Schüler-Zugangsstatistiken** — Ergänzende Kontrolle

---

## Akzeptanzkriterien

### Für Materialerstellung
- [ ] Generierte Materialien sind fachlich korrekt und didaktisch sinnvoll
- [ ] DOCX-Dateien lassen sich direkt öffnen und bearbeiten
- [ ] AFB-Verteilung entspricht den Vorgaben (30/40/30)
- [ ] Drei Niveaustufen sind klar unterscheidbar und konsistent

### Für H5P-Übungen
- [ ] Übungen funktionieren ohne technische Kenntnisse der Lehrkraft
- [ ] Schüler:innen können mit Zugangscode üben
- [ ] Verschiedene Aufgabentypen (MC, Lückentext, etc.) sind verfügbar
- [ ] Feedback ist hilfreich und lernförderlich

### Für Lehrplan-Integration
- [ ] Suchergebnisse sind relevant und präzise
- [ ] Hochgeladene PDFs werden korrekt erschlossen
- [ ] Verweise auf den Lehrplan sind nachvollziehbar

### Für Personalisierung
- [ ] Profilinformationen (Bundesland, Schulform, Fächer) werden gespeichert
- [ ] Präferenzen werden über Sessions hinweg beibehalten
- [ ] Anpassungen sind transparent und vom Nutzer kontrollierbar

### Für Effizienz
- [ ] Materialerstellung dauert maximal 2-3 Minuten
- [ ] Benutzeroberfläche ist intuitiv ohne Schulung
- [ ] Ergebnisse sind sofort einsatzbereit ohne Nachbearbeitung

---

## Zielgruppen-spezifische Jobs

### Referendar:innen
- Brauchen didaktische Begründungen und Hinweise
- Benötigen Unterstützung bei der Planungssicherheit
- Schätzen ausführliche Erwartungshorizonte als Orientierung

### Erfahrene Lehrkräfte
- Fokus auf Effizienz und Zeitersparnis
- Wollen schnelle Anpassungen an bekannte Formate
- Nutzen Personalisierung für konsistente Materialien

### Fachfremd Unterrrichtende
- Benötigen fundierte Sachinformationen
- Schätzen didaktische Aufbereitungen
- Wollen Sicherheit in fachlichen Fragen

---

## Metriken zur Erfolgsmessung

| Job-Kategorie | Metrik | Zielwert |
|---------------|--------|----------|
| Materialerstellung | Zeit bis zum fertigen Material | < 3 Minuten |
| Prüfungserstellung | AFB-Verteilungsgenauigkeit | 100% Konformität |
| Differenzierung | Nutzung der 3 Niveaus | > 50% der Materialien |
| H5P-Übungen | Schüler-Engagement | > 70% Bearbeitungsquote |
| Lehrplan-Integration | Relevanz der Suchergebnisse | > 90% Trefferquote |
| Personalisierung | Wiederkehrende Nutzer | > 60% nach 30 Tagen |
| Gesamtzufriedenheit | NPS (Net Promoter Score) | > 50 |

---

*Zuletzt aktualisiert: Februar 2026*
