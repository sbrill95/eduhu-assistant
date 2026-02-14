# H5P Integration Recherche für eduhu-assistant

**Erstellt:** 14. Februar 2026  
**Autor:** AI-Assistent  
**Zweck:** Technische Evaluation für programmatische H5P-Erstellung und -Bereitstellung

---

## Executive Summary

H5P ist ein etabliertes Framework für interaktive HTML5-Lernmodule. Für eduhu-assistant ist die **programmatische Erstellung** (nicht nur Anzeige) von H5P-Inhalten entscheidend. 

**Kernerkenntnisse:**
- ✅ **Statisches Hosting möglich**: H5P kann via h5p-standalone auf Cloudflare Pages ohne Backend bereitgestellt werden
- ⚠️ **Keine Python-Bibliotheken**: Es gibt KEINE fertigen Python-Pakete für H5P-Generierung – manuelle ZIP-Erstellung erforderlich
- ✅ **JSON-basierte Struktur**: H5P-Dateien sind ZIP-Archive mit definierter Struktur, die programmatisch erstellt werden können
- 💡 **Beste Architektur**: FastAPI generiert H5P-ZIPs → Supabase Storage/Cloudflare R2 → Frontend mit h5p-standalone

---

## 1. H5P Dateiformat & Struktur

### 1.1 Was ist eine .h5p Datei?

Eine `.h5p`-Datei ist ein **umbenanntes ZIP-Archiv** mit folgender Struktur:

```
my-exercise.h5p (ZIP)
├── h5p.json                    # Package Definition (Metadaten)
├── content/
│   ├── content.json            # Eigentlicher Inhalt & Parameter
│   ├── images/                 # Medien (optional)
│   │   └── example.png
│   └── audios/                 # Audio-Dateien (optional)
├── H5P.MultiChoice-1.16/       # Content Type Library
│   ├── library.json
│   ├── semantics.json
│   ├── scripts/
│   │   └── multichoice.js
│   └── styles/
│       └── multichoice.css
├── H5P.Question-1.5/           # Dependency Library
│   ├── library.json
│   └── ...
└── FontAwesome-4.5/            # Weitere Dependencies
    └── ...
```

### 1.2 Die drei Kern-JSON-Dateien

#### **h5p.json** (Package Definition)

Definiert Metadaten und Library-Abhängigkeiten:

```json
{
  "title": "Multiple Choice Quiz",
  "language": "de",
  "mainLibrary": "H5P.MultiChoice",
  "embedTypes": ["div", "iframe"],
  "preloadedDependencies": [
    {
      "machineName": "H5P.MultiChoice",
      "majorVersion": 1,
      "minorVersion": 16
    },
    {
      "machineName": "H5P.Question",
      "majorVersion": 1,
      "minorVersion": 5
    }
  ],
  "license": "CC BY-SA",
  "authors": [
    {
      "name": "eduhu-assistant",
      "role": "Author"
    }
  ]
}
```

**Pflichtfelder:**
- `title` – Anzeigename
- `mainLibrary` – Haupt-Content-Type (z.B. "H5P.MultiChoice")
- `language` – ISO 639-1 Code (z.B. "de", "en")
- `preloadedDependencies` – Alle benötigten Libraries
- `embedTypes` – ["div"] oder ["iframe"]

#### **content/content.json** (Inhalt & Parameter)

Enthält die eigentlichen Fragen, Antworten, Einstellungen. Die Struktur ist **content-type-spezifisch**:

**Beispiel: Multiple Choice**
```json
{
  "media": {
    "type": {},
    "disableImageZooming": false
  },
  "answers": [
    {
      "correct": true,
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "Richtig! Python wurde 1991 von Guido van Rossum veröffentlicht.",
        "notChosenFeedback": ""
      },
      "text": "<div>1991</div>\n"
    },
    {
      "correct": false,
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "Falsch. Java wurde 1995 veröffentlicht.",
        "notChosenFeedback": ""
      },
      "text": "<div>1995</div>\n"
    },
    {
      "correct": false,
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "Falsch. Das wäre zu früh.",
        "notChosenFeedback": ""
      },
      "text": "<div>1985</div>\n"
    }
  ],
  "overallFeedback": [
    {
      "from": 0,
      "to": 50,
      "feedback": "Versuche es nochmal!"
    },
    {
      "from": 51,
      "to": 100,
      "feedback": "Gut gemacht!"
    }
  ],
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "type": "auto",
    "singlePoint": false,
    "randomAnswers": true,
    "showSolutionsRequiresInput": true,
    "confirmCheckDialog": false,
    "confirmRetryDialog": false,
    "autoCheck": false
  },
  "UI": {
    "checkAnswerButton": "Überprüfen",
    "showSolutionButton": "Lösung anzeigen",
    "tryAgainButton": "Nochmal versuchen",
    "tipsLabel": "Tipp anzeigen",
    "scoreBarLabel": "Du hast :num von :total Punkten erreicht",
    "tipAvailable": "Tipp verfügbar",
    "feedbackAvailable": "Feedback verfügbar",
    "readFeedback": "Feedback vorlesen",
    "wrongAnswer": "Falsche Antwort",
    "correctAnswer": "Richtige Antwort",
    "shouldCheck": "Hätte ausgewählt werden sollen",
    "shouldNotCheck": "Hätte nicht ausgewählt werden sollen",
    "noInput": "Bitte antworte, bevor du die Lösung ansiehst"
  },
  "confirmCheck": {
    "header": "Beenden?",
    "body": "Bist du sicher, dass du beenden möchtest?",
    "cancelLabel": "Abbrechen",
    "confirmLabel": "Beenden"
  },
  "confirmRetry": {
    "header": "Nochmal versuchen?",
    "body": "Bist du sicher, dass du nochmal versuchen möchtest?",
    "cancelLabel": "Abbrechen",
    "confirmLabel": "Bestätigen"
  },
  "question": "<p>Wann wurde Python erstmals veröffentlicht?</p>\n"
}
```

