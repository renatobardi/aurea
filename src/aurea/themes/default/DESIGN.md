# Default — Design System

A clean, minimal, professional design system for presentations. Neutral enough to work for any topic, any audience. Clarity and readability are the primary concerns — never decoration for its own sake.

---

## 1. Visual Theme

The Default theme is built on restraint. White space is not empty — it is the frame that gives content room to breathe. Every visual decision serves comprehension, not aesthetics.

**Character**: Professional, approachable, universal. Think internal reports, product walkthroughs, onboarding materials, all-hands meetings. Nothing here will alienate an executive or a junior engineer.

**Influence**: Stripped from editorial design traditions — the Swiss International Style — where grid, typography hierarchy, and white space do all the heavy lifting. No gradients, no textures, no decorative elements that don't carry meaning.

**When to use**: When you don't know the audience. When you want the content, not the presentation, to be the focal point. When credibility and clarity matter more than personality.

---

## 2. Color Palette

| Role       | Hex       | Usage                                      |
|------------|-----------|--------------------------------------------|
| Background | `#ffffff`  | Slide background, all surfaces             |
| Text       | `#111111`  | Body copy, lists, captions                 |
| Heading    | `#333333`  | Titles, subtitles, labels                  |
| Accent     | `#0066cc`  | Links, highlights, progress bar, callouts  |
| Muted      | `#777777`  | Secondary text, dates, metadata            |
| Surface     | `#f5f5f5`  | Code blocks, table rows, subtle backgrounds |
| Border     | `#e0e0e0`  | Dividers, table lines, card borders        |

**Color usage rules:**
- Use the accent color (`#0066cc`) for one thing per slide — the most important element that needs attention.
- Never use more than 3 colors on a single slide.
- If you need to emphasize text, use weight (bold) before color.
- Gray (`#777777`) is for context, not content. Dates, sources, speaker notes hints.

---

## 3. Typography

**Primary font**: `"Helvetica Neue", Helvetica, Arial, sans-serif`

A universally available, legible sans-serif. Present on every operating system. Excellent at all sizes, especially small body copy.

| Level     | Size    | Weight | Usage                          |
|-----------|---------|--------|--------------------------------|
| H1        | 2.4em   | 600    | Slide title (section openers)  |
| H2        | 1.7em   | 600    | Primary content heading        |
| H3        | 1.3em   | 600    | Sub-heading, callout title     |
| H4        | 1.0em   | 600    | Label, tag, micro-heading      |
| Body      | 1.0em   | 400    | Lists, paragraphs, captions    |
| Code      | 0.8em   | 400    | Inline and block code          |

**Typography rules:**
- Line height: 1.5 for body, 1.2 for headings.
- Letter spacing: -0.01em for headings (slightly tighter feels more deliberate).
- Never use ALL CAPS for entire sentences — only for short labels (3 words or fewer).
- Avoid centered text for more than 2 lines.

---

## 4. Components

### Code Blocks
Light gray background (`#f8f8f8`), monospace font, 1px border. Rounded corners (4px). Scrollable when content overflows. Maximum height: 400px. Never let code dominate the slide — if the block is the hero, it's the only element.

### Blockquotes
Left border: 4px solid accent blue. Light gray background. Italic. Use for attributions, key statements, or highlighted takeaways.

### Tables
Clean, borderless between rows except horizontal dividers. Header row has a light blue-gray background. Accent-colored bottom border on header row makes the table feel structured without being heavy.

### Lists
Standard indented bullets. 0.4em gap between items gives breathing room. Avoid nesting deeper than 2 levels — if you need 3 levels, the content belongs in a different format.

### Emphasis
- **Bold**: Use for the most important phrase in a paragraph. One bold phrase per paragraph, maximum.
- *Italic*: Use for titles of works, technical terms on first mention, or mild emphasis.
- `Code`: For filenames, function names, CLI commands, any literal string.

---

## 5. Layout

The reveal.js default layout. Slides are vertically and horizontally centered.

**Content width**: ~80% of slide width. Don't push text to the edges.

**Slide density guidelines:**
- Maximum 7 bullet points per slide.
- Maximum 2 columns of content per slide.
- A slide with only a title and 2–3 bullet points is often better than 7 compressed bullets.
- One code block OR one table per slide. Not both.
- Leave at least 20% of the slide as white space.

