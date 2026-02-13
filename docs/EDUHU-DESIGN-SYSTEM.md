# eduhu Design System — abgeleitet aus Teaser Deck

## Brand Identity

- **Name:** eduhu (immer lowercase)
- **Maskottchen:** Eule 🦉 — integriert in Logo-Buchstabe "u"
- **Ton:** Warm, professionell, einladend — nie kalt oder technisch

---

## Farbpalette

### Primärfarben

| Rolle | Farbe | Hex | Tailwind |
|---|---|---|---|
| **Primary / Accent** | Burnt Orange | `#C8552D` | `primary` |
| **Primary Hover** | Dunkleres Orange | `#A8461F` | `primary-hover` |
| **Primary Soft** | Helles Peach | `#FADDD0` | `primary-soft` |

### Textfarben

| Rolle | Farbe | Hex | Tailwind |
|---|---|---|---|
| **Text Primary** | Dunkelbraun | `#2D2018` | `text-primary` |
| **Text Secondary** | Graubraun | `#6B6360` | `text-secondary` |
| **Text Muted** | Hellgrau | `#9E9A96` | `text-muted` |
| **Text on Dark** | Weiß | `#FFFFFF` | `text-on-dark` |

### Hintergründe

| Rolle | Farbe | Hex | Tailwind |
|---|---|---|---|
| **Page Background** | Warmes Creme | `#F5F0EB` | `bg-page` |
| **Card Background** | Weiß | `#FFFFFF` | `bg-card` |
| **Card Dark** | Dunkelbraun | `#3A2E2A` | `bg-card-dark` |
| **Subtle Background** | Helles Warmgrau | `#F0EDEA` | `bg-subtle` |

### Akzent / Status

| Rolle | Farbe | Hex |
|---|---|---|
| **Success** | Gedämpftes Grün | `#4A8C5C` |
| **Error** | Warmes Rot | `#C0392B` |
| **Warning** | Bernstein | `#D4872A` |

---

## Typografie

### Font-Familie
- **Headlines:** Sans-Serif, bold — empfohlen: **Inter** oder **DM Sans**
- **Body:** Gleiche Font-Familie, regular/medium weight
- **Monospace:** Für Code/Daten — `JetBrains Mono` oder `Fira Code`

### Größen-Hierarchie

| Ebene | Größe | Gewicht | Verwendung |
|---|---|---|---|
| **Section Label** | 12-14px | Semibold, UPPERCASE, letter-spacing 0.1em | Kategorien ("PROBLEM", "LÖSUNG") |
| **H1 / Page Title** | 32-40px | Bold/Black | Seitenüberschriften |
| **H2 / Section Title** | 24-28px | Bold | Abschnittsüberschriften |
| **H3 / Card Title** | 18-20px | Semibold | Kartentitel |
| **Body** | 14-16px | Regular (400) | Fließtext |
| **Body Small** | 12-13px | Regular | Fußnoten, Timestamps |
| **Stat / Hero Number** | 48-80px | Black (900) | Große Kennzahlen |

---

## Komponenten

### Cards

```
Standard Card:
- Background: weiß (#FFFFFF)
- Border-Radius: 16px
- Shadow: 0 2px 8px rgba(0,0,0,0.06)
- Padding: 24px
- Kein Border (Shadow statt Rand)

Dark Card:
- Background: #3A2E2A
- Text: weiß
- Gleicher Radius + Padding

Accent Card:
- Background: #C8552D
- Text: weiß
- Für Highlights / CTAs
```

### Buttons

```
Primary Button:
- Background: #C8552D
- Text: weiß, semibold
- Border-Radius: 14px
- Padding: 12px 24px
- Hover: #A8461F
- Transition: 150ms ease

Secondary / Outline Button:
- Background: transparent
- Border: 1.5px solid #C8552D
- Text: #C8552D
- Hover: Background #FADDD0

Ghost Button:
- Background: #FADDD0 (Primary Soft)
- Text: #C8552D
- Kein Border
- Für weniger prominente Actions

Button mit Pfeil:
- Text + " →" suffix
- Verwendet in Listen als Action-Link
```

### Inputs

