---
name: aurea.extract
description: Extract a design system from a URL and generate a complete Aurea theme (works without CLI)
---

# aurea.extract — Design System Extraction

You are extracting a design system from a live URL and generating a complete Aurea theme. This command works **without the CLI** — you perform the extraction natively using your web browsing capability.

## Step 1 — Fetch the target URL

The user's input is: `$ARGUMENTS`

Parse `$ARGUMENTS` to extract:
- **URL**: the website to extract from (required).
- **Theme name**: a short identifier like `stripe-dark` or `linear` (optional — derive from domain if missing).

Fetch the URL using your native web browsing capability. Retrieve:
1. The main HTML page.
2. Any linked CSS stylesheets referenced in `<link rel="stylesheet">` tags.
3. Inline `<style>` blocks.

If the URL is inaccessible, report the error and ask for an alternative URL or a CSS snippet to paste directly.

## Step 2 — Parse design tokens

From the fetched HTML and CSS, extract the following tokens:

### Colors
- Look for: CSS custom properties (`--color-*`, `--primary`, `--background`, etc.), `background-color` declarations on `body` / `:root`, hardcoded hex values (#RRGGBB, #RGB), HSL/RGB values used repeatedly.
- Categorize as: background, surface, primary, secondary, accent, text, text-muted, border, success, warning, error.
- Extract at minimum: background, primary, accent, text. All others are optional.

### Typography
- Look for: `font-family` on `body`, `h1`–`h6`, headings.
- Extract: heading font family, body font family, base font size, heading scale.
- Note any Google Fonts or custom font imports (but do not include external font URLs in the generated theme — use system font fallbacks).

### Spacing & Shape
- Look for: `border-radius` on cards, buttons, panels.
- Look for: padding/margin patterns (4px, 8px, 16px, 24px, etc.).
- Note the general spacing unit (4px or 8px base grid).

### Motion & Style
- Look for: `transition`, `animation` declarations.
- Note: is the design flat, raised (box shadows), glassmorphic, or outlined?
- Note: does it use gradients prominently?

## Step 3 — Infer design personality

Based on extracted tokens, characterize the design system:

- **Mood**: one word (minimal, bold, playful, technical, elegant, corporate…)
- **Dominant color temperature**: warm / cool / neutral
- **Visual weight**: light / medium / heavy
- **Key design trait**: one sentence (e.g., "High-contrast dark theme with electric blue accents and generous whitespace")

## Step 4 — Generate theme files

Create the following directory structure:
`{{SLIDES_DIR}}/../.aurea/themes/<theme-name>/`

### 4a. `DESIGN.md`

Generate a complete DESIGN.md with these 9 sections:

```markdown
# <Theme Name> Design System

## 1. Overview
<2-3 sentences: what this design system is, its origin, its personality>

## 2. Color Palette
| Token | Hex | Usage |
|-------|-----|-------|
| Background | #RRGGBB | Page/slide background |
| Surface | #RRGGBB | Card and panel backgrounds |
| Primary | #RRGGBB | Headlines, primary actions |
| Secondary | #RRGGBB | Supporting elements |
| Accent | #RRGGBB | Highlights, CTAs, emphasis |
| Text | #RRGGBB | Body copy |
| Text Muted | #RRGGBB | Captions, secondary info |
| Border | #RRGGBB | Dividers, outlines |

## 3. Typography
- **Heading font**: <font-family> (fallback: <system-font>)
- **Body font**: <font-family> (fallback: <system-font>)
- **Base size**: <px>
- **Heading scale**: H1 <em>, H2 <em>, H3 <em>
- **Weight**: Headings <weight>, Body <weight>

## 4. Spacing & Layout
- **Base unit**: <4px or 8px>
- **Border radius**: <small: Xpx, medium: Xpx, large: Xpx>
- **Slide padding**: <recommended padding>
- **Max content width**: <Xpx or %>

## 5. Elevation & Depth
<Describe shadow system, z-layers, or flat/glass approach>

## 6. Motion & Transitions
- **Default transition**: <slide / fade / none>
- **Duration**: <Xms>
- **Easing**: <ease function>

## 7. Slide Type Inventory
List available slide classes and their intended use:
- `.title-slide` — Opening and closing title slides
- `.content-slide` — Standard content with heading + body
- `.quote-slide` — Large pull quotes
- `.data-slide` — Charts and statistics
- `.two-column` — Side-by-side content
- `.image-full` — Full-bleed visual slide

## 8. Do's
- <3–5 specific guidance items that work well in this theme>

## 9. Don'ts
- <3–5 specific patterns to avoid in this theme>
```

### 4b. `theme.css`

Generate reveal.js-compatible CSS with custom properties:

```css
/**
 * <Theme Name> theme for reveal.js
 * Extracted from: <source URL>
 * Generated: <date>
 */

:root {
  --r-background-color: #RRGGBB;
  --r-main-color: #RRGGBB;
  --r-heading-color: #RRGGBB;
  --r-link-color: #RRGGBB;
  --r-link-color-hover: #RRGGBB;
  --r-selection-background-color: #RRGGBB;
  --r-main-font: '<body-font>', <fallbacks>;
  --r-heading-font: '<heading-font>', <fallbacks>;
  --r-main-font-size: <size>px;
  --r-heading-line-height: 1.2;
  --r-heading-letter-spacing: <value>;
  --r-heading-text-transform: none;

  /* Custom tokens */
  --aurea-surface: #RRGGBB;
  --aurea-accent: #RRGGBB;
  --aurea-text-muted: #RRGGBB;
  --aurea-border: #RRGGBB;
  --aurea-radius-sm: <Xpx>;
  --aurea-radius-md: <Xpx>;
}

.reveal {
  background-color: var(--r-background-color);
  color: var(--r-main-color);
  font-family: var(--r-main-font);
  font-size: var(--r-main-font-size);
}

.reveal h1, .reveal h2, .reveal h3 {
  font-family: var(--r-heading-font);
  color: var(--r-heading-color);
  line-height: var(--r-heading-line-height);
}

/* Slide type: title-slide */
.reveal section.title-slide {
  background-color: var(--r-background-color);
}

/* Slide type: quote-slide */
.reveal section.quote-slide blockquote {
  font-size: 2em;
  font-style: italic;
  border-left: 4px solid var(--aurea-accent);
  padding-left: 1em;
}

/* Slide type: data-slide */
.reveal section.data-slide .stat-number {
  font-size: 4em;
  font-weight: 700;
  color: var(--aurea-accent);
}

/* Two-column layout */
.reveal section.two-column .columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2em;
}
```

### 4c. `layout.css`

```css
/**
 * Layout utilities for <Theme Name>
 */

/* Grid helpers */
.reveal .columns-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }
.reveal .columns-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1em; }

/* Emphasis utilities */
.reveal .accent { color: var(--aurea-accent); }
.reveal .muted { color: var(--aurea-text-muted); }
.reveal .surface { background: var(--aurea-surface); border-radius: var(--aurea-radius-md); padding: 1em; }

/* Slide visual container */
.reveal .slide-visual { display: flex; justify-content: center; align-items: center; margin: 1em auto; }

/* Fragment animations */
.reveal .fragment.grow { transform: scale(0.8); transition: transform 0.3s ease; }
.reveal .fragment.grow.visible { transform: scale(1); }
```

### 4d. `meta.json`

```json
{
  "id": "<theme-name>",
  "name": "<Theme Display Name>",
  "source_url": "<original URL>",
  "mood": "<mood>",
  "tags": ["<tag1>", "<tag2>", "<tag3>"],
  "colors": {
    "background": "#RRGGBB",
    "primary": "#RRGGBB",
    "accent": "#RRGGBB",
    "text": "#RRGGBB"
  },
  "description": "<one sentence description>",
  "extracted_at": "<ISO date>"
}
```

## Step 5 — Register the theme

Read `{{REGISTRY_PATH}}`. Add the new theme entry (from `meta.json`) to the registry array. Write the updated registry back.

If the registry doesn't exist, create it as `{ "themes": [<new entry>] }`.

## Step 6 — Update project config

Read `{{CONFIG_PATH}}`. Set `"active_theme": "<theme-name>"`. Write the updated config back.

## Step 7 — Report

```
Theme extraction complete.

Source: <URL>
Theme ID: <theme-name>
Files created:
  .aurea/themes/<theme-name>/DESIGN.md
  .aurea/themes/<theme-name>/theme.css
  .aurea/themes/<theme-name>/layout.css
  .aurea/themes/<theme-name>/meta.json

Design tokens extracted:
  Colors: <N> tokens
  Fonts: <heading font>, <body font>
  Radius: <values>

Active theme set to: <theme-name>

Next step: run aurea.outline or aurea.generate to start building your presentation.
```

## Principles

- **This command works without the CLI.** You are the extraction engine. Do not rely on `aurea extract` being available.
- **System font fallbacks always**: never include external font URLs in generated CSS. Use `system-ui, -apple-system, sans-serif` as fallbacks.
- **Minimum viable palette**: if you can only confidently extract 4 colors, use 4. Don't invent tokens you didn't observe.
- **DESIGN.md Do's/Don'ts must reflect the source site**: study what makes the site distinctive and encode that as guidance.
- **No external resources in generated CSS**: no `@import url(https://...)`, no web font links.