#### **library.json** (Library Definition)

Jede Library (Content Type oder Dependency) enthält eine `library.json`:

```json
{
  "title": "Multiple Choice",
  "description": "Multiple choice question",
  "machineName": "H5P.MultiChoice",
  "majorVersion": 1,
  "minorVersion": 16,
  "patchVersion": 5,
  "runnable": 1,
  "author": "Joubel",
  "license": "MIT",
  "preloadedJs": [
    {"path": "scripts/multichoice.js"}
  ],
  "preloadedCss": [
    {"path": "styles/multichoice.css"}
  ],
  "preloadedDependencies": [
    {
      "machineName": "H5P.Question",
      "majorVersion": 1,
      "minorVersion": 5
    }
  ]
}
```

### 1.3 Programmatische Erstellung (ohne H5P Editor)

**Schritt-für-Schritt:**

1. **Verzeichnisstruktur erstellen**
   ```python
   import os
   import json
   import zipfile
   from pathlib import Path
   
   def create_h5p_structure(output_dir):
       Path(output_dir).mkdir(parents=True, exist_ok=True)
       Path(f"{output_dir}/content").mkdir(exist_ok=True)
   ```

2. **h5p.json schreiben**
   ```python
   h5p_json = {
       "title": "My Quiz",
       "language": "de",
       "mainLibrary": "H5P.MultiChoice",
       "embedTypes": ["div"],
       "preloadedDependencies": [
           {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16}
       ]
   }
   with open(f"{output_dir}/h5p.json", "w", encoding="utf-8") as f:
       json.dump(h5p_json, f, ensure_ascii=False, indent=2)
   ```

3. **content/content.json schreiben**
   ```python
   content_json = {
       "question": "<p>Was ist 2+2?</p>",
       "answers": [
           {"correct": False, "text": "<div>3</div>"},
           {"correct": True, "text": "<div>4</div>"},
           {"correct": False, "text": "<div>5</div>"}
       ],
       "behaviour": {"enableRetry": True},
       "UI": {"checkAnswerButton": "Überprüfen"}
   }
   with open(f"{output_dir}/content/content.json", "w", encoding="utf-8") as f:
       json.dump(content_json, f, ensure_ascii=False, indent=2)
   ```

4. **Libraries hinzufügen**
   - **Problem:** Libraries (JS/CSS) müssen **manuell** aus offiziellen H5P-Releases kopiert werden
   - **Quellen:**
     - H5P.org: Beispiel-H5Ps herunterladen und extrahieren
     - GitHub: https://github.com/h5p/h5p-multichoice (Releases)
   
5. **ZIP erstellen (als .h5p)**
   ```python
   def create_h5p_zip(source_dir, output_file):
       with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
           for root, dirs, files in os.walk(source_dir):
               for file in files:
                   file_path = os.path.join(root, file)
                   arcname = os.path.relpath(file_path, source_dir)
                   zipf.write(file_path, arcname)
   
   create_h5p_zip("./my-h5p-content", "quiz.h5p")
   ```

**⚠️ Kritischer Punkt: Library-Verwaltung**

Es gibt **KEINE Python-Library**, die automatisch die benötigten H5P-Libraries (JS/CSS) herunterlädt oder einbindet. Du musst:
- Einmalig alle benötigten Content Types als .h5p von H5P.org herunterladen
- Die Library-Ordner extrahieren und in deinem Projekt vorhalten
- Beim Generieren die entsprechenden Libraries in das ZIP kopieren

---

## 2. H5P Content Types – JSON-Schemas

### 2.1 Multiple Choice (H5P.MultiChoice)

**GitHub:** https://github.com/h5p/h5p-multi-choice

**content.json Minimal-Beispiel:**
```json
{
  "question": "<p>Was ist die Hauptstadt von Deutschland?</p>",
  "answers": [
    {
      "correct": false,
      "text": "<div>München</div>",
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "Falsch",
        "notChosenFeedback": ""
      }
    },
    {
      "correct": true,
      "text": "<div>Berlin</div>",
      "tipsAndFeedback": {
        "tip": "",
        "chosenFeedback": "Richtig!",
        "notChosenFeedback": ""
      }
    }
  ],
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "type": "auto",
    "singlePoint": false,
    "randomAnswers": true
  },
  "UI": {
    "checkAnswerButton": "Überprüfen",
    "showSolutionButton": "Lösung",
    "tryAgainButton": "Nochmal"
  }
}
```

### 2.2 Fill in the Blanks (H5P.Blanks)

**GitHub:** https://github.com/h5p/h5p-blanks

**Syntax:** Lücken werden mit `*Antwort*` markiert, Alternativen mit `/`:

