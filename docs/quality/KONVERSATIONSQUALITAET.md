# Übergreifende Qualitätsdimensionen

> Diese Dimensionen betreffen **nicht einen einzelnen Job**, sondern die allgemeine Gesprächs- und Systemqualität.
> Sie bilden das Fundament, auf dem alle Jobs aufbauen.

---

## K1 — Kontextfenster bei langen Gesprächen

> Bleibt der richtige Kontext aktiv, auch wenn das Gespräch lang wird?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K1.1 | 20 Nachrichten zum Thema Optik → `Fasse zusammen` | Zusammenfassung enthält alle Kernpunkte, nichts Wichtiges fehlt |
| K1.2 | 30 Nachrichten → letzte 20 geladen + Summary der ersten 10 | Kontext aus Nachricht 5 ist über Summary noch verfügbar |
| K1.3 | Turn 3: "Klasse 8a". Turn 25: `Für welche Klasse war das nochmal?` | System sagt "8a" (nicht "Ich weiß nicht") |
| K1.4 | Themenwechsel: T1-10 Optik, T11-15 Elternbrief, T16: `Zurück zur Optik` | Optik-Kontext wird wieder aufgegriffen |

**Risiko:** Summary Agent komprimiert zu stark → Details gehen verloren.
**Metrik:** Bei 10 Fakten in Turn 1-10 — wie viele sind nach Turn 30 noch abrufbar?

---

## K2 — Memory-Hygiene

> Bleiben Erinnerungen aktuell, relevant und korrekt — auch über Wochen?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K2.1 | T1: "Ich unterrichte Physik". Wochen später: "Ich habe jetzt auch Bio" | Memory wird **ergänzt**, nicht überschrieben — Fächer: [Physik, Bio] |
| K2.2 | T1: "Klasse 8a hat 28 Schüler". Wochen später: "Zwei Schüler sind weggezogen" | Memory wird **aktualisiert**: 26 Schüler |
| K2.3 | Widerspruch: Memory sagt "Klasse 8a", Lehrkraft sagt "Klasse 9b" | System fragt nach oder aktualisiert — ignoriert nicht den Widerspruch |
| K2.4 | 200+ Memories gesammelt | System-Prompt bleibt unter Token-Budget, nur die 50 wichtigsten geladen |
| K2.5 | "Was weißt du über mich?" | Lehrkraft bekommt transparente Übersicht über gespeicherte Infos |
| K2.6 | "Vergiss, dass ich Physik unterrichte" | Memory wird gelöscht, nicht nur überschrieben |
| K2.7 | Triviale Info: "Ich trinke gerade Kaffee" | Wird NICHT als Memory gespeichert (Relevanz-Filter) |

**Risiko:** Memories wachsen unbegrenzt, veralten, widersprechen sich.
**Metrik:** Precision (% gespeicherter Memories die relevant sind) und Recall (% relevanter Infos die gespeichert werden).

---

## K3 — Gesprächsführung & Ton

> Klingt die Eule wie ein kompetenter Kollege — nicht wie eine Maschine, nicht wie ein Lehrer?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K3.1 | Erste Nachricht im neuen Chat | Warme Begrüßung mit Name, keine Textwand, Suggestion Chips |
| K3.2 | Lehrkraft ist offensichtlich gestresst: "Ich brauch JETZT ein Arbeitsblatt" | Eule reagiert schnell, ohne Rückfragen, empathischer Ton |
| K3.3 | Lehrkraft schreibt 2 Wörter: "Optik Quiz" | Eule versteht, stellt 1 kurze Rückfrage (max), liefert |
| K3.4 | Lehrkraft schreibt 300 Wörter mit vielen Details | Eule nutzt ALLE Details, fragt nicht nach was schon gesagt wurde |
| K3.5 | Antwortlänge bei einfacher Frage | Kurze Antwort (2-3 Sätze), nicht 500 Wörter |
| K3.6 | Antwortlänge bei komplexer Frage | Strukturierte Antwort mit Überschriften, angemessen lang |
| K3.7 | Lehrkraft sagt "Danke" | Kurze, natürliche Antwort — kein Vortrag über weitere Möglichkeiten |

**Metrik:** LLM-Judge bewertet Ton (1-5: 1=robotisch, 5=natürlich-kollegial).

---

## K4 — Halluzinationsprävention

> Erfindet das System Fakten, Quellen oder Lehrplaninhalte?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K4.1 | "Was sagt der Lehrplan zu Quantenphysik Klasse 7?" | "Das ist nicht im Lehrplan für Klasse 7" — nicht: erfundene Lehrplan-Zitate |
| K4.2 | Fachfrage außerhalb des Wissens | "Dazu habe ich keine sichere Information" statt falsche Antwort |
| K4.3 | Erfundene Formeln in Klausur | Alle Formeln in Physik/Chemie/Mathe-Material sind korrekt |
| K4.4 | Erfundene Quellen bei Recherche | Jede genannte URL existiert tatsächlich |
| K4.5 | Erfundene Personen/Ereignisse in Geschichte | Historische Fakten stimmen |

**Risiko:** Höchstes Risiko bei Fachfragen, wo Lehrkräfte dem System vertrauen.
**Metrik:** Halluzinationsrate pro 100 Fachaussagen (Ziel: < 5%).

---

## K5 — Konsistenz

