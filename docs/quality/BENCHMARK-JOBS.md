# Jobs to be Done — Benchmark-Framework

> **Zweck:** Operationalisierte JTBD-Tabelle als gemeinsame Grundlage im Team.
> Jeder Job hat messbare Sub-Operationen und konkrete Testsets, die automatisiert ausgeführt werden können.
>
> **Stand:** Februar 2026 — v1 (Diskussionsvorlage)

---

## Wie diese Tabelle funktioniert

| Spalte | Bedeutung |
|--------|-----------|
| **Job** | Was die Lehrkraft erreichen will (Nutzersicht) |
| **Sub-Operation** | Messbarer Teilschritt, den das System dafür leisten muss |
| **Testset** | Konkreter Prompt + Erwartungskriterien → automatisiert prüfbar |
| **Kriterium** | Woran wir Pass/Fail entscheiden (Regex, Strukturcheck, LLM-Judge) |

### Prüfmethoden

- **Regex** — Einfacher Pattern-Match auf die Antwort (z.B. enthält "AFB I", "AFB II", "AFB III")
- **Struktur** — JSON/DOCX-Strukturprüfung (z.B. DOCX hat Tabelle mit Erwartungshorizont)
- **LLM-Judge** — Zweites LLM bewertet die Antwort nach Rubrik (z.B. "Ist die Erklärung altersgerecht für Klasse 5?")
- **Latenz** — Antwortzeit unter Schwellenwert
- **Roundtrip** — Über mehrere Turns hinweg prüfen (Kontext bleibt erhalten)

---

## J01 — Klausur erstellen

> **Job:** "Wenn ich eine Klausur brauche, möchte ich Fach/Klasse/Thema/Dauer nennen und eine druckfertige Klausur mit Erwartungshorizont erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J01.1 | Aufgaben generieren mit AFB-Verteilung | `Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten` | Antwort enthält Aufgaben mit AFB I, II und III; Verteilung ~30/40/30 | Regex + LLM-Judge |
| J01.2 | Erwartungshorizont beifügen | (gleicher Prompt wie J01.1) | DOCX enthält Abschnitt "Erwartungshorizont" mit Musterlösungen zu jeder Aufgabe | Struktur |
| J01.3 | Notenschlüssel beifügen | (gleicher Prompt wie J01.1) | DOCX enthält Notenschlüssel-Tabelle (Note → Punktbereich) | Struktur |
| J01.4 | DOCX-Download funktioniert | Download-Link aus Antwort abrufen | HTTP 200, Content-Type `application/vnd.openxmlformats`, Datei > 5 KB | Struktur |
| J01.5 | Punkteverteilung konsistent | (gleicher Prompt wie J01.1) | Summe der Einzelpunkte = Gesamtpunktzahl im Notenschlüssel | Struktur |
| J01.6 | Einzelne Aufgabe ändern | Turn 1: Klausur generieren. Turn 2: `Mach Aufgabe 2 anspruchsvoller` | Aufgabe 2 wurde geändert (neuer Text), restliche Aufgaben identisch | Roundtrip + LLM-Judge |
| J01.7 | Fachliche Korrektheit | `Erstelle eine Klausur für Chemie Klasse 11, Thema Redoxreaktionen` | Aufgaben sind fachlich korrekt (keine falschen Formeln, keine erfundenen Fakten) | LLM-Judge |
| J01.8 | Antwortzeit akzeptabel | (gleicher Prompt wie J01.1) | Antwort innerhalb von 60 Sekunden | Latenz |

### Testset-Varianten für J01

```yaml
- prompt: "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten"
  fach: Physik
  erwartung: Aufgaben zu Kraft, Beschleunigung, Newton
- prompt: "Erstelle eine Klausur für Deutsch Klasse 8, Thema Kurzgeschichten, 90 Minuten"
  fach: Deutsch
  erwartung: Textanalyse, Stilmittel, Interpretation
- prompt: "Erstelle eine Klausur für Politische Bildung Klasse 10, Thema Demokratie"
  fach: Politik
  erwartung: Quellenanalyse, Urteilsbildung
- prompt: "Erstelle eine Klausur für Pflege LF1, Thema Pflegeprozess"
  fach: Pflege (Berufsschule)
  erwartung: Fallsituation, Pflegeplanung
```