**content.json Beispiel:**
```json
{
  "text": "<p>Python wurde im Jahr *1991* von *Guido van Rossum/van Rossum* entwickelt.</p>",
  "overallFeedback": [
    {"from": 0, "to": 50, "feedback": "Versuche es nochmal!"},
    {"from": 51, "to": 100, "feedback": "Gut gemacht!"}
  ],
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "showSolutionsRequiresInput": true,
    "caseSensitive": false,
    "autoCheck": false
  },
  "checkAnswerButton": "Überprüfen",
  "tryAgainButton": "Nochmal",
  "showSolutionButton": "Lösung",
  "inputLabel": "Leeres Feld @num von @total"
}
```

**Hinweis:** Blanks verwendet eine **String-basierte Syntax** statt strukturierter JSON-Objekte für Lücken.

### 2.3 Drag and Drop (H5P.DragQuestion)

**GitHub:** https://github.com/h5p/h5p-drag-question

Ermöglicht Drag-and-Drop von Texten/Bildern auf Zonen in einem Hintergrundbild.

**content.json Struktur (vereinfacht):**
```json
{
  "scoreShow": "Zeige Punkte",
  "tryAgain": "Nochmal",
  "checkAnswer": "Überprüfen",
  "submitAnswer": "Abschicken",
  "question": {
    "settings": {
      "size": {
        "width": 620,
        "height": 310
      }
    },
    "task": {
      "elements": [
        {
          "x": 10,
          "y": 10,
          "width": 100,
          "height": 50,
          "dropZones": ["0"],
          "type": {
            "library": "H5P.AdvancedText 1.1",
            "params": {
              "text": "<div>Ziehbares Element</div>"
            }
          },
          "backgroundOpacity": 100
        }
      ],
      "dropZones": [
        {
          "x": 200,
          "y": 50,
          "width": 100,
          "height": 100,
          "correctElements": ["0"],
          "showLabel": true,
          "label": "<div>Ablage hier</div>"
        }
      ]
    }
  },
  "behaviour": {
    "enableRetry": true,
    "enableCheckButton": true,
    "singlePoint": false
  }
}
```

**⚠️ Komplex:** Drag & Drop erfordert präzise Positionsangaben und ist für programmatische Generierung aufwändig.

### 2.4 True/False (H5P.TrueFalse)

**GitHub:** https://github.com/h5p/h5p-true-false

**content.json Beispiel:**
```json
{
  "correct": "true",
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "confirmCheckDialog": false,
    "confirmRetryDialog": false
  },
  "l10n": {
    "trueText": "Wahr",
    "falseText": "Falsch",
    "score": "Du hast @score von @total Punkten",
    "checkAnswer": "Überprüfen",
    "showSolutionButton": "Lösung",
    "tryAgain": "Nochmal",
    "wrongAnswerMessage": "Falsche Antwort",
    "correctAnswerMessage": "Richtige Antwort",
    "scoreBarLabel": "Du hast :num von :total Punkten"
  },
  "question": "<p>Python ist eine kompilierte Sprache.</p>",
  "media": {
    "type": {}
  }
}
```

**Feld `correct`:** `"true"` oder `"false"` (String!)

### 2.5 Mark the Words (H5P.MarkTheWords)

**GitHub:** https://github.com/h5p/h5p-mark-the-words

Benutzer markieren korrekte Wörter in einem Text.

**content.json Beispiel:**
```json
{
  "textField": "<p>Python ist eine *interpretierte* Programmiersprache. Sie ist bekannt für ihre *einfache* Syntax.</p>",
  "overallFeedback": [
    {"from": 0, "to": 50, "feedback": "Versuche es nochmal!"},
    {"from": 51, "to": 100, "feedback": "Sehr gut!"}
  ],
  "checkAnswerButton": "Überprüfen",
  "tryAgainButton": "Nochmal",
  "showSolutionButton": "Lösung",
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "showScorePoints": true
  }
}
```

**Syntax:** Markierbare Wörter mit `*Wort*`.

### 2.6 Drag Text (H5P.DragText)

**GitHub:** https://github.com/h5p/h5p-drag-text

Wörter per Drag & Drop in Lücken ziehen.

**content.json Beispiel:**
```json
{
  "textField": "<p>Python wurde von *Guido van Rossum* entwickelt. Die erste Version erschien *1991*.</p>",
  "overallFeedback": [
    {"from": 0, "to": 100, "feedback": ""}
  ],
  "checkAnswer": "Überprüfen",
  "tryAgain": "Nochmal",
  "showSolution": "Lösung",
  "behaviour": {
    "enableRetry": true,
    "enableSolutionsButton": true,
    "enableCheckButton": true,
    "instantFeedback": false
  }
}
```

**Syntax:** Wie bei Blanks – `*Antwort*`.

---

## 3. H5P Player-Optionen

### 3.1 h5p-standalone (Empfohlen für statische Sites)

**GitHub:** https://github.com/tunapanda/h5p-standalone  
**NPM:** https://www.npmjs.com/package/h5p-standalone

**Vorteile:**
- ✅ Funktioniert **ohne Backend** (rein client-seitig)
- ✅ Kann auf **statischen Hosting** (Cloudflare Pages, Vercel, GitHub Pages) laufen
- ✅ Nur JavaScript + HTML (kein Node-Server nötig)
- ✅ Unterstützt alle gängigen H5P Content Types

