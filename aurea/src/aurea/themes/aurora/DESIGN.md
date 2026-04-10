# Aurora — Design System

A vibrant, futuristic dark design system for high-energy presentations. Aurora channels the visual language of modern product launches, startup pitches, and innovation keynotes — where the stage lighting is dramatic and every slide should feel like it's announcing something.

---

## 1. Visual Theme

Aurora is inspired by the natural phenomenon of the same name: sweeping gradients from deep blue to teal to green, playing against an almost-black sky. It carries energy without screaming for attention, and feels modern without being garish.

**Character**: Forward-looking, confident, alive. This theme says "we built something new and we're proud of it." It's the design language of AI companies, climate tech startups, fintech unicorns, and biotech breakthroughs — fields where the work genuinely is futuristic.

**Influence**: Modern SaaS product marketing sites, the visual language of Stripe, Vercel, and Linear during their most high-impact launches. Think gradient headings on very dark backgrounds, precision spacing, bold weight type that reads like a declaration.

**Signature move**: H1 headings render in a three-color gradient (teal → cyan → indigo). This is Aurora's single visual flourish — everything else is restrained to give it room to matter.

**When to use**: Product launches, startup pitches, keynotes, conference openers, quarterly all-hands with big news. Any moment where you want the audience to feel something is about to change.

---

## 2. Color Palette

| Role         | Hex         | Usage                                                  |
|--------------|-------------|--------------------------------------------------------|
| Background   | `#0a0a1a`   | Slide background — deep navy-black                     |
| Surface      | `#0f1629`   | Code blocks — slightly lighter, blue-tinted            |
| Text         | `#f0f0f0`   | Body copy, bullets, captions                           |
| Heading      | `#ffffff`   | H2/H3/H4 — pure white                                 |
| Gradient H1  | `#10b981 → #06b6d4 → #818cf8` | Section titles — the aurora gradient |
| Primary      | `#10b981`   | Teal — progress bar, list markers, strong emphasis     |
| Accent       | `#06b6d4`   | Cyan — links, em emphasis, secondary highlights        |
| Indigo       | `#818cf8`   | Gradient tail, tertiary accent (gradient only)         |
| Code text    | `#34d399`   | Inline code content — light teal                       |
| Muted        | `#7a9a90`   | Secondary text, metadata                               |

**Color harmony rules:**
- Teal (`#10b981`) and cyan (`#06b6d4`) are close relatives — use them together, not in competition.
- Never use `#818cf8` (indigo) outside of the H1 gradient. It's reserved for the fade-out effect.
- Progress and growth concepts map to teal. Future/horizon concepts map to cyan.
- When you need to draw attention, teal beats cyan. When you need subtlety, cyan beats teal.

---

## 3. Typography

**Primary font**: `"Inter", system-ui, -apple-system, sans-serif`

| Level     | Size    | Weight | Notes                                        |
|-----------|---------|--------|----------------------------------------------|
| H1        | 2.6em   | 800    | Aurora gradient — section/opener slides      |
| H2        | 1.9em   | 800    | Slide titles — white, bold, impactful        |
| H3        | 1.35em  | 800    | Sub-headings, callout labels                 |
| H4        | 1.0em   | 800    | Micro-labels                                 |
| Body      | 1.0em   | 400    | Lists, paragraphs                            |
| Code      | 0.78em  | 400    | Monospace                                    |

**Typography rules:**
- Font weight: 800 for all headings. This is heavier than Midnight or Default. On a very dark background, weight carries energy.
- Letter spacing: -0.03em — tighter than Midnight. Larger, heavier text needs this to feel intentional.
- Line height: 1.1 for headings (tight), 1.55 for body (relaxed contrast).
- The tightness of headings combined with the looseness of body copy creates visual rhythm.

---

## 4. Components

### H1 Gradient
The signature element. `background: linear-gradient(135deg, #10b981 0%, #06b6d4 50%, #818cf8 100%)` applied as a text clip. Use H1 for section opener slides, not for every slide. The gradient is striking — it should feel special.

### Code Blocks
Deep blue-tinted surface (`#0f1629`). Teal-hued outer glow. Code text color is `#e2f5f0` — warm off-white that reads cleanly on the blue surface. Box shadow: `0 4px 32px rgba(16, 185, 129, 0.15), 0 0 0 1px rgba(6, 182, 212, 0.2)` — the outermost ring is cyan-tinted, different from Midnight's purple ring.

### Inline Code
Teal-tinted background, `#34d399` text (light teal). Feels like terminal output in a modern CLI tool.

### Blockquotes
Teal left-border, very faint teal background, `#b0e8d8` text. Use for customer quotes, key product principles, or highlighted data points.

### Bold and Emphasis
- **Bold (`**text**`)**: Teal (`#10b981`) — not white like Midnight. Bold in Aurora means "this is a positive, forward-moving thing."
- *Italic (`*text*`)**: Cyan (`#06b6d4`) — use for product names, concepts, technical terms you're defining.

---

## 5. Layout

Standard reveal.js centered layout. Aurora's deep background creates a spotlight effect — content in the center feels like it's under stage lighting.

**Density guidelines:**
- Maximum 5 bullet points per slide.
- One code block per slide.
- Gradient H1 slides work best as section dividers with no other content — let the gradient breathe.
- For launch moments: consider a single-word H1 + one-line subtitle. The gradient does the work.