---

## J02 — Differenziertes Material erstellen

> **Job:** "Wenn ich heterogene Lerngruppen habe, möchte ich automatisch drei Niveaustufen erhalten, damit alle Schüler auf ihrem Level arbeiten können."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J02.1 | Drei Niveaus generieren | `Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung` | Antwort/DOCX enthält drei klar getrennte Abschnitte: Basis, Mittel, Erweitert | Struktur |
| J02.2 | Niveaus sind unterscheidbar | (gleicher Prompt) | Basis ist sprachlich/inhaltlich einfacher als Mittel, Mittel einfacher als Erweitert | LLM-Judge |
| J02.3 | Gleiches Lernziel auf allen Niveaus | (gleicher Prompt) | Alle drei Niveaus behandeln dasselbe Kernthema (nicht verschiedene Themen) | LLM-Judge |
| J02.4 | DOCX-Download funktioniert | Download-Link abrufen | HTTP 200, Datei öffenbar, drei Abschnitte sichtbar | Struktur |
| J02.5 | Hilfestellungen auf Basis-Niveau | (gleicher Prompt) | Basis-Niveau enthält Hinweise, Tipps oder Hilfestellungen | LLM-Judge |

### Testset-Varianten für J02

```yaml
- prompt: "Erstelle differenziertes Material für Mathe Klasse 7, Thema Bruchrechnung"
- prompt: "Erstelle differenziertes Material für Biologie Klasse 9, Thema Zellteilung"
- prompt: "Erstelle differenziertes Material für Deutsch Klasse 5, Thema Märchen"
```

---

## J03 — Interaktive Übungen erstellen (H5P)

> **Job:** "Wenn ich meinen Schülern selbstständiges Üben ermöglichen will, möchte ich interaktive Übungen erstellen, die sie ohne Anmeldung per Code aufrufen können."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J03.1 | Übungen generieren | `Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7` | Antwort enthält ≥ 5 Fragen mit je ≥ 3 Antwortoptionen | Regex + Struktur |
| J03.2 | Zugangscode generiert | (gleicher Prompt) | Antwort enthält Zugangscode (z.B. `tiger42`) und Link | Regex |
| J03.3 | QR-Code generiert | (gleicher Prompt) | Antwort enthält QR-Code-URL oder Bild | Regex |
| J03.4 | Schülerseite erreichbar | Zugangscode aus J03.2 über `/s/{code}` aufrufen | HTTP 200, Seite zeigt Übungen | Struktur |
| J03.5 | Verschiedene Übungstypen | `Erstelle Lückentext-Übungen zu Bruchrechnung` | Übungstyp ist "blanks" (nicht MC) | Struktur |
| J03.6 | Fachliche Korrektheit | (gleicher Prompt wie J03.1) | Richtige Antworten sind tatsächlich korrekt, falsche plausibel aber falsch | LLM-Judge |

### Testset-Varianten für J03

```yaml
- prompt: "Erstelle 5 Multiple-Choice-Fragen zu Photosynthese für Klasse 7"
  typ: multichoice
- prompt: "Erstelle Lückentext-Übungen zum Thema Bruchrechnung Klasse 6"
  typ: blanks
- prompt: "Erstelle Wahr-oder-Falsch-Fragen zum Thema Demokratie Klasse 9"
  typ: truefalse
- prompt: "Erstelle Drag-Text-Übungen zum Thema Satzglieder Klasse 5"
  typ: dragtext
```

---

## J04 — Lehrplan durchsuchen

> **Job:** "Wenn ich wissen will, was der Lehrplan zu einem Thema sagt, möchte ich im Chat danach fragen und relevante Auszüge erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J04.1 | Relevante Lehrplan-Chunks finden | `Was steht im Lehrplan zu Optik Klasse 8?` | Antwort enthält spezifische Lehrplaninhalte (nicht nur allgemeines Wissen) | LLM-Judge |
| J04.2 | Kompetenzen benennen | `Welche Kompetenzen soll ich bei Elektrizitätslehre fördern?` | Antwort nennt konkrete Kompetenzformulierungen aus dem Lehrplan | LLM-Judge |
| J04.3 | Kein Lehrplan → Hinweis | (Lehrkraft ohne hochgeladenen Lehrplan) `Was sagt mein Lehrplan zu Optik?` | Antwort weist darauf hin, dass kein Lehrplan hochgeladen ist | Regex |
| J04.4 | Richtiger Lehrplan genutzt | (Profil: Sachsen, Gymnasium) `Lehrplaninhalte für Physik Klasse 9` | Antwort referenziert sächsischen Gymnasium-Lehrplan, nicht z.B. NRW | LLM-Judge |

