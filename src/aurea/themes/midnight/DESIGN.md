# Midnight — Design System

A dark, focused, minimal design system for technical presentations. Built for long-form deep-dives where the audience needs to stay in a focused state — reading code, following architecture diagrams, absorbing dense information without visual fatigue.

---

## 1. Visual Theme

Midnight draws from the aesthetic of high-end developer tooling and modern SaaS dashboards. Think Linear, Vercel, Raycast — interfaces designed to get out of the way while still feeling considered and premium.

**Character**: Disciplined restraint on a very dark canvas. Purple is the single voice — it speaks once per slide, clearly. Everything else recedes.

**Influence**: The best dark-mode developer interfaces. The philosophy that dark themes are not just "light themes inverted" — they require different contrast ratios, different weight choices, different spacing to avoid looking muddy. Midnight is engineered for actual dark environments, not just dark backgrounds.

**When to use**: Engineering talks, technical architecture overviews, security research presentations, dev conference talks. Any context where the audience is developers, and the room may be dark.

---

## 2. Color Palette

| Role        | Hex         | Usage                                              |
|-------------|-------------|----------------------------------------------------|
| Background  | `#0d0d0d`   | Slide background — near-black, not pure black      |
| Surface     | `#1a1a2e`   | Code blocks, elevated panels                       |
| Text        | `#e5e5e5`   | Body copy, bullets, captions                       |
| Heading     | `#ffffff`   | Titles, H1/H2 — pure white for maximum contrast   |
| Primary     | `#7c3aed`   | Borders, progress bar, key accents                 |
| Accent      | `#a855f7`   | Links, inline code, em emphasis                    |
| Light accent| `#c084fc`   | Hover states, secondary highlights                 |
| Muted       | `#888888`   | Dates, sources, secondary labels                   |

**Why near-black over pure black**: `#0d0d0d` (not `#000000`) prevents the harsh "floating text" effect on OLED screens and projectors. Pure black makes light elements appear to float unnaturally. Near-black reads as a surface, not a void.

**Color usage rules:**
- Purple (`#7c3aed`) appears once per slide — on the single most important structural element.
- Headings are pure white (`#ffffff`). Never accent-colored.
- `em` tags render in `#a855f7` — use `*emphasis*` to color a key technical term, not for style.
- Never use bright colors other than the purple family. The restraint is intentional.

---

## 3. Typography

**Primary font**: `"Inter", system-ui, -apple-system, sans-serif`

Inter was designed specifically for screen rendering — the letter forms are optimized for dark backgrounds and small sizes. Excellent legibility for code-adjacent content.

| Level     | Size    | Weight | Notes                                      |
|-----------|---------|--------|--------------------------------------------|
| H1        | 2.5em   | 700    | Section titles, impact moments             |
| H2        | 1.8em   | 700    | Slide titles (has a faint purple underline)|
| H3        | 1.3em   | 700    | Sub-sections, callout labels               |
| H4        | 1.0em   | 700    | Micro-labels, tags                         |
| Body      | 1.0em   | 400    | Lists, paragraphs                          |
| Code      | 0.78em  | 400    | Monospace (inline and block)               |

**Typography rules:**
- Letter spacing: -0.02em for headings. Tighter than Default — Inter at large sizes needs this.
- Line height: 1.6 for body (slightly more than Default — dark backgrounds benefit from more air).
- Never use font-weight below 400 on dark backgrounds — thin text disappears.
- H2 slides have a subtle bottom border: `1px solid rgba(124, 58, 237, 0.3)`. This is structural, not decorative.

---

## 4. Components

### Code Blocks
Dark surface `#1a1a2e` (navy-dark, distinct from the near-black background). Purple-tinted glow border. This creates a sense of depth — code lives "inside" the slide rather than floating on it. Syntax highlighting works naturally on this surface.

### Inline Code
Purple-tinted background, `#c084fc` text. Clearly distinguishable from prose. Use liberally for function names, file paths, CLI commands — this is a technical theme.

### Blockquotes
Compact left-border style. Purple 3px border, very faint purple background. For attributed quotes, section epigraphs, or highlighted architectural principles.

### Tables
Minimal — thin horizontal separators only. Header row has a faint purple background and a 2px purple bottom border. Row hover state adds a very subtle purple tint. Tables feel part of the dark surface, not imposed on it.

### Emphasis
- **Bold (`**text**`)**: Renders white (`#ffffff`) — maximum contrast against the dark background. Use for the single most important word/phrase.
- *Italic (`*text*`)**: Renders purple (`#a855f7`) — use for key technical terms, names of concepts, or a phrase you want the audience to remember.
- `Code`: Purple-tinted, always monospace.

---

## 5. Layout

Standard reveal.js centered layout. Midnight's near-black background means edge content can blend into nothing — keep content centered and well-padded.

**Density guidelines:**
- Maximum 5 bullet points per slide (dark themes can feel dense — be more sparse than you think you need to be).
- One code block per slide. Two code blocks look cluttered on dark.
- Leave at least 25% white (dark) space.
- When showing code + explanation, prefer two separate slides: code on one, explanation on the next.