**Common layouts:**
1. **Opener**: H1 gradient + subtitle + presenter name. Dramatic. Clean.
2. **Section divider**: H1 gradient only. Centered. Dark space all around.
3. **Metric slide**: H2 + one massive number (styled with H1 gradient or teal color).
4. **Feature announcement**: H2 + 3 bullets with short, punchy lines.
5. **Before/After**: Two-column — left column "before" in muted colors, right column "after" in teal.

---

## 6. Depth

Aurora uses two distinct dark layers plus glow effects to create a futuristic sense of depth:

| Layer          | Color/Effect                             | Usage                           |
|----------------|------------------------------------------|---------------------------------|
| Deep background | `#0a0a1a`                               | The slide canvas                |
| Code surface   | `#0f1629`                               | Code blocks — subtly elevated   |
| Teal glow      | `rgba(16, 185, 129, 0.15)` shadow        | Code block ambient glow         |
| Cyan ring      | `rgba(6, 182, 212, 0.2)` border          | Code block 1px ring             |
| Gradient text  | Teal → Cyan → Indigo                    | H1 — highest visual layer       |

**The glow effect philosophy**: Aurora is the only Aurea theme that uses ambient glow. The soft teal shadow on code blocks mimics the glow of a terminal on a dark desk. This is atmospheric, not decorative — it reinforces the "something is happening here" feeling.

---

## 7. Do's and Don'ts

### Do
- Use H1 gradient headings for section transitions and major reveals.
- Write **bold** text for positive outcomes, progress, and growth — the teal color reinforces forward motion.
- Use *emphasis* for product names and key concepts — cyan is the "this is the future" color.
- Lead with the headline number. "3.2× faster" belongs on slide 1, not slide 12.
- Use the before/after two-column layout for showing transformation.
- Keep bullet text short enough to feel like punchy announcements, not explanations.

### Don't
- Don't use H1 gradient on every slide — it loses its impact.
- Don't mix Aurora with warm colors (orange, red, yellow) — they clash with the teal/cyan palette.
- Don't use the indigo (`#818cf8`) directly — it's for the gradient tail only.
- Don't write long paragraphs. Aurora is for announcements, not documentation.
- Don't use blockquotes for decoration — they should quote real people or real metrics.
- Don't add additional glow effects beyond what the theme provides — "more glow" quickly becomes noise.

---

## 8. Responsive

Aurora is designed for large screens and projection in conference settings or company events.

**Stage/keynote projection:**
- The dark background absorbs ambient stage light well.
- The high-contrast gradient headings remain legible even on washed-out projectors.
- Avoid slides with faint colors (like muted gray text) — low-contrast elements disappear on projectors.

**Video/streaming:**
- The teal/cyan palette looks excellent in video compression (less blocking than red/orange).
- The gradient text may show slight compression artifacts at very low bitrates — if streaming at <1Mbps, consider using H2 white headings instead of H1 gradient.

**PDF export:**
- Dark backgrounds look striking in PDF/on-screen but consume heavy ink.
- Colors translate reasonably to grayscale if needed (teal and cyan both map to mid-range gray, maintaining hierarchy).

---

## 9. Agent Prompt Guide

This section tells AI agents (Claude, Gemini, Copilot, etc.) how to create presentations using the Aurora theme effectively.

### Core philosophy
Aurora is the announcement theme. Every slide should feel like it's building toward something — a reveal, a milestone, a future state. Write like a product team that is proud of what they built. Use short, declarative language. Numbers first, explanation second.

### Slide creation rules
1. **Lead with the headline.** The most exciting thing you're announcing belongs on slide 2, not slide 10.
2. **Titles as announcements.** "Latency dropped by 80%" beats "Performance improvements."
3. **Use H1 as a dramatic pause.** For section dividers, a one-line H1 gradient slide with nothing else is powerful.
4. **Numbers are content.** If you have a metric, put it on its own slide with the number very large.
5. **Maximum 4 bullets.** Aurora slides should feel punchy — 5+ bullets look like a PowerPoint deck, not a keynote.

### Color usage for agents
- Use `**bold**` to highlight metrics, outcomes, and growth indicators (renders teal).
- Use `*emphasis*` for product names, feature names, or concepts being defined (renders cyan).
- Never suggest adding red, orange, or yellow. They clash.
- The H1 gradient is automatic — just use `# Heading` for section openers.

### Teal for progress/growth concepts
The primary color, teal (`#10b981`), is the color of growth, health, and progress. Use it (via bold) for:
- Revenue growth, user growth, performance improvements
- New features, launched products, completed milestones
- Anything "up and to the right"

Cyan (`#06b6d4`) is the color of the future and possibility. Use it (via em/italic) for:
- Product names and concepts being introduced
- What's coming next, the vision
- Technology names, standards, protocols

### Structure recommendation
For a product launch or keynote using Aurora:
- Slide 1: Title — product name in H1 gradient, single tagline. Nothing else.
- Slide 2: The big number / the headline result. One stat, oversized.
- Slides 3–4: The problem (brief — 2–3 bullets max, muted tone).
- Slides 5–7: Section break (H1 gradient "The Solution") + feature slides (1 feature per slide).
- Slides 8–10: Traction / evidence / customer proof. Metrics as bold teal.
- Slide 11: H1 gradient "What's Next" + 3-bullet roadmap.
- Slide 12: Call to action. One sentence. One link.
