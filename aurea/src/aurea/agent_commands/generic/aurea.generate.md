---
name: aurea.generate
description: Create full Markdown presentation from the outline
---

# aurea.generate — Full Presentation Generation

You are generating the complete Markdown source for a reveal.js presentation. This is the main content-creation step — every slide gets written in full.

## Step 1 — Read all context

Read these files before writing a single slide:

1. `{{CONFIG_PATH}}` — project settings: author, theme, output preferences.
2. `{{DESIGN_MD_PATH}}` — the active theme's design system. Read it carefully:
   - **Color palette**: exact hex values for primary, secondary, accent, background, text.
   - **Typography**: font families, heading sizes, body sizes.
   - **Do's**: patterns that work well in this theme.
   - **Don'ts**: patterns to avoid (e.g., "never use more than 2 fonts", "avoid dense bullet lists").
   - **Slide types**: which CSS classes and layouts are available.
3. `{{SLIDES_DIR}}/outline.md` — the narrative plan. Follow it faithfully. Do not invent new slides or skip planned ones without noting why.

## Step 2 — Generate `slides/presentation.md`

Write the file to `{{SLIDES_DIR}}/presentation.md`.

### Required structure

```markdown
---
title: "<presentation title>"
author: "<author from config>"
theme: "<active_theme>"
date: "<YYYY-MM-DD>"
---

<!-- SLIDE 1: Title -->
<!-- .slide: class="title-slide" data-background-color="<primary color from DESIGN.md>" -->

# <Title>

### <Subtitle or author tagline>

---

<!-- SLIDE 2: <slide title from outline> -->
<!-- .slide: class="<relevant CSS class>" -->

## <Slide Heading>

<Body content — MAXIMUM 40 words. One clear idea. Strong, active language.>

<!-- VISUAL: <description of desired visual — diagram, chart, illustration, icon arrangement> -->

Note:
<Speaker notes — 100–200 words. Expand on the slide's idea. Include supporting data, examples, anecdotes, transitions to the next slide. Write as if coaching a presenter.>

---

<!-- SLIDE 3: ... -->
```

### Slide writing rules

**Body content (≤40 words):**
- One dominant idea per slide.
- Use the theme's tone (from DESIGN.md) — formal, minimal, bold, etc.
- Prefer strong nouns and active verbs over passive constructions.
- Lists: maximum 3 items. If you need 4+, split into two slides.
- Numbers and statistics stand alone — give them space, don't bury them.

**Speaker notes (Note: prefix):**
- Every slide MUST have speaker notes.
- Notes are first-class content — they contain the depth that slides don't.
- Include: expanded explanation, supporting evidence, storytelling beats, transition cue to next slide.
- Write in second person ("You'll want to pause here…") to coach the presenter.

**`<!-- VISUAL: -->` markers:**
- Add to any slide that would benefit from a diagram, chart, icon, or illustration.
- Be specific: "<!-- VISUAL: Bar chart comparing Q1 vs Q2 revenue, using accent color for the winning bar -->"
- The `aurea.visual` command will process these markers later.

**`<!-- .slide: -->` attributes:**
- Use CSS classes from `DESIGN.md`'s slide type inventory.
- Use `data-background-color` for accent slides.
- Use `data-transition` for special transitions (fade, slide, zoom) at key narrative moments.

**Slide separators:**
- Use `---` (three dashes on a blank line) between every slide.
- Use `--` for vertical (sub-slide) navigation if nesting related content.

## Step 3 — Validate against outline

After writing all slides, verify:
- [ ] Slide count matches the outline plan (±1 is acceptable).
- [ ] Narrative arc is intact: opening → development → climax → conclusion.
- [ ] No slide body exceeds 40 words.
- [ ] Every slide has a `Note:` section.
- [ ] Theme's Do's and Don'ts from DESIGN.md are respected.
- [ ] `<!-- VISUAL: -->` markers are present on at least 30% of slides.

## Step 4 — Report to user

After saving the file, tell the user:
- Total slide count.
- How many slides have `<!-- VISUAL: -->` markers (suggest running `aurea.visual` next).
- Any slides where you deviated from the outline and why.
- Suggested next step: `aurea.refine` for targeted edits, or `aurea.visual` for visuals, or `aurea.build` to generate HTML.

## Principles

- **Slides are the summary; notes are the speech.** If you find yourself writing more than 40 words on a slide body, move the excess to speaker notes.
- **Visual-first thinking**: before writing slide text, ask "what is the strongest visual representation of this idea?" Use `<!-- VISUAL: -->` markers liberally.
- **Honor the theme**: DESIGN.md is a creative brief. If the theme is "minimal", resist the urge to add more. If it's "bold", don't be timid.
- **Climax slide gets special treatment**: make the most important insight unmissable — large text, strong color, maximum visual weight.