### Testset-Varianten für J04

```yaml
- prompt: "Was steht im Lehrplan zu Optik Klasse 8?"
  voraussetzung: Physik-Lehrplan Sachsen hochgeladen
- prompt: "Welche Kompetenzen für Elektrizitätslehre Klasse 9?"
  voraussetzung: Physik-Lehrplan Sachsen hochgeladen
- prompt: "Lehrplaninhalte für Pflege CE 01?"
  voraussetzung: Pflege-Lehrplan BIBB hochgeladen
```

---

## J05 — Unterrichtsstunde planen

> **Job:** "Wenn ich eine Stunde vorbereiten muss, möchte ich einen strukturierten Verlaufsplan erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J05.1 | Verlaufsplan mit Phasen | `Plane eine Doppelstunde zum Thema Elektrizität für Klasse 9` | Antwort enthält Phasen (Einstieg, Erarbeitung, Sicherung) mit Zeitangaben | Regex + LLM-Judge |
| J05.2 | Methodenvielfalt | (gleicher Prompt) | Mindestens 2 verschiedene Methoden genannt (z.B. Experiment + Partnerarbeit) | LLM-Judge |
| J05.3 | Zeitangaben summieren auf | (gleicher Prompt) | Summe der Minuten ≈ 90 (Doppelstunde) | Regex + Struktur |
| J05.4 | Lehrplanbezug | (Lehrkraft mit Lehrplan) gleicher Prompt | Antwort referenziert Lehrplaninhalte oder Kompetenzen | LLM-Judge |
| J05.5 | DOCX-Export | `Erstelle einen Verlaufsplan für Mathe Klasse 7, Bruchrechnung, 45 Minuten` | DOCX mit Tabelle (Phase / Zeit / Inhalt / Methode / Material) | Struktur |

---

## J06 — Sich Dinge merken (Memory)

> **Job:** "Wenn ich dem Assistenten etwas über mich oder meine Klassen erzähle, möchte ich, dass er sich das merkt und beim nächsten Mal nutzt."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J06.1 | Explizites Merken | Turn 1: `Merk dir: Klasse 8a hat Schwierigkeiten mit Bruchrechnung` | Antwort bestätigt das Speichern | Regex |
| J06.2 | Implizites Erkennen | Turn 1: `Ich unterrichte Mathe und Bio in Klasse 7` | Memory-Agent extrahiert Fächer + Klasse (DB-Check) | Struktur (DB) |
| J06.3 | Abruf in neuer Session | Session 1: J06.1 ausführen. Session 2: `Was weißt du über meine Klasse 8a?` | Antwort erwähnt Bruchrechnung-Schwierigkeiten | Roundtrip + Regex |
| J06.4 | Profilbasierter Kontext | Profil: Physik, Sachsen, Gymnasium. `Plane eine Stunde` | Antwort bezieht sich auf Physik + sächsischen Lehrplan (ohne dass Lehrkraft es nochmal sagt) | LLM-Judge |
| J06.5 | Memory beeinflusst Materialerstellung | Memories: "bevorzugt Gruppenarbeit". `Erstelle einen Verlaufsplan` | Verlaufsplan enthält Gruppenarbeit-Phasen | LLM-Judge |

---

## J07 — Elternkommunikation

