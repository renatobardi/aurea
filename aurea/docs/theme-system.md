# Aurea Theme System

## Theme Structure

Each theme is a directory containing exactly four files:

```
themes/<theme-id>/
├── DESIGN.md       — Human-readable + agent-parseable design system
├── theme.css       — reveal.js CSS custom properties
├── layout.css      — Grid, animations, layout overrides
└── meta.json       — Registry metadata
```

## DESIGN.md Format (9 Required Sections)

Every DESIGN.md MUST contain all 9 sections. Missing sections cause `AureaError` during build:

```markdown
## 1. Visual Theme
<!-- Describe the overall visual character -->

## 2. Color Palette
<!-- Hex values and semantic roles: primary, background, text, accent, surface -->

## 3. Typography
<!-- Heading font, body font, sizes, weights, line height -->

## 4. Components
<!-- Buttons, code blocks, lists, tables, callouts -->

## 5. Layout
<!-- Grid system, max-width, spacing scale, padding -->

## 6. Depth
<!-- Shadows, border-radius, z-index, blur effects -->

## 7. Do's and Don'ts
<!-- What to emphasize and what to avoid -->

## 8. Responsive
<!-- Breakpoints, mobile behavior, scaling notes -->

## 9. Agent Prompt Guide
<!-- How should an AI agent use this theme? Colors for what purposes?
     Maximum words per slide? Key visual metaphors? -->
```

The `_validate_design_md()` function in `build.py` checks for these 9 keywords (case-insensitive):
`visual theme`, `color palette`, `typography`, `components`, `layout`, `depth`, `do's`, `responsive`, `agent prompt`

## theme.css — reveal.js Custom Properties

Standard CSS custom properties that reveal.js reads:

```css
:root {
  --r-background-color: #ffffff;
  --r-main-color: #111111;
  --r-main-font: "Helvetica Neue", sans-serif;
  --r-main-font-size: 1.1rem;
  --r-heading-color: #333333;
  --r-heading-font: "Helvetica Neue", sans-serif;
  --r-heading-font-weight: 700;
  --r-heading-text-transform: none;
  --r-heading1-size: 2.5em;
  --r-heading2-size: 1.8em;
  --r-heading3-size: 1.4em;
  --r-link-color: #0066cc;
  --r-link-color-hover: #004499;
  --r-code-font: monospace;
  --r-block-margin: 20px;
}
```

## meta.json Schema

```json
{
  "id": "stripe",
  "name": "Stripe",
  "category": "fintech",
  "tags": ["minimal", "professional", "dark"],
  "mood": "Clean, professional, data-forward design for financial products",
  "colors": {
    "primary": "#635bff",
    "background": "#0a2540",
    "text": "#ffffff",
    "accent": "#00d4ff"
  },
  "typography": {
    "heading": "\"Sohne\", \"Helvetica Neue\", sans-serif",
    "body": "\"Sohne\", sans-serif"
  },
  "version": "1.0.0",
  "path": "stripe",
  "source": "awesome-design-md"
}
```

## Registry Format

`src/aurea/themes/registry.json` (global, read-only):

```json
{
  "version": "1.0.0",
  "sources": [
    {
      "repo": "https://github.com/VoltAgent/awesome-design-md.git",
      "last_sync": "2025-01-01"
    }
  ],
  "themes": [
    { "id": "default", "name": "Default", ... },
    { "id": "midnight", "name": "Midnight", ... }
  ]
}
```

Projects can have a local registry at `.aurea/themes/registry.json`. Local entries shadow global ones by `id`. The `load_registry()` function in `theme.py` merges both.

## Available Themes

### Original (5)
| ID | Name | Category | Style |
|----|------|----------|-------|
| `default` | Default | general | Clean, minimal, neutral |
| `midnight` | Midnight | dark | Deep blue, elegant |
| `aurora` | Aurora | colorful | Vibrant gradients, lively |
| `editorial` | Editorial | editorial | Typography-forward, readable |
| `brutalist` | Brutalist | experimental | Raw, high-contrast |

### Imported from awesome-design-md (31+)
Categories: AI/ML, DevTools, Infrastructure, Design, Enterprise, Automotive, Finance, Social/Media

## Creating a Custom Theme

```bash
aurea theme create my-brand
```

This scaffolds `.aurea/themes/my-brand/` with all four files. Edit `DESIGN.md` to describe your brand, then update `theme.css` with your colors.

## Applying a Theme

```bash
aurea theme use stripe          # copy to .aurea/themes/ + update config.json
aurea build --theme stripe      # CLI override for one-off builds
```

## Importing from awesome-design-md

```bash
python scripts/import-awesome-designs.py
```

The script clones/updates `VoltAgent/awesome-design-md`, parses each `DESIGN.md`, generates `meta.json` + `theme.css` + `layout.css`, and updates `registry.json`.

## DESIGN.md Dual-Purpose Contract (Art. V)

DESIGN.md serves two audiences simultaneously:
1. **Human developers**: Describes the design system clearly enough to guide manual implementation
2. **AI agents**: Structured enough for agents to follow when generating slides

**Never change the 9-section format** without updating:
- `src/aurea/commands/build.py` (`REQUIRED_SECTIONS`)
- `src/aurea/commands/extract.py` (`generate_raw_design_md()`)
- All 56 agent templates in `src/aurea/agent_commands/`
- This document