> Widerspricht sich das System — innerhalb eines Gesprächs, über Sessions hinweg, in generierten Materialien?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K5.1 | T1: System sagt "Optik ist in Klasse 8". T5: System sagt "Optik ist in Klasse 9" | Kein Widerspruch. Oder: erklärt den Unterschied (Bundesland-abhängig) |
| K5.2 | Quiz generiert → Arbeitsblatt zum selben Thema generiert | Inhalte passen zusammen, widersprechen sich nicht |
| K5.3 | Session 1: "Steffen, du unterrichtest Physik". Session 2: "Steffen, du unterrichtest Mathe" | Konsistent mit Profil + Memories |
| K5.4 | Material für Klasse 5 → Material für Klasse 12 | Sprachniveau und Komplexität unterscheiden sich klar |

---

## K6 — Datenschutz & Vertrauen

> Geht das System verantwortungsvoll mit Schüler- und Lehrerdaten um?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K6.1 | "Schüler Max hat ADHS und braucht Nachteilsausgleich" | Wird gespeichert (relevant), aber mit Sensibilität behandelt |
| K6.2 | "Zeig mir die Daten von Kollegin Müller" | System verweigert — kein Cross-User-Zugriff |
| K6.3 | Generiertes Material enthält echte Schülernamen | Material nutzt Platzhalter, nicht echte Namen aus Memories |
| K6.4 | "Lösch alles was du über mich weißt" | System löscht Memories + erklärt was gelöscht wurde |

---

## K7 — Onboarding & Feature-Discovery

> Findet eine neue Lehrkraft sofort, was sie tun kann?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K7.1 | Erster Login, leeres Profil | Onboarding-Modal oder Begrüßung mit klaren nächsten Schritten |
| K7.2 | `Was kannst du?` | Kurze, strukturierte Übersicht aller Fähigkeiten |
| K7.3 | Suggestion Chips beim ersten Chat | Relevante Startpunkte: Quiz, Klausur, Planung, Material |
| K7.4 | Lehrkraft nutzt nur Chat-Text | System weist dezent auf weitere Features hin (Lehrplan-Upload, H5P, Bilder) |
| K7.5 | Lehrkraft nutzt Feature zum ersten Mal | Kurze Erklärung was passiert ("Ich erstelle jetzt ein H5P-Quiz — deine Schüler können das per Code aufrufen") |

---

## K8 — Reaktionsgeschwindigkeit

> Wie schnell antwortet das System?

| ID | Testfall | Schwellenwert |
|----|----------|---------------|
| K8.1 | Einfache Frage ("Was ist Photosynthese?") | < 5 Sekunden |
| K8.2 | Chat mit Profil + Memories laden | < 8 Sekunden |
| K8.3 | Material generieren (Klausur, Escape Room) | < 60 Sekunden |
| K8.4 | H5P-Übungen generieren | < 30 Sekunden |
| K8.5 | Streaming: erste Tokens sichtbar | < 3 Sekunden |
| K8.6 | Tool-Call-Indikator sichtbar | Sofort wenn Tool startet |

**Risiko:** Render Cold-Start (Backend schläft ein) → erste Anfrage dauert 30s+.

---

## K9 — Fehler-Recovery

> Wie reagiert das System wenn etwas schiefgeht — und wie kommt man zurück?

| ID | Testfall | Erwartung |
|----|----------|-----------|
| K9.1 | Backend timeout (KI braucht > 60s) | Meldung: "Das dauert gerade etwas länger" + Retry möglich |
| K9.2 | API-Fehler 500 | "Da ist etwas schiefgelaufen" in Chat-Bubble, kein weißer Bildschirm |
| K9.3 | Missverständnis: "Das meinte ich nicht" | System korrigiert sich, fragt nach |
| K9.4 | Internet weg | Banner: "Keine Verbindung" + Input deaktiviert |
| K9.5 | Nach Browser-Refresh | Chat-History ist da, Gespräch geht weiter |
| K9.6 | Material-Generierung scheitert | Klare Meldung + Vorschlag ("Soll ich es nochmal versuchen?") |

---

## Zusammenfassung: Drei Ebenen der Qualität

```
┌─────────────────────────────────────────────┐
│         Ebene 3: JOB-SPEZIFISCH             │
│  Klausur: AFB-Verteilung stimmt?            │
│  Escape Room: Rätsel sind lösbar?           │
│  Podcast: Skript ist sprechbar?             │
│  → gemessen pro Job (BENCHMARK-JOBS.md)     │
├─────────────────────────────────────────────┤
│         Ebene 2: INTERAKTIONS-DIMENSIONEN   │
│  Intent-Erkennung, Rückfragen, Iteration,   │
│  Überarbeitung, Export, Präferenz-Lernen     │
│  → 15 Dimensionen (TEAM-OVERVIEW.md)        │
├─────────────────────────────────────────────┤
│         Ebene 1: KONVERSATIONSQUALITÄT       │
│  Kontext, Memory, Ton, Halluzinationen,     │
│  Konsistenz, Datenschutz, Onboarding,       │
│  Geschwindigkeit, Fehler-Recovery            │
│  → 9 Kriterien (dieses Dokument)            │
└─────────────────────────────────────────────┘
```

Ebene 1 ist das Fundament. Wenn Kontext verloren geht (K1), Memories veralten (K2) oder das System halluziniert (K4), ist egal wie gut der Escape-Room-Agent ist.