> **Job:** "Wenn ich einen Brief an Eltern schreiben muss, möchte ich nur den Anlass nennen und einen fertigen, professionellen Brief erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J07.1 | Briefformat einhalten | `Schreibe einen Elternbrief für den Wandertag am 15. März` | Antwort enthält: Anrede, Datum, Betreff, Informationen, Unterschriftszeile | Regex + LLM-Judge |
| J07.2 | Formaler Ton | (gleicher Prompt) | Anrede "Liebe Eltern" oder "Sehr geehrte Eltern", Sie-Form durchgehend | LLM-Judge |
| J07.3 | Relevante Details | (gleicher Prompt) | Brief enthält: Datum, Uhrzeit/Treffpunkt, was mitbringen, Rücklaufzettel | LLM-Judge |
| J07.4 | Kontextanpassung | `Schreibe einen Elternbrief: Schülerin Lisa zeigt aggressives Verhalten` | Brief ist einfühlsam, sachlich, lösungsorientiert (nicht anklagend) | LLM-Judge |

---

## J08 — Bilder finden oder generieren

> **Job:** "Wenn ich ein Bild für Arbeitsblätter oder Präsentationen brauche, möchte ich es im Chat beschreiben und direkt erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J08.1 | Bildersuche (Stockfotos) | `Suche ein Bild vom Wasserkreislauf` | Antwort enthält Pixabay-Bildvorschau(en) mit Lizenzhinweis | Regex |
| J08.2 | Bildgenerierung (KI) | `Erstelle ein Bild: Schematische Darstellung einer Pflanzenzelle` | Antwort enthält generiertes Bild (image-card) | Regex |
| J08.3 | Bild iterieren | Turn 1: J08.2. Turn 2: `Mach den Zellkern größer und rot` | Neues Bild generiert, das die Änderung berücksichtigt | Roundtrip + LLM-Judge |
| J08.4 | Bild herunterladen | Bild-URL aus J08.2 abrufen | HTTP 200, Content-Type image/*, Datei > 10 KB | Struktur |

---

## J09 — Classroom-Tools (Live im Unterricht)

> **Job:** "Wenn ich im Unterricht spontan einen Timer, eine Abstimmung oder eine Zufallsauswahl brauche, möchte ich das direkt im Chat machen."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J09.1 | Timer stellen | `Stell einen Timer auf 5 Minuten` | Antwort enthält Timer-Indikator (`TIMER:300`) | Regex |
| J09.2 | Zufälligen Schüler wählen | `Wähle einen Schüler aus: Anna, Ben, Clara, David, Eva` | Antwort enthält genau einen der genannten Namen | Regex |
| J09.3 | Gruppen einteilen | `Teile diese Schüler in 3er-Gruppen ein: Anna, Ben, Clara, David, Eva, Finn` | Antwort enthält 2 Gruppen à 3 Personen, alle Namen zugeordnet | Regex + LLM-Judge |
| J09.4 | Abstimmung erstellen | `Erstelle eine Abstimmung: Welches Thema wollen wir vertiefen? Optionen: Optik, Mechanik, Elektrizität` | Antwort enthält Zugangscode + QR-Code + alle 3 Optionen | Regex |
| J09.5 | Würfeln | `Wirf 2 Würfel` | Antwort enthält 2 Zahlen zwischen 1-6 | Regex |

---

## J10 — Audio & Sprache

> **Job:** "Wenn ich einen Podcast oder Dialog für den Unterricht brauche, möchte ich das Thema beschreiben und ein fertiges Audio erhalten."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J10.1 | Podcast-Skript erstellen | `Erstelle einen Podcast zum Thema Klimawandel für Klasse 9, 5 Minuten` | Antwort enthält Skript mit mindestens 2 Sprecherrollen | Regex + LLM-Judge |
| J10.2 | Audio generieren | (gleicher Prompt, wenn TTS aktiv) | Audio-Datei verfügbar, Dauer > 60 Sekunden | Struktur |
| J10.3 | Gesprächssimulation | `Erstelle ein Arzt-Patienten-Gespräch zum Thema Diabetes für Pflege-Azubis` | Skript enthält Arzt- und Patientenrolle, medizinisch plausibel | LLM-Judge |
| J10.4 | YouTube-Quiz | `Erstelle ein Quiz zu diesem Video: [YouTube-URL]` | Antwort enthält Fragen basierend auf dem Videoinhalt | LLM-Judge |

---

## J11 — Kontextbewahrung (Multi-Turn)

> **Job:** "Wenn ich ein Gespräch mit dem Assistenten führe, möchte ich, dass er sich an alles erinnert, was ich in diesem Gespräch gesagt habe."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J11.1 | 2-Turn Kontext | T1: `Ich plane eine Stunde zu Optik für Klasse 8`. T2: `Erstelle dafür 3 Aufgaben` | Aufgaben beziehen sich auf Optik + Klasse 8 | Roundtrip + LLM-Judge |
| J11.2 | 5-Turn Kontext | T1-T5 aufbauendes Gespräch (siehe Testset) | Turn 5 referenziert korrekt alle vorherigen Turns | Roundtrip + LLM-Judge |
| J11.3 | Kontext nach 20+ Turns | 20 Nachrichten senden, dann `Fasse zusammen, woran wir gearbeitet haben` | Zusammenfassung enthält Kernthemen des Gesprächs | Roundtrip + LLM-Judge |
| J11.4 | Material-Iteration | T1: Klausur generieren. T2: `Ändere Aufgabe 2`. T3: `Füge eine AFB-III-Aufgabe hinzu` | Jeder Turn baut auf dem vorherigen auf | Roundtrip + LLM-Judge |

### Testset für J11.2 (5-Turn)

```yaml
turns:
  - "Ich plane eine Stunde zu Optik für Klasse 8"
  - "Was sind die Lernziele dafür laut Lehrplan?"
  - "Erstelle 3 Aufgaben dazu"
  - "Mach Aufgabe 2 schwieriger"
  - "Fasse zusammen, was wir besprochen haben"
prüfung_turn_5:
  - enthält "Optik"
  - enthält "Klasse 8"
  - referenziert die Aufgaben
  - referenziert die Änderung an Aufgabe 2
```

---

## J12 — Recherche & Wissensquellen

> **Job:** "Wenn ich aktuelle Informationen oder Fachinhalte brauche, möchte ich, dass der Assistent für mich recherchiert."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J12.1 | Web-Recherche | `Welche aktuellen Methoden gibt es für inklusiven Physikunterricht?` | Antwort enthält aktuelle Quellen/Links (URLs) | Regex |
| J12.2 | Wikipedia-Suche | `Erkläre den Doppler-Effekt` | Antwort enthält fachlich korrekte Erklärung mit Quellenangabe | LLM-Judge |
| J12.3 | Quellenangaben | `Recherchiere zum Thema Klimawandel im Unterricht` | Antwort enthält mindestens 1 URL oder Quellenreferenz | Regex |

---

## J13 — Todo-Verwaltung

> **Job:** "Wenn ich mir Aufgaben merken muss, möchte ich dem Assistenten sagen 'erinnere mich an...' und eine Liste führen."

| ID | Sub-Operation | Testset | Kriterium | Methode |
|----|---------------|---------|-----------|---------|
| J13.1 | Todo erstellen | `Erinnere mich daran, morgen die Klausuren zurückzugeben` | Antwort bestätigt Erstellung, enthält Todo-Text | Regex |
| J13.2 | Todo-Liste anzeigen | `Was steht auf meiner Todo-Liste?` | Antwort enthält todo-card mit allen offenen Todos | Regex |
| J13.3 | Todo abhaken | T1: Todo erstellen. T2: `Das mit den Klausuren ist erledigt` | Todo wird als erledigt markiert | Roundtrip + Struktur (DB) |
| J13.4 | Fälligkeitsdatum | `Erinnere mich bis Freitag an die Noten-Eingabe` | Todo hat due_date gesetzt | Struktur (DB) |

---

## Übergreifende Qualitätskriterien

Diese gelten für **alle** Jobs:

| ID | Kriterium | Beschreibung | Methode |
|----|-----------|-------------- |---------|
| Q01 | Sprache | Antwort ist auf Deutsch, professionell aber nahbar | LLM-Judge |
| Q02 | Keine Halluzinationen | Fakten sind korrekt, keine erfundenen Quellen/Gesetze/Formeln | LLM-Judge |
| Q03 | Rückfragen bei Unklarheit | Bei vagem Prompt fragt die KI nach statt zu raten | LLM-Judge |
| Q04 | Altersgerechte Sprache | Material für Klasse 5 klingt anders als für Klasse 12 | LLM-Judge |
| Q05 | Antwortzeit | < 30s für einfache Antworten, < 60s für Material-Generierung | Latenz |
| Q06 | Robustheit | System crasht nicht bei ungewöhnlichen Inputs | Struktur |

---

## Automatisierungs-Architektur (Vorschlag)

```
benchmark_runner.py
│
├── test_sets/                   # YAML-Dateien pro Job
│   ├── j01_klausur.yaml
│   ├── j02_differenzierung.yaml
│   ├── ...
│   └── quality_criteria.yaml
│
├── evaluators/
│   ├── regex_eval.py            # Pattern-Match
│   ├── structure_eval.py        # DOCX/JSON/DB Checks
│   ├── latency_eval.py          # Zeitmessung
│   ├── llm_judge_eval.py        # Zweites LLM bewertet
│   └── roundtrip_eval.py        # Multi-Turn Tests
│
├── reporters/
│   └── benchmark_report.py      # JSON + Markdown Report
│
└── run_benchmark.py             # CLI: python run_benchmark.py --jobs J01,J02 --env production
```

### Beispiel Testset-YAML

```yaml
# test_sets/j01_klausur.yaml
job: J01
name: "Klausur erstellen"
tests:
  - id: J01.1
    name: "AFB-Verteilung"
    prompt: "Erstelle eine Klausur für Physik Klasse 10, Thema Mechanik, 45 Minuten"
    teacher_profile:
      bundesland: Sachsen
      schulform: Gymnasium
      faecher: [Physik]
    evaluations:
      - type: regex
        pattern: "AFB\\s*(I|1)"
        description: "Enthält AFB I Aufgaben"
      - type: regex
        pattern: "AFB\\s*(II|2)"
        description: "Enthält AFB II Aufgaben"
      - type: regex
        pattern: "AFB\\s*(III|3)"
        description: "Enthält AFB III Aufgaben"
      - type: llm_judge
        rubric: |
          Bewerte ob die Klausur eine sinnvolle AFB-Verteilung hat:
          - ~30% Reproduktion (AFB I): Wissen wiedergeben, Formeln anwenden
          - ~40% Transfer (AFB II): Wissen anwenden, Zusammenhänge erkennen
          - ~30% Reflexion (AFB III): Bewerten, begründen, eigene Lösungswege
          Antworte mit PASS oder FAIL und kurzer Begründung.
      - type: latency
        max_ms: 60000
```

---

## Priorisierung für das Gespräch

### Tier 1 — Kern-Features (hiermit starten)

| Job | Warum Prio 1 |
|-----|--------------|
| **J01 Klausur** | Größter Zeitspareffekt, höchste Nutzernachfrage |
| **J02 Differenzierung** | Zentrales pädagogisches Versprechen |
| **J05 Stundenplanung** | Täglicher Bedarf |
| **J11 Kontextbewahrung** | Grundvoraussetzung für alle anderen Jobs |

### Tier 2 — Differenzierung zum Wettbewerb

| Job | Warum Prio 2 |
|-----|--------------|
| **J03 H5P-Übungen** | Einzigartiges Feature, hoher Schüler-Mehrwert |
| **J04 Lehrplan-RAG** | Curriculare Konformität, USP |
| **J06 Memory** | Personalisierung, Lock-in |

### Tier 3 — Ecosystem & Extras

| Job | Warum Prio 3 |
|-----|--------------|
| **J07 Elternbriefe** | Nice-to-have, schnell testbar |
| **J08 Bilder** | Abhängig von externen APIs |
| **J09 Classroom-Tools** | Live-Unterricht Feature |
| **J10 Audio** | Premium-Feature |
| **J12 Recherche** | Ergänzend |
| **J13 Todos** | Organisationshilfe |

---

## Nächste Schritte

1. **Team-Meeting:** Jobs J01-J13 durchgehen, Priorisierung bestätigen/anpassen
2. **Testsets schärfen:** Konkrete Prompts + Erwartungskriterien pro Job festlegen
3. **Benchmark-Runner bauen:** `run_benchmark.py` mit YAML-Testsets
4. **Erste Baseline messen:** Alle Tier-1-Jobs durchlaufen, Report generieren
5. **Iterieren:** Bei jeder Änderung Benchmark laufen lassen → Regression erkennen