**Installation (npm):**
```bash
npm install h5p-standalone
```

**Verwendung (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/h5p-standalone@3.8.0/dist/styles/h5p.css" />
  <script src="https://cdn.jsdelivr.net/npm/h5p-standalone@3.8.0/dist/main.bundle.js"></script>
</head>
<body>
  <div id="h5p-container"></div>

  <script>
    const { H5P } = H5PStandalone;
    
    new H5P(document.getElementById('h5p-container'), {
      h5pJsonPath: '/h5p-content/my-quiz',  // Pfad zum extrahierten H5P
      frameJs: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.8.0/dist/frame.bundle.js',
      frameCss: 'https://cdn.jsdelivr.net/npm/h5p-standalone@3.8.0/dist/styles/h5p.css'
    });
  </script>
</body>
</html>
```

**Wichtig:** Die .h5p-Datei muss **extrahiert** werden. Der Player lädt dann die Dateien aus dem entpackten Verzeichnis.

**React-Integration:**
```jsx
import { H5P } from 'h5p-standalone';
import { useEffect, useRef } from 'react';

function H5PPlayer({ contentId }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      new H5P(containerRef.current, {
        h5pJsonPath: `/h5p-content/${contentId}`,
        frameJs: '/assets/h5p/frame.bundle.js',
        frameCss: '/assets/h5p/styles/h5p.css'
      });
    }
  }, [contentId]);

  return <div ref={containerRef} />;
}
```

### 3.2 Lumi H5P (Desktop Editor + Server)

**Website:** https://lumi.education  
**GitHub:** https://github.com/Lumieducation/H5P-Nodejs-library

**Was ist Lumi?**
- Desktop-App zum **Erstellen** von H5P-Content (Alternative zum H5P-Editor)
- Node.js-Server-Library für H5P (Backend-Integration)

**Komponenten:**
- `@lumieducation/h5p-server` – H5P-Core für Node.js
- `@lumieducation/h5p-express` – Express-Integration
- `@lumieducation/h5p-react` – React-Komponenten für Player/Editor
- `@lumieducation/h5p-mongos3` – MongoDB + S3 Storage

**Eignung für eduhu-assistant:**
- ❌ **Zu komplex** für unseren Use Case (wir brauchen KEINEN Editor im Frontend)
- ✅ Könnte für Backend-Integration interessant sein (wenn wir User Editing später wollen)
- ⚠️ Erfordert Node.js-Backend (nicht Python)

### 3.3 h5p-php-library (Offiziell, aber PHP)

**GitHub:** https://github.com/h5p/h5p-php-library

**Eignung:**
- ❌ Nur PHP (nicht mit FastAPI/Python nutzbar)
- ✅ Offiziell unterstützt, vollständig
- ⚠️ Müsste komplett nach Python portiert werden (enormer Aufwand)

**Fazit:** Nicht relevant für uns.

---

## 4. Hosting & Serving H5P

### 4.1 Kann H5P auf statischen Sites laufen?

**JA!** Mit `h5p-standalone`:

**Bestätigt funktionierende Setups:**
- ✅ **Cloudflare Pages** (auch private Repos)
- ✅ **GitHub Pages**
- ✅ **Vercel**
- ✅ **Netlify**
- ✅ **Firebase Hosting**
- ✅ **Amazon S3 + CloudFront**

**Quelle:** https://www.animmouse.com/p/how-to-use-h5p-standalone/

**Beispiel-Repo:** https://github.com/AnimMouse/h5p-standalone-gh-pages-example

### 4.2 Minimal-Setup für Browser-Rendering

**Anforderungen:**
1. Extrahiertes H5P-Verzeichnis (mit h5p.json, content/, Libraries/)
2. h5p-standalone JavaScript laden
3. Container-DIV + Initialisierung

**Verzeichnisstruktur auf Server:**
```
/public
  /h5p-content
    /quiz-123
      h5p.json
      content/
        content.json
      H5P.MultiChoice-1.16/
        ...
  /assets
    /h5p
      frame.bundle.js
      styles/
        h5p.css
  index.html
```

**index.html:**
```html
<script src="/assets/h5p/main.bundle.js"></script>
<div id="h5p-container"></div>
<script>
  new H5PStandalone.H5P(document.getElementById('h5p-container'), {
    h5pJsonPath: '/h5p-content/quiz-123',
    frameJs: '/assets/h5p/frame.bundle.js',
    frameCss: '/assets/h5p/styles/h5p.css'
  });