```
Text Input / Textarea:
- Background: #FFFFFF
- Border: 1.5px solid #D9D3CD
- Border-Radius: 14px
- Padding: 12px 16px
- Focus: Border #C8552D, ring 2px #FADDD0
- Placeholder: #9E9A96
```

### Navigation (Bottom Tab Bar)

```
- 4 Tabs: Home, Material, Routinen, Profil
- Aktiv: Icon + Text in Primary (#C8552D)
- Inaktiv: Icon + Text in Muted (#9E9A96)
- Background: weiß mit top-border 1px #F0EDEA
```

### Listen-Items

```
- Pfeil-Bullet: "→" in Primary-Farbe als Aufzählungszeichen
- Oder: Checkbox-Circle in Primary (#C8552D) mit weißem Haken
- Spacing: 12px zwischen Items
```

### Section Labels

```
- Text: UPPERCASE
- Farbe: Primary (#C8552D)
- Font-Size: 12-14px
- Letter-Spacing: 0.1em
- Font-Weight: 600 (Semibold)
- Immer ÜBER der Headline
```

---

## Layout-Prinzipien

1. **Großzügiger Whitespace** — Mindestens 24px Padding in Cards, 16-24px zwischen Elementen
2. **Warme Töne** — Nie kalt-grau, immer warm (Creme, Braun, Orange)
3. **Card-First** — Inhalte in Cards gruppieren, nicht lose auf der Seite
4. **Klare Hierarchie** — Section Label → Headline → Content → Actions
5. **Mobile-First** — Smartphone ist Hauptdevice der Nutzer (Lehrer + Schüler)
6. **Eule als Personality** — Das Maskottchen erscheint als Avatar in Chat/KI-Interaktionen

---

## Abstände (Spacing Scale)

| Token | Wert | Verwendung |
|---|---|---|
| `xs` | 4px | Inline-Spacing |
| `sm` | 8px | Enge Abstände |
| `md` | 16px | Standard-Gap |
| `lg` | 24px | Card-Padding, Section-Gap |
| `xl` | 32px | Zwischen Sektionen |
| `2xl` | 48px | Seiten-Margin |

---

## Border Radius

| Element | Radius |
|---|---|
| Cards | 16px |
| Buttons | 14px |
| Inputs | 14px |
| Avatare / Icons | 50% (rund) |
| Tags / Badges | 8px |
| Bottom Sheet | 24px (top only) |

---

## Schatten

| Ebene | Wert | Verwendung |
|---|---|---|
| **Subtle** | `0 1px 3px rgba(0,0,0,0.04)` | Hover-States |
| **Card** | `0 2px 8px rgba(0,0,0,0.06)` | Standard-Cards |
| **Elevated** | `0 4px 16px rgba(0,0,0,0.10)` | Modale, Dropdowns |

---

## Tailwind Config (Vorschlag)

```js
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#C8552D',
          hover: '#A8461F',
          soft: '#FADDD0',
        },
        text: {
          primary: '#2D2018',
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
        },
        success: '#4A8C5C',
        error: '#C0392B',
        warning: '#D4872A',
      },
      borderRadius: {
        card: '16px',
        btn: '14px',
        input: '14px',
        badge: '8px',
        sheet: '24px',
      },
      boxShadow: {
        subtle: '0 1px 3px rgba(0,0,0,0.04)',
        card: '0 2px 8px rgba(0,0,0,0.06)',
        elevated: '0 4px 16px rgba(0,0,0,0.10)',
      },
    },
  },
}
```

---

## Do's & Don'ts

### ✅ Do
- Warme Farben verwenden (Creme, Braun, Orange)
- Großzügig Whitespace lassen
- Section Labels als Kategorie-Tags nutzen
- "→" als branded Bullet-Point
- Eule als KI-Avatar

### ❌ Don't
- Keine kalten Grautöne (#f0f0f0 etc.)
- Keine scharfen Ecken (border-radius: 0)
- Keine dünnen 1px Borders als Hauptstruktur (Shadows statt Borders)
- Kein reines Schwarz (#000) für Text
- Keine überladenen Seiten — Luft lassen
