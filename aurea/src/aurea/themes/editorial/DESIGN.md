# Editorial — Design System

A newspaper-inspired, typography-forward design system for presentations built on authority and trust. Editorial is for the presenter who has done the work and wants the ideas to stand on their own merit — no visual tricks, just words, structure, and evidence arranged with care.

---

## 1. Visual Theme

Editorial draws from the traditions of print journalism and academic publishing: Georgia serif type, near-black ink on near-white paper, strong horizontal rules that divide and organize, and a single red accent that functions like a publication's masthead color.

**Character**: Authoritative, credible, considered. The aesthetic of a well-edited magazine or a prestigious academic journal. There's no dark mode — everything is built for natural reading conditions, like a newspaper on a desk in good morning light.

**Influence**: The New York Times, The Economist, academic journals, and the design tradition of books typeset by thoughtful humans. Specifically: the use of thin horizontal rules between sections, the table's top-and-bottom border convention (not full grid), and the restraint of using only one accent color — red — exactly where it matters.

**The red accent**: In newspapers, red is the masthead color. It signals "this is the publication's voice." In Editorial, red (`#c0392b`) is the publication's accent — used for emphasis and only for emphasis. It's not decorative; it's editorial judgment made visible.

**When to use**: Research presentations, academic talks, policy briefings, thought leadership, board-level reports, financial analysis. Any content where credibility and authority are more important than energy and excitement.

---

## 2. Color Palette

| Role        | Hex        | Usage                                                  |
|-------------|------------|--------------------------------------------------------|
| Background  | `#fafafa`  | Slide background — off-white, not pure white (less glare) |
| Text        | `#1a1a1a`  | Body copy, lists, captions — near-black, not pure black |
| Heading     | `#1a1a1a`  | Titles — same as text (typography carries hierarchy)   |
| Accent      | `#c0392b`  | Links, progress bar, blockquote border, selection      |
| Rule        | `#cccccc`  | Table borders, horizontal rules, H2 bottom border      |
| Strong rule | `#1a1a1a`  | H1 bottom border, table top/bottom borders             |
| Muted       | `#777777`  | Citations, dates, footnotes, metadata                  |
| Code surface| `#f5f5f5`  | Code blocks — barely-off-white                        |

**Color philosophy:**
- The palette has only two hues: neutral grays (from near-white to near-black) and one accent (red).
- Color is not used to decorate. It is used to signal: links lead somewhere, red means "editorial attention here."
- Never add a second accent color. If you feel something needs emphasis and red is already used, use bold weight, not color.

---

## 3. Typography

**Primary font**: `Georgia, "Times New Roman", serif`

Georgia was designed specifically for screen rendering in the 1990s and remains one of the most legible serif fonts available universally. Its proportions are generous — open counters, slightly heavier strokes than print-optimized fonts — making it highly readable on screens at presentation sizes.

| Level     | Size    | Weight | Notes                                               |
|-----------|---------|--------|-----------------------------------------------------|
| H1        | 2.4em   | 700    | Article headline — has a 3px bottom rule            |
| H2        | 1.75em  | 700    | Section heading — has a 1px light bottom rule       |
| H3        | 1.3em   | 700    | Sub-heading, pull-quote label                       |
| H4        | 1.0em   | 700    | Byline, micro-label                                 |
| Body      | 1.0em   | 400    | Lists, paragraphs — relaxed line-height (1.65)      |
| Quote     | 1.05em  | 400    | Blockquote — slightly larger, italic                |
| Code      | 0.78em  | 400    | Monospace — contrasts sharply with serif body       |

**Typography rules:**
- Line height 1.65 for body — editorial copy breathes. Long-form text benefits from generous leading.
- Letter spacing: -0.01em for headings. Georgia is naturally well-spaced; just a touch tighter.
- H1 carries a 3px solid bottom border. H2 carries a 1px light border. These are the column rules of editorial layout.
- Links use underlines (not just color) — in print, you can't hover to check. The underline is the visual signal.

---

## 4. Components

### Section Rules
H1 and H2 headings have horizontal rules underneath — a direct reference to newspaper layout where column heads are separated by thin rules. H1 gets a thick rule (3px, near-black), H2 gets a thin rule (1px, light gray).

### Tables
Editorial tables use the "top and bottom border" convention from academic and financial publishing — no full grid, just borders at the very top (2px), between the header and first row (1px), between rows (1px), and at the very bottom (2px). No background colors on cells.

### Blockquotes
The pull-quote tradition: large-ish italic text with a red left border. No background tint — just the border and the italic type. Optional `cite` or `footer` element for attribution, which renders in muted gray at 75% size.

### Code Blocks
Minimal. Near-white background (`#f5f5f5`), thin gray border. No drop shadows. Code is foreign to editorial layout — it should be usable but not decorative. Monospace font creates contrast against the serif body.

### Emphasis and Strong
- **Bold (`**text**`)**: Pure black — maximum weight on near-black body text. Subtle but clear.
- *Italic (`*text*`)**: Italic Georgia is particularly beautiful. Use for titles, foreign terms, and genuine emphasis.
- `Code inline`: Near-black on very light gray. Unambiguously different from the serif body.

---

## 5. Layout

Editorial centers content in reveal.js's standard layout, but the design sensibility is horizontal and column-like — content flows top to bottom, not in grids.

**Density guidelines:**
- Editorial can carry slightly more text per slide than other themes — the generous line-height and serif type are designed for reading.
- Maximum 6–7 bullet points, but prose lines should be kept shorter than for body text.
- Tables are well-suited to this theme. Two-column comparison tables, data tables, chronologies.
- Avoid images that feel like stock photography — this theme calls for charts, diagrams, or no images at all.