</script>
```

**Kein Backend nötig!** Alle Dateien sind statisch.

### 4.3 Backend vs. Statisch

| Aspekt | Statisch (h5p-standalone) | Mit Backend (Lumi/PHP) |
|--------|---------------------------|------------------------|
| **Hosting** | Cloudflare Pages, S3, etc. | Node/PHP Server |
| **H5P Editor** | Nein | Ja |
| **User State Tracking** | Manuell (Custom-Code) | Eingebaut |
| **xAPI/LRS** | Manuell (JS-Hooks) | Eingebaut |
| **Content-Generierung** | Extern (Python) | Server-seitig |
| **Skalierung** | Unlimitiert (CDN) | Server-abhängig |

**Für eduhu-assistant:**
- ✅ Statisch ist **ideal** (Content wird von FastAPI generiert, aber Frontend ist statisch)
- ✅ h5p-standalone für Player
- ✅ Custom xAPI-Tracking via JavaScript (falls nötig)

---

## 5. Programmatische H5P-Generierung in Python

### 5.1 Gibt es Python-Bibliotheken?

**NEIN.** Es existiert **keine dedizierte Python-Library** für H5P-Generierung.

**Recherche-Ergebnisse:**
- Die offizielle H5P-Core-Library ist in **PHP** geschrieben
- Lumi bietet eine **Node.js/TypeScript**-Implementierung
- Für Python gibt es nur **manuelle Ansätze**

### 5.2 Manuelle Generierung in Python

**Strategie:**
1. JSON-Templates für Content Types erstellen
2. Daten vom LLM in JSON-Struktur überführen
3. H5P-ZIP manuell erstellen (mit `zipfile`)

**Code-Beispiel:**

```python
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any
import shutil

class H5PGenerator:
    def __init__(self, libraries_path: str):
        """
        :param libraries_path: Pfad zu extrahierten H5P-Libraries
        """
        self.libraries_path = Path(libraries_path)
    
    def create_multiple_choice(
        self,
        question: str,
        answers: List[Dict[str, Any]],
        output_file: str,
        title: str = "Multiple Choice Quiz"
    ):
        """
        Erstellt ein H5P Multiple Choice Quiz.
        
        :param question: Fragetext (HTML erlaubt)
        :param answers: Liste von Dicts mit {'text': str, 'correct': bool, 'feedback': str}
        :param output_file: Ausgabedatei (.h5p)
        :param title: Titel des Quiz
        """
        # Temporäres Arbeitsverzeichnis
        temp_dir = Path("./temp_h5p")
        temp_dir.mkdir(exist_ok=True)
        
        # h5p.json erstellen
        h5p_json = {
            "title": title,
            "language": "de",
            "mainLibrary": "H5P.MultiChoice",
            "embedTypes": ["div"],
            "preloadedDependencies": [
                {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
                {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5}
            ]
        }
        
        with open(temp_dir / "h5p.json", "w", encoding="utf-8") as f:
            json.dump(h5p_json, f, ensure_ascii=False, indent=2)
        
        # content/content.json erstellen
        content_dir = temp_dir / "content"
        content_dir.mkdir(exist_ok=True)
        
        formatted_answers = [
            {
                "correct": ans['correct'],
                "text": f"<div>{ans['text']}</div>",
                "tipsAndFeedback": {
                    "tip": "",
                    "chosenFeedback": ans.get('feedback', ''),
                    "notChosenFeedback": ""
                }
            }
            for ans in answers
        ]
        
        content_json = {
            "question": f"<p>{question}</p>",
            "answers": formatted_answers,
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": True,
                "enableCheckButton": True,
                "type": "auto",
                "singlePoint": False,
                "randomAnswers": True
            },
            "UI": {
                "checkAnswerButton": "Überprüfen",
                "showSolutionButton": "Lösung anzeigen",
                "tryAgainButton": "Nochmal versuchen"
            }
        }
        
        with open(content_dir / "content.json", "w", encoding="utf-8") as f:
            json.dump(content_json, f, ensure_ascii=False, indent=2)
        
        # Libraries kopieren
        required_libs = [
            "H5P.MultiChoice-1.16",
            "H5P.Question-1.5",
            "FontAwesome-4.5"
        ]
        
        for lib in required_libs:
            src = self.libraries_path / lib
            dst = temp_dir / lib
            if src.exists():
                shutil.copytree(src, dst)
            else:
                raise FileNotFoundError(f"Library not found: {src}")
        
        # ZIP erstellen
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Aufräumen
        shutil.rmtree(temp_dir)
        
        return output_file

# Verwendung
generator = H5PGenerator(libraries_path="./h5p-libraries")

generator.create_multiple_choice(
    question="Was ist die Hauptstadt von Deutschland?",
    answers=[
        {"text": "München", "correct": False, "feedback": "Falsch"},
        {"text": "Berlin", "correct": True, "feedback": "Richtig!"},
        {"text": "Hamburg", "correct": False, "feedback": "Falsch"}
    ],
    output_file="quiz.h5p",
    title="Hauptstädte-Quiz"
)
```

**Weitere Content Types:**

```python
def create_fill_in_blanks(self, text: str, output_file: str, title: str = "Lückentext"):
    """
    Lücken im Text mit *Antwort* markieren.
    Beispiel: "Python wurde *1991* veröffentlicht."
    """
    content_json = {
        "text": f"<p>{text}</p>",
        "behaviour": {
            "enableRetry": True,
            "enableSolutionsButton": True,
            "caseSensitive": False
        },
        "checkAnswerButton": "Überprüfen",
        "tryAgainButton": "Nochmal",
        "showSolutionButton": "Lösung"
    }
    # ... analog zu Multiple Choice

def create_true_false(self, question: str, correct: bool, output_file: str, title: str = "Wahr oder Falsch"):
    content_json = {
        "correct": "true" if correct else "false",
        "question": f"<p>{question}</p>",
        "behaviour": {"enableRetry": True},
        "l10n": {
            "trueText": "Wahr",
            "falseText": "Falsch",
            "checkAnswer": "Überprüfen"
        }
    }
    # ... analog