**Common layouts:**
1. **Title slide**: H1 title, H3 subtitle, optional metadata line below.
2. **Content slide**: H2 heading + bullet list (4–6 items).
3. **Code slide**: H2 heading + single code block. The code is the content.
4. **Quote slide**: Full-screen centered blockquote. Nothing else.
5. **Two-column**: Left 50% text/bullets, right 50% code or image.

---

## 6. Depth

The Default theme is deliberately flat. No shadows on text, no 3D effects, no gradients on backgrounds.

**Subtle depth is allowed:**
- Code blocks and pre elements may have `box-shadow: 0 2px 8px rgba(0,0,0,0.08)` — just enough to lift them off the page.
- Blockquotes use a left border as a visual anchor.
- Tables use a 2px accent-colored bottom border on the header row.

**What not to do:**
- No drop shadows on headings.
- No background gradients.
- No card-style containers with thick borders (that's for other themes).

---

## 7. Do's and Don'ts

### Do
- Start with a clear title on every slide.
- Use bullet lists for parallel concepts only — if items aren't parallel, write prose.
- Use the accent color exclusively for the single most important thing on the slide.
- Keep slides sparse. When in doubt, split into two slides.
- Write in short, scannable lines. Aim for 6–8 words per bullet.

### Don't
- Don't use more than 2 font sizes on a single slide (heading + body is enough).
- Don't center-align body text — reserve centering for titles and standalone quotes.
- Don't use accent color decoratively. No blue lines, blue boxes for style. Blue means "this matters."
- Don't mix bold, italic, and code in the same sentence.
- Don't use ALL CAPS for longer phrases — it reads as shouting.
- Don't put a paragraph on a slide. If you need a paragraph, you need a document.

---

## 8. Responsive

Reveal.js scales slides to fit the viewport automatically. The Default theme is designed at a base of 1920×1080, 16:9 ratio.

**Scaling behavior:**
- Font sizes are defined in `em` — they scale proportionally with `--r-main-font-size`.
- At small viewport sizes (phone/tablet), headings may reflow. Keep H1 titles under 8 words to prevent awkward breaks.
- Code blocks have `max-height: 400px` with scroll — they won't overflow the slide.
- Tables with more than 5 columns should be avoided; they break at smaller viewports.

**Print / PDF export:**
- White background ensures clean PDF output.
- All elements have sufficient contrast for black-and-white printing.
- Avoid relying on color alone to convey meaning — use icons or text labels too.

---

## 9. Agent Prompt Guide

This section tells AI agents (Claude, Gemini, Copilot, etc.) how to create presentations using the Default theme effectively.

### Core philosophy
The Default theme is a blank canvas, not a destination. Your job is to make the **content** compelling — this theme will not rescue weak ideas with visual flair. Think like an editor: cut, clarify, organize.

### Slide creation rules
1. **One idea per slide.** If you need a conjunction ("and", "also", "plus"), that's probably two slides.
2. **Titles as takeaways.** Write slide titles as statements, not topics. "Revenue grew 40% YoY" beats "Revenue."
3. **Maximum 6 bullets per slide.** If you have 8 items, find a way to group them into 2 categories of 4.
4. **Lead with the conclusion.** The most important point belongs on the first bullet, not the last.

### Color usage
- Use `#0066cc` (accent blue) to highlight the single most important number, word, or element on the slide. Only one use per slide.
- Body text stays `#111111`. Never change body text color for emphasis — use bold instead.
- Use `#777777` for secondary context: dates, sources, speaker annotations.

### Typography guidance
- H1 for section title slides (the ones that introduce a new topic).
- H2 for content slides with supporting bullets.
- H3 for sub-sections or callout labels inside a slide.
- Never use H4 or lower for slide titles.

### Content dos and don'ts for agents
- **Do** write titles as assertions: "Users drop off at checkout" not "Checkout conversion."
- **Do** use code blocks only for actual code or terminal output — not for quotes or callouts.
- **Do** end the deck with a clear "next steps" or "call to action" slide.
- **Don't** write slides with more than 3 lines of prose. This is not a document.
- **Don't** include slide numbers in the content — reveal.js handles that.
- **Don't** use tables with more than 5 columns or 8 rows.

### Structure recommendation
For a standard 15–20 slide deck using Default:
- Slides 1: Title + presenter info
- Slides 2–3: Problem / context (short bullets, high contrast)
- Slides 4–10: Core content (one idea per slide, code or tables where appropriate)
- Slides 11–13: Results / evidence (use numbers prominently)
- Slides 14–15: Conclusion and next steps