**Common layouts for technical content:**
1. **Section opener**: H1 centered, single subtitle line. Often the most impactful slide.
2. **Architecture slide**: H2 + code block. Code is the hero. Title anchors the context.
3. **Comparison slide**: Two-column layout — left: old approach, right: new approach.
4. **Terminal output**: Full-slide pre/code block. No heading needed — the output speaks.
5. **Insight slide**: H2 + 3–4 bullets. Save for principles and takeaways.

---

## 6. Depth

Midnight uses layered dark values to create depth without light:

| Layer       | Color      | Usage                               |
|-------------|------------|-------------------------------------|
| Void        | `#0d0d0d`  | Background — the deepest layer      |
| Surface     | `#1a1a2e`  | Code blocks — visually elevated     |
| Glow        | `rgba(124, 58, 237, 0.07)` | Blockquote tint, hover states |
| Light       | `#ffffff`  | Headings — the highest contrast point |

Code blocks also use `box-shadow: 0 4px 24px rgba(0,0,0,0.5), 0 0 0 1px rgba(124, 58, 237, 0.2)` — a slight outer glow that reads as premium without being garish.

**Avoid:**
- Bright neon colors that weren't specified above.
- Multiple glow effects on the same slide.
- White backgrounds inside dark slides (it breaks the immersion).

---

## 7. Do's and Don'ts

### Do
- Use code blocks generously — this theme is made for them.
- Write slide titles as precise, declarative technical statements.
- Use `*asterisks*` (italic/em) to call out specific technical terms in purple.
- Keep bullet lists to 5 items or fewer.
- Use the architecture slide layout for system design content.
- Let white space (dark space) breathe — don't fill every pixel.

### Don't
- Don't use colorful icons or emoji — they clash with the dark palette.
- Don't use light-mode screenshots inline — they'll look jarring. If you must, add a dark border frame.
- Don't use more than two levels of bullet nesting.
- Don't use tables with more than 4 columns on this theme — they're hard to read on dark.
- Don't use the accent purple as a background color for any large area.
- Don't use all-caps headings — Inter's weight does the work without shouting.

---

## 8. Responsive

Midnight is optimized for dark conference rooms with projection, and developer screens (usually dark-mode UI, 13"–27" range).

**Projection concerns:**
- Very dark backgrounds can lose contrast on cheap projectors. If the venue is uncertain, test at 50% brightness.
- The near-black (`#0d0d0d`) vs pure black choice is deliberate — it renders better on projectors with raised black levels.
- Code blocks use a slightly lighter surface (`#1a1a2e`) to remain distinct even on washed-out projectors.

**Screen concerns:**
- OLED/AMOLED screens: the near-black background prevents the "floating" text effect of pure black.
- Retina/HiDPI: Inter renders beautifully at high DPI. The -0.02em letter-spacing was tuned for these displays.

**PDF export:**
- Dark backgrounds consume ink. For printable versions, generate a separate light-mode export.
- On screen PDF previews, the dark theme looks intentional and premium.

---

## 9. Agent Prompt Guide

This section tells AI agents (Claude, Gemini, Copilot, etc.) how to create presentations using the Midnight theme effectively.

### Core philosophy
Midnight is for content that rewards attention. Every slide should justify its existence — no filler, no re-stating what was just said. The dark canvas creates a focused, cinema-like environment. Use it for the content that matters most.

### Slide creation rules
1. **Be more sparse than you think you need to be.** Dark themes hide clutter less forgivingly than light themes. If a slide feels full, split it.
2. **Titles are precise.** Not "Database Design" but "Why we chose a write-ahead log over event sourcing."
3. **Maximum 5 bullets.** In a dark theme, even 5 can feel dense. Aim for 3.
4. **Code is a first-class citizen.** This theme is designed for code. Don't be afraid to dedicate a slide to nothing but a code block.

### Color usage for agents
- Use `*emphasis*` (which renders purple, `#a855f7`) to highlight the one concept per slide you want the audience to remember. Not for every technical term — for the key one.
- Never suggest changing heading colors to accent purple — headings stay white.
- Never suggest adding colored backgrounds to content areas.

### Purple usage — use sparingly
Purple (`#7c3aed`) appears automatically in: H2 border-bottom, code block inline background, blockquote border, list markers, table headers, progress bar.

Do NOT add additional purple elements to a slide. The theme's accent value is already present. Adding more purple breaks the restraint that makes it work.

### Technical content guidance
- For architecture diagrams: describe them in ASCII or Mermaid, placed in a code block. The dark surface makes ASCII art highly readable.
- For CLI output: use a full-slide pre block with no heading. Label the slide in the title bar only.
- For API comparisons: use a two-column table. Keep it to 3 rows of comparison at most.
- For error messages: use a blockquote with the error on one line, and your explanation as the blockquote body.

### Structure recommendation
For a 20-slide technical talk using Midnight:
- Slides 1: Title — name of the talk, your handle/name. Minimal.
- Slides 2–3: Problem definition. Precise, no fluff.
- Slides 4–6: Current state — code, architecture, metrics. One per slide.
- Slides 7–14: Deep dive — each technical concept gets its own slide(s). Code blocks welcome.
- Slides 15–17: The solution or recommendation. Show the code or config.
- Slides 18–19: Results, metrics, before/after.
- Slide 20: Conclusion. One sentence. A link. Done.