```

### 5.3 Library-Verwaltung

**Problem:** Woher kommen die H5P-Libraries (JS/CSS)?

**Lösung 1: Einmalig manuell herunterladen**
1. H5P.org besuchen: https://h5p.org/content-types-and-applications
2. Beispiel-Content für jeden benötigten Type herunterladen (.h5p)
3. .h5p → .zip umbenennen, extrahieren
4. Library-Ordner in `./h5p-libraries/` ablegen

**Lösung 2: H5P Hub API (theoretisch)**
- H5P.org bietet eine API zum Herunterladen von Libraries
- Nicht offiziell dokumentiert, nur für registrierte Hubs
- **Nicht empfohlen** (unreliable, keine Garantie)

**Empfehlung:**
- Einmalig alle benötigten Libraries (MultiChoice, Blanks, TrueFalse, etc.) herunterladen
- In Git-Repo committen (sie ändern sich selten)
- Bei Bedarf manuell aktualisieren

---

## 6. Alternative Ansätze

### 6.1 Option A: H5P JSON → h5p-standalone Player (Empfohlen)

**Flow:**
1. FastAPI Backend: Frage vom LLM generieren → H5P .h5p ZIP erstellen
2. Upload zu Supabase Storage / Cloudflare R2
3. Frontend: .h5p extrahieren (im Browser oder Build-Zeit)
4. h5p-standalone rendert Content

**Vorteile:**
- ✅ Volle H5P-Kompatibilität (exportierbar, wiederverwendbar)
- ✅ Standard-konform
- ✅ User kann H5P herunterladen und in Moodle/etc. importieren

**Nachteile:**
- ⚠️ Library-Abhängigkeiten müssen verwaltet werden
- ⚠️ .h5p-Dateien sind relativ groß (mit allen Libraries)

### 6.2 Option B: Eigene HTML5 Exercises (ohne H5P)

**Flow:**
1. FastAPI generiert React-Komponenten-JSON
2. Frontend rendert mit eigenem Quiz-Framework

**Vorteile:**
- ✅ Volle Kontrolle
- ✅ Kleinere Payloads
- ✅ Einfacher zu debuggen

**Nachteile:**
- ❌ Kein Standard (nicht exportierbar)
- ❌ Müssen alles selbst entwickeln (Scoring, Feedback, etc.)
- ❌ Kein Zugang zu H5P-Ecosystem

### 6.3 Option C: H5P Hub API (falls verfügbar)

**Status:** Nicht öffentlich verfügbar

Die H5P Hub API ist nur für registrierte Content Hubs (wie h5p.org selbst oder Lumi). Es gibt **keine öffentliche API** zum:
- Hochladen von programmatisch erstellten Inhalten
- Automatischen Download von Libraries

**Fazit:** Nicht nutzbar.

### 6.4 Empfehlung

Für eduhu-assistant: **Option A** (H5P mit h5p-standalone)

**Begründung:**
- Standard-konform → User können Inhalte exportieren
- Professionelle Darstellung
- Wiederverwendbar in anderen LMS
- Community-Support

---

## 7. Storage-Optionen

### 7.1 Supabase Storage

**Vorteile:**
- ✅ Bereits im Stack
- ✅ Einfache Integration mit FastAPI
- ✅ Kostenlos bis 1 GB (dann $0.021/GB)
- ✅ CDN inklusive

**Beispiel-Code (FastAPI):**
```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Upload .h5p
with open("quiz.h5p", "rb") as f:
    response = supabase.storage.from_("h5p-content").upload(
        path="quizzes/quiz-123.h5p",
        file=f,
        file_options={"content-type": "application/zip"}
    )

# Public URL
url = supabase.storage.from_("h5p-content").get_public_url("quizzes/quiz-123.h5p")
```

### 7.2 Cloudflare R2

**Vorteile:**
- ✅ Kostenlos bis 10 GB
- ✅ Kein Egress-Cost (Bandbreite gratis)
- ✅ S3-kompatibel

**Beispiel-Code:**
```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='https://<account-id>.r2.cloudflarestorage.com',
    aws_access_key_id='<R2_ACCESS_KEY>',
    aws_secret_access_key='<R2_SECRET_KEY>'
)

s3.upload_file('quiz.h5p', 'h5p-content', 'quizzes/quiz-123.h5p')
```

### 7.3 Direktes JSON-Serving (ohne .h5p)

**Idee:** Statt .h5p-Dateien nur die extrahierten Dateien hosten.

**Struktur:**
```
https://cdn.eduhu.com/h5p-content/
  quiz-123/
    h5p.json
    content/
      content.json
    H5P.MultiChoice-1.16/
      ...