**Common layouts:**
1. **Headline slide**: H1 with bottom rule, subtitle in H4 (byline style), optional date or publication label.
2. **Section opener**: H1 rule + single sentence of context. Like a section break in a long-form article.
3. **Data slide**: H2 + table. The table's editorial styling is designed for this.
4. **Argument slide**: H2 + 4–5 bullets. Each bullet is a complete, defensible statement.
5. **Quote slide**: Full-slide blockquote with citation. The red border is the only color.

---

## 6. Depth

Editorial is deliberately flat — it is print. No shadows, no gradients, no glow effects.

**Visual structure without depth:**
- Hierarchy comes entirely from type scale and horizontal rules.
- The H1 3px rule is the strongest "border" in the theme — it organizes more powerfully than any shadow would.
- Tables use border-top and border-bottom conventions from academic/financial publishing — structural borders, not decorative borders.

**The one exception**: Code blocks may use a 1px solid border (`#cccccc`). This is the weakest possible separator — enough to distinguish code from background, nothing more.

---

## 7. Do's and Don'ts

### Do
- Write full, complete sentences as bullet points — not fragments. This theme can carry them.
- Use tables generously. Editorial tables look more at home here than in any other theme.
- Use blockquotes for real attributable quotes — researchers, authors, your own data speaking.
- Respect the horizontal rule hierarchy: H1 thick rule = major section, H2 thin rule = sub-section.
- Use `*italic*` for titles of works, papers, terms being defined.
- Write slide titles that read like article headlines — declarative, specific, memorable.

### Don't
- Don't add colors beyond the specified palette. No blue links unless you change the theme.
- Don't use H1 for every slide — it creates excessive thick rules. H2 is the workhorse heading.
- Don't add background colors to paragraphs or code blocks beyond the specified light gray.
- Don't center body text. Editorial layout is left-aligned.
- Don't use images unless they are charts, diagrams, or photographs with journalistic quality.
- Don't write titles as questions. Newspaper headlines don't ask — they assert.
- Don't use emoji — they are graphically incompatible with editorial typography.

---

## 8. Responsive

Editorial is optimized for screen reading and PDF export — its print heritage makes it the best Aurea theme for creating presentations that double as documents.

**PDF export:**
- Near-white background prints white. Near-black text prints clean.
- The red accent prints well in both color and grayscale (maps to a distinctive medium gray).
- Tables print excellently — the top-and-bottom border convention is the academic standard precisely because it prints clearly.

**Screen viewing:**
- Off-white (`#fafafa`) is easier on the eyes than pure white, especially in bright rooms.
- Georgia at `36px` base size is highly legible on any resolution.
- High contrast between text and background means no accessibility issues.

**Projection:**
- Light themes can wash out on projectors in bright rooms. Editorial's high contrast (near-black on near-white) is resistant to this.
- The red accent is strong enough to survive moderate projection degradation.
- If projector quality is unknown, this is the safest choice among light themes.

---

## 9. Agent Prompt Guide

This section tells AI agents (Claude, Gemini, Copilot, etc.) how to create presentations using the Editorial theme effectively.

### Core philosophy
Editorial is for ideas that deserve to stand on their own. Your job is to be an editor, not a designer. Every bullet should be a defensible claim. Every slide should add a new idea, not restate the last one. The audience for this theme reads carefully — reward that attention.

### Slide creation rules
1. **Write complete sentences.** Fragments feel sloppy in editorial context. "Revenue grew 40% YoY due to enterprise expansion" beats "Revenue ↑ 40%."
2. **Titles as assertions.** "The intervention reduced readmission rates by 23%" beats "Study results."
3. **Structure as argument.** The slide sequence should build a logical case. Each slide's title should be provable from the evidence on that slide.
4. **Data earns its place.** Every data point should appear because it proves something, not because it's available.
5. **One argument per slide.** If a slide makes two separate points, it should be two slides.

### Color usage for agents
- Red (`#c0392b`) appears automatically for links and blockquote borders. Do not add red to text.
- Bold renders as near-black (`#000000`) — use it for the key term in a claim.
- Italic renders as standard Georgian italic — use it for titles of works, terms on first definition, and genuine (not decorative) emphasis.
- Never suggest adding colored backgrounds, highlights, or text other than what the theme provides.

### Tone guidance
- Write for a reader, not a viewer. Editorial audiences read slides.
- Cite your sources. Use the blockquote's cite syntax: `> Quote text\n> -- Author, Source, Year`
- Avoid superlatives ("the best," "revolutionary") — editorial voice is measured, evidenced.
- Use hedging language appropriately: "suggests," "indicates," "is consistent with." Overclaiming damages credibility.

### Blockquote usage
Blockquotes in Editorial have a red left-border and are slightly enlarged. Use them for:
- Direct quotes from research, interviews, or primary sources.
- A single key finding stated in the most precise language.
- Your own strongest claim, set apart for emphasis.

Never use blockquotes for style. In editorial context, the red-bordered pullout quote signals "this is attributed to a source." Decoration undermines that.

### Structure recommendation
For a research or thought leadership talk using Editorial:
- Slide 1: Title slide — headline assertion, author, institution, date. H1 rule makes it feel published.
- Slides 2–3: The question being answered. Be specific. "Does X cause Y?" or "What explains the gap between A and B?"
- Slides 4–5: Context and prior work. Brief. Reference rather than summarize.
- Slides 6–10: Findings. One finding per slide. Title = the finding. Body = the evidence.
- Slides 11–13: Implications. What does this mean for practitioners, for policy, for the field?
- Slide 14: Limitations and open questions. Editorial credibility requires acknowledging what you don't know.
- Slide 15: Conclusion and references. The claim you want them to leave with, backed by the body of the talk.
