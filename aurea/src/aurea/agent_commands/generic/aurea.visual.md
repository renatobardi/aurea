---
name: aurea.visual
description: Generate SVG and CSS visual assets for slides marked with VISUAL comments
---

# aurea.visual — Visual Asset Generation

You are creating inline visual assets for slides that have been marked with `<!-- VISUAL: -->` comments. Every visual must use exact colors from the active theme's DESIGN.md and be embedded directly in the slide — no external image files.

## Step 1 — Read the design system

Read `{{DESIGN_MD_PATH}}` in full. Extract and store:

- **Primary color**: `#RRGGBB`
- **Secondary color**: `#RRGGBB`
- **Accent color**: `#RRGGBB`
- **Background color**: `#RRGGBB`
- **Text color**: `#RRGGBB`
- **Additional palette colors** (if defined): note each one with its semantic label.
- **Typography**: font family names for headings and body.
- **Do's**: visual patterns encouraged by the theme.
- **Don'ts**: patterns to avoid — follow these strictly.
- **Corner radius / spacing tokens** (if defined): use consistent values.

You will use these values in every visual you generate. Do not invent colors outside the palette.

## Step 2 — Scan for VISUAL markers

Read `{{SLIDES_DIR}}/presentation.md`. Find every `<!-- VISUAL: <description> -->` comment.

For each marker, record:
- Slide number (count `---` separators)
- Slide title
- Visual description from the comment
- Surrounding context (what the slide is about)

List all markers before starting any generation.

## Step 3 — Generate visuals

For each marker, choose the most appropriate visual type and generate it inline:

### Type A — Inline SVG

Use for: diagrams, icons, abstract shapes, data visualizations, process flows, comparisons.

```html
<!-- VISUAL: [description] -->
<figure class="slide-visual">
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="[description]">
  <!-- SVG elements using palette colors only -->
</svg>
</figure>
```

Rules for SVG:
- Use only colors from the DESIGN.md palette.
- Text in SVG: use the theme's font family or a safe fallback (`sans-serif`).
- Keep paths simple — this renders in a browser, not a print engine.
- Minimum touch targets: 44×44px for interactive-looking elements.
- Include `role="img"` and `aria-label` for accessibility.

### Type B — CSS Art / Layout

Use for: stylized UI mockups, abstract geometric compositions, icon grids, tag clouds, timeline strips.

```html
<!-- VISUAL: [description] -->
<div class="slide-visual css-art" aria-label="[description]">
  <!-- Styled divs using inline style or data-attributes -->
</div>
<style>
  /* Scoped styles using theme palette variables */
</style>
```

### Type C — Mermaid Diagram

Use for: flowcharts, sequence diagrams, entity relationships, Git graphs, architecture diagrams.

````markdown
<!-- VISUAL: [description] -->
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Outcome A]
    B -->|No| D[Outcome B]
    style A fill:<primary_color>,color:<text_on_primary>
    style C fill:<accent_color>
```
````

Use theme colors in `style` directives. Keep diagrams to ≤8 nodes — complexity defeats the purpose.

### Type D — Data Visualization (HTML/CSS)

Use for: bar charts, progress rings, stat callouts, comparison grids.

Build with pure HTML+CSS. No JavaScript charting libraries. Example bar chart:

```html
<!-- VISUAL: [description] -->
<div class="chart" role="img" aria-label="[description]">
  <div class="bar" style="--value: 72%; --color: <accent_color>">
    <span class="label">Q1</span><span class="value">72%</span>
  </div>
  <!-- additional bars -->
</div>
```

## Step 4 — Replace markers in presentation.md

For each processed `<!-- VISUAL: -->` marker, replace the comment with the generated asset inline. Keep the `<!-- VISUAL: -->` comment as a reference above the asset:

```markdown
<!-- VISUAL: Bar chart comparing Q1 vs Q2 revenue -->
<figure class="slide-visual">
  <svg viewBox="0 0 800 300" ...>
    <!-- generated SVG -->
  </svg>
</figure>
```

Do not modify any other part of the slide.

## Step 5 — Report

After processing all markers:

```
Visual assets generated: X of Y markers processed.

Slide 3 — "Revenue Growth": SVG bar chart (4 bars, accent color highlights)
Slide 5 — "Architecture": Mermaid flowchart (6 nodes)
Slide 8 — "Key Stat": CSS stat callout (large number + ring)
Slide 11 — "Process": SVG process flow (5 steps)

Skipped: 0
```

If any marker description was too vague to generate a high-quality visual, report it and suggest a more specific description.

Ask: "Ready to build? Run `aurea.build` to generate the final HTML."

## Principles

- **Every color must come from DESIGN.md.** If you're tempted to use a color not in the palette, use the closest palette color instead.
- **Simple > complex**: a clean 4-bar chart beats a cluttered 12-bar one. Reduce to the essential comparison.
- **Visuals serve the narrative**: each visual should make the slide's idea more obvious, not just prettier.
- **Offline-first**: no `<img src="https://...">`, no external SVG references. Everything is inline.
- **DESIGN.md Don'ts apply here too**: if the theme says "avoid gradients", don't add gradient fills to SVGs.