```

**Vorteil:**
- ✅ Kein Entpacken nötig (h5p-standalone kann direkt auf Verzeichnis zeigen)

**Nachteil:**
- ⚠️ User kann Content nicht als .h5p herunterladen
- ⚠️ Viele kleine Dateien statt einer .h5p

**Empfehlung:**
- **Beides anbieten:**
  - .h5p für Download
  - Extrahiertes Verzeichnis für h5p-standalone

---

## 8. Architektur-Empfehlung für eduhu-assistant

### 8.1 Stack-Übersicht

**Backend:**
- Python FastAPI
- OpenAI/Anthropic für Content-Generierung
- Supabase PostgreSQL für Metadaten

**Frontend:**
- React (Vite)
- Cloudflare Pages

**Storage:**
- Supabase Storage oder Cloudflare R2

### 8.2 Empfohlene Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                         USER REQUEST                        │
│         "Erstelle ein Quiz zu Python Basics"                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│  1. LLM prompt: "Generate 5 multiple choice questions..."   │
│  2. Parse LLM response → JSON                               │
│  3. H5PGenerator.create_multiple_choice(...)                │
│  4. Upload .h5p zu Supabase Storage                         │
│  5. Extrahiere .h5p in /public/h5p-content/<id>/            │
│  6. Return: {id, title, url, extracted_path}                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Supabase Storage                          │
│  /h5p-files/quiz-123.h5p              (Download)            │
│  /h5p-content/quiz-123/...            (Extracted)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               React Frontend (Cloudflare Pages)             │
│  import { H5P } from 'h5p-standalone';                      │
│                                                             │
│  new H5P(containerRef.current, {                            │
│    h5pJsonPath: '/h5p-content/quiz-123',                    │
│    frameJs: '/h5p-assets/frame.bundle.js',                  │
│    frameCss: '/h5p-assets/styles/h5p.css'                   │
│  });                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Detaillierter Workflow

#### Backend (FastAPI)

**1. Content-Generierung**
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Du bist ein Experte für Lernmaterialien."},
        {"role": "user", "content": """
Erstelle 5 Multiple-Choice-Fragen zu Python Basics.
Format:
{
  "questions": [
    {
      "question": "...",
      "answers": [
        {"text": "...", "correct": true/false, "feedback": "..."}
      ]
    }
  ]
}
"""}
    ],
    response_format={"type": "json_object"}
)

questions_data = json.loads(response.choices[0].message.content)
```

**2. H5P-Generierung**
```python
from h5p_generator import H5PGenerator

generator = H5PGenerator(libraries_path="./h5p-libraries")

h5p_file = f"quiz-{uuid.uuid4()}.h5p"
generator.create_multiple_choice(
    question=questions_data['questions'][0]['question'],
    answers=questions_data['questions'][0]['answers'],
    output_file=h5p_file
)
```

**3. Upload & Extraktion**
```python
# Upload .h5p
with open(h5p_file, "rb") as f:
    supabase.storage.from_("h5p-files").upload(h5p_file, f)

# Extrahiere für h5p-standalone
import zipfile
extract_path = f"./public/h5p-content/{quiz_id}"
with zipfile.ZipFile(h5p_file, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Upload extrahierte Dateien
for file in Path(extract_path).rglob('*'):
    if file.is_file():
        rel_path = file.relative_to("./public")
        supabase.storage.from_("h5p-content").upload(
            str(rel_path),
            file.read_bytes()
        )
```

#### Frontend (React)

**H5PPlayer Komponente:**
```tsx
import { useEffect, useRef } from 'react';
import { H5P } from 'h5p-standalone';

interface H5PPlayerProps {
  contentId: string;
}

export function H5PPlayer({ contentId }: H5PPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const player = new H5P(containerRef.current, {
      h5pJsonPath: `https://cdn.eduhu.com/h5p-content/${contentId}`,
      frameJs: '/h5p-assets/frame.bundle.js',
      frameCss: '/h5p-assets/styles/h5p.css',
      
      // Optional: xAPI Event Tracking
      // (wird später für Analytics benötigt)
    });

    // Cleanup
    return () => {
      // H5P cleanup if needed
    };
  }, [contentId]);

  return (
    <div className="h5p-player-wrapper">
      <div ref={containerRef} />
    </div>
  );
}
```

**Download-Button:**
```tsx
function DownloadH5P({ contentId }: { contentId: string }) {
  const handleDownload = () => {
    window.open(
      `https://cdn.eduhu.com/h5p-files/${contentId}.h5p`,
      '_blank'
    );
  };

  return (
    <button onClick={handleDownload}>
      📥 Als H5P herunterladen (für Moodle/LMS)
    </button>
  );
}
```

### 8.4 Deployment-Strategie

**Cloudflare Pages Build:**
```bash
# package.json
{
  "scripts": {
    "build": "vite build",
    "postbuild": "node scripts/copy-h5p-assets.js"
  }
}
```

**scripts/copy-h5p-assets.js:**
```javascript
// h5p-standalone Dateien nach /public/h5p-assets kopieren
const fs = require('fs-extra');
const path = require('path');

const source = path.join(__dirname, '../node_modules/h5p-standalone/dist');
const dest = path.join(__dirname, '../dist/h5p-assets');

fs.copySync(source, dest);
console.log('✅ H5P assets copied');
```

### 8.5 Kosten-Schätzung

**Annahme:** 1000 generierte H5P-Inhalte/Monat

| Service | Kosten |
|---------|--------|
| **Supabase Storage** (1 GB) | $0 (Free Tier) |
| **Cloudflare Pages** | $0 (Free Tier) |
| **Cloudflare R2** (10 GB) | $0 (Free Tier) |
| **Bandbreite** (Cloudflare) | $0 (unlimitiert) |
| **FastAPI Hosting** (Fly.io/Railway) | ~$5-10/Monat |

**Gesamt: ~$5-10/Monat** (ohne LLM-Kosten)

---

## 9. Implementierungs-Roadmap

### Phase 1: Proof of Concept (1-2 Wochen)

**Ziele:**
- [x] H5P-Dateiformat verstehen
- [ ] Manuelle Erstellung eines Multiple Choice H5P
- [ ] h5p-standalone lokal zum Laufen bringen
- [ ] Python-Script für einfache Multiple Choice Generierung

**Deliverables:**
- Funktionierendes lokales Setup mit h5p-standalone
- Python-Script, das valide .h5p erstellt

### Phase 2: Backend-Integration (2-3 Wochen)

**Ziele:**
- [ ] H5PGenerator-Klasse (Multiple Choice, True/False, Fill in Blanks)
- [ ] FastAPI-Endpoint: `/api/generate-quiz`
- [ ] Supabase Storage Integration
- [ ] Library-Verwaltung (Versionierung)

**Deliverables:**
- API Endpoint, der LLM-Input → .h5p konvertiert
- Upload zu Supabase

### Phase 3: Frontend-Integration (2 Wochen)

**Ziele:**
- [ ] React H5PPlayer-Komponente
- [ ] Quiz-Übersichtsseite
- [ ] Download-Funktion
- [ ] Responsive Design

**Deliverables:**
- Funktionierende Quiz-Anzeige im Frontend
- User kann H5P herunterladen

### Phase 4: Erweiterte Features (3-4 Wochen)

**Ziele:**
- [ ] Weitere Content Types (Drag Text, Mark the Words)
- [ ] xAPI-Event-Tracking (für Analytics)
- [ ] User Progress Speicherung
- [ ] Quiz-Serien (Question Set)

**Deliverables:**
- Vollständiges Feature-Set
- Analytics-Dashboard

### Phase 5: Testing & Launch (1-2 Wochen)

**Ziele:**
- [ ] Cross-Browser-Tests
- [ ] Performance-Optimierung
- [ ] Dokumentation
- [ ] Beta-Launch

---

## 10. Offene Fragen & Risiken

### Offene Fragen

1. **Library-Updates:** Wie gehen wir mit H5P-Library-Updates um?
   - **Lösung:** Versionierung im Repo, quarterly Updates

2. **User-generierte Inhalte:** Sollen User selbst H5P erstellen können?
   - **Entscheidung ausstehend** (benötigt Lumi Editor-Integration)

3. **Offline-Fähigkeit:** Sollen H5P auch offline funktionieren?
   - **Lösung:** Service Worker + Cache API (später)

### Risiken

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| H5P-Libraries ändern Format | Niedrig | Hoch | Library-Versionen einfrieren |
| h5p-standalone wird nicht mehr maintained | Mittel | Hoch | Fork erstellen, selbst hosten |
| Browser-Inkompatibilitäten | Niedrig | Mittel | Polyfills, Testing |
| Zu große Dateigrößen (.h5p) | Mittel | Niedrig | Nur benötigte Libraries einbinden |

---

## 11. Nützliche Links

**Offizielle Dokumentation:**
- H5P Developer Guide: https://h5p.org/documentation/developers
- H5P Specification: https://h5p.org/documentation/developers/h5p-specification
- Semantics Definition: https://h5p.org/semantics

**Tools:**
- h5p-standalone: https://github.com/tunapanda/h5p-standalone
- Lumi H5P: https://lumi.education
- H5P Examples: https://h5p.org/content-types-and-applications

**GitHub Repositories:**
- H5P MultiChoice: https://github.com/h5p/h5p-multi-choice
- H5P Blanks: https://github.com/h5p/h5p-blanks
- H5P TrueFalse: https://github.com/h5p/h5p-true-false
- H5P MarkTheWords: https://github.com/h5p/h5p-mark-the-words
- H5P DragText: https://github.com/h5p/h5p-drag-text

**Tutorials:**
- Hosting on Static Sites: https://www.animmouse.com/p/how-to-use-h5p-standalone/
- Example Setup: https://github.com/AnimMouse/h5p-standalone-gh-pages-example

---

## 12. Fazit

### ✅ Was funktioniert

1. **H5P kann programmatisch erstellt werden** (manuell via Python)
2. **Statisches Hosting ist möglich** (Cloudflare Pages + h5p-standalone)
3. **Standard-konforme Inhalte** (exportierbar, wiederverwendbar)
4. **Skalierbar** (CDN-basiert)

### ⚠️ Herausforderungen

1. **Keine Python-Library** → Manuelle Implementierung nötig
2. **Library-Verwaltung** → Einmalig Setup, dann stabil
3. **Komplexe Content Types** (Drag & Drop) → Aufwändig zu generieren

### 💡 Empfehlung

**Für eduhu-assistant ist H5P mit h5p-standalone die beste Wahl:**

**Pro:**
- ✅ Professionell & bewährt
- ✅ Exportierbar (Moodle, etc.)
- ✅ Kein Backend nötig (statisches Hosting)
- ✅ Große Community

**Contra:**
- ⚠️ Initiale Lernkurve (JSON-Schemas)
- ⚠️ Library-Management erforderlich

**Alternative:** Falls H5P zu komplex wird, können wir immer noch auf eigene React-Komponenten ausweichen – aber der Standard-konforme Ansatz ist langfristig wertvoller.

---

**Status:** Ready for Implementation  
**Nächste Schritte:** Phase 1 PoC starten
