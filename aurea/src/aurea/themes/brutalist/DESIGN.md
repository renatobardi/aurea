# Brutalist — Design System

Raw. Confrontational. Unforgettable. Brutalist is the anti-theme — the deliberate rejection of polish, gradients, and visual comfort in favor of pure structural honesty. Every element is exposed. There is no decoration, only function. The frame is the frame. The text is the text. Nothing hides.

---

## 1. Visual Theme

Architectural Brutalism gave us buildings that refused to hide their structure — raw concrete, exposed steel, honest geometry. Web brutalism applied those principles to digital interfaces: thick borders, stark typography, visible grids, no apologies.

Presentation brutalism goes further. It says: the message is so important that ornamentation would distract from it. The slide is a wall. The text is spray-painted on it.

**Character**: Direct, confrontational, confident to the point of provocation. This is not a theme for people who want to be liked — it's a theme for people who want to be remembered. It works because it violates expectations. Every other slide deck looks like a deck. This one looks like a declaration.

**Influence**: Swiss grid systems taken to their logical extreme, early web design, punk zine aesthetics, constructivist propaganda posters (Rodchenko, Klutsis), the visual language of protest and urgency. Also: the work of designers who use restrictions as creative constraints — when you have only black, white, and red, every choice matters.

**Signature elements:**
- Every slide has a visible 3px black border. The container is declared.
- H1/H2/H3 are in Impact — condensed, tall, all-caps. The industrial typeface of posters and warnings.
- H3 is red. The one color intrusion. It signals the most urgent thing on the slide.
- `em` text renders red. Emphasis is visceral.
- Code blocks cast a hard offset shadow (4px, 4px, no blur) — brutalist shadows are geometric, not ambient.
- Blockquotes have an 8px red left border and a full 3px black outer border. They are contained, declared, unmissable.

**When to use**: Talks meant to disrupt, challenge, or provoke. Conference keynotes for technical audiences who are bored of polished decks. Manifestos. Calls to action. Anything where the goal is "you will not forget this."

---

## 2. Color Palette

| Role        | Hex       | Usage                                              |
|-------------|-----------|--------------------------------------------------|
| Background  | `#ffffff`  | Pure white — maximum contrast baseline           |
| Text        | `#000000`  | Pure black — no gray, no softening               |
| Red         | `#ff0000`  | Pure red — H3, em/italic, links, bullets, blockquote border, progress |
| Code bg     | `#000000`  | Black — code blocks invert the palette           |
| Code text   | `#ffffff`  | White — inside black code blocks                 |
| Surface     | `#f0f0f0`  | Table striping, blockquote background            |
| Shadow      | `#000000`  | Hard offset shadows on code blocks               |

**The three-color rule**: Brutalist operates with exactly three colors — black, white, and red. This is a hard constraint, not a guideline.

- **Black**: Structure, text, borders, weight.
- **White**: Background, space, the void between things.
- **Red**: The one place of urgency. Use it for the thing the audience must not miss.

**Why pure colors**: `#000000`, `#ffffff`, `#ff0000`. Not near-black, not off-white, not vermillion. The absoluteness of pure values is intentional. Brutalism doesn't compromise.

---

## 3. Typography

**Headings**: `Impact, "Arial Black", "Haettenschweiler", sans-serif`  
**Body**: `Arial, Helvetica, sans-serif`

| Level     | Size    | Transform | Notes                                    |
|-----------|---------|-----------|------------------------------------------|
| H1        | 3.2em   | UPPERCASE | Primary statement — fills the slide      |
| H2        | 2.2em   | UPPERCASE | Slide title — dominant, condensed        |
| H3        | 1.5em   | UPPERCASE | Red — the urgent sub-point               |
| H4        | 1.1em   | UPPERCASE | Label, category                          |
| Body      | 0.95em  | None      | Arial — functional, honest               |
| Code      | 0.75em  | None      | Courier New — the only pure monospace    |

**Impact**: A display typeface designed to pack the maximum letterforms into a narrow horizontal space. All-caps Impact was built for headlines, posters, and urgency. There is no subtlety in Impact. That's the point.

**Typography rules:**
- ALL CAPS for all headings. No exceptions. Brutalism shouts.
- Line height: 1.0 for headings. No extra leading — the letters are the measure.
- Letter spacing: 0.01em — minimal. Impact's natural condensed form is the form.
- Body text is Arial at 0.95em — unambiguously functional, common, unglamorous. The contrast with Impact is intentional.

---

## 4. Components

### Slide Border
Every slide carries a 3px solid black border. This is the signature Brutalist structural element. It declares: "this is a contained thing." The frame makes the content feel deliberately placed, not floating. It also creates a page-within-a-page effect — the slide looks like it was placed on a surface.

### Code Blocks
Black background, white monospace text. Hard offset box shadow: `4px 4px 0px #000`. No border-radius. No glow. The shadow is geometric, not ambient — Brutalism casts no soft shadows.

### Inline Code
Black background, white text. Sharp rectangle, no rounded corners. Like a typewriter key.

### Blockquotes
Full outer border (3px black) plus an extra-thick red left border (8px). Light gray background. No italics — in Brutalism, quotes are declarations, not whispers. Bold weight.

### Tables
Full grid — every cell has a 2px black border. Header row is black background, white text, all-caps. Alternating row striping in light gray. The table is a grid in the strict sense — you can see every cell as a container.

### H3 — The Red Sub-heading
The theme's only automatic color intrusion. H3 headings render red (`#ff0000`). Use H3 to mark the single most urgent, critical, or provocative point on the slide.

### `em` / Italic
Renders red, not italic. `*emphasis*` in Brutalism is not a gentle inclination — it's a fire alarm. Use for the one thing per slide that must not be missed.

---

## 5. Layout

Brutalist slides have a visible border that constrains the content area. Everything inside is structured and intentional.

**Maximum slide density**: **5 words per slide is the ideal.** Not 5 bullets — 5 words total. A single H1 statement and nothing else is the most powerful use of this theme.

**When you must have bullets**: Maximum 4. Each bullet is a complete, short statement. No sub-bullets. No explanations. The explanation belongs in your spoken words.

**Common layouts:**
1. **Manifesto**: Full-slide H1 (uppercase Impact). One statement. No subtitle.
2. **Declaration + evidence**: H2 statement + H3 red challenge + 2 bullets.
3. **Statement + counter**: H2 left, H2 right (two-column disagreement layout).
4. **Numbers**: One enormous number (H1 at 3.2em) + one line of context.
5. **Warning**: H3 in red (the warning signal) + blockquote (the evidence).

---

## 6. Depth

Brutalism has no soft depth. It has hard depth: geometry.

- **The slide border** is a depth statement — it declares the slide as a plane.
- **Code blocks** cast a hard 4px offset shadow. No blur radius. It looks stacked, not floating.
- **Blockquotes** use two borders (outer black + red left) to create contained, nested structure.
- **Table cells** have full visible borders — the grid is the depth.

**What Brutalism explicitly rejects:**
- Drop shadows with blur (soft, ambient = fake)
- Gradients (transitional, evasive = dishonest)
- Rounded corners (softening = weakness)
- Background tints that don't carry meaning

In Brutalism, "depth" is a structural question, not an aesthetic one.

---

## 7. Do's and Don'ts

### Do
- Use H1 for statements with 1–5 words. Let the Impact typeface fill the slide.
- Use H3 (red) for the single most confrontational or urgent point.
- Use `*em*` for the one red word in a sentence. Not for every other word.
- Write bullet points as complete, blunt statements: "We were wrong." "The system failed." "This works."
- Use code blocks with the hard shadow — they look intentional on this theme.
- Embrace white space inside the black border. The empty space is as deliberate as the text.
- Use the blockquote for quotable, attributable, direct statements.

### Don't
- Don't use more than 5 words in an H1. If you can't say it in 5 words, make two slides.
- Don't add soft shadows, gradients, or rounded corners anywhere.
- Don't use more than 4 bullets per slide.
- Don't use H3 for structural sub-sections — it's red, which means "urgent." Use H4 for structural labels.
- Don't use red outside of the specified elements (H3, em, links, bullets, blockquote border, progress).
- Don't add images unless they are black-and-white photographs — color photos violate the palette.
- Don't use multiple font sizes on the same slide beyond heading + body.
- Don't soften the language. Brutalist copy is direct, declarative, unhedged.

---

## 8. Responsive

Brutalist is designed for large screens and stages where impact (literally) is the goal.

**Projection:**
- Pure black on pure white has maximum contrast — readable on any projector at any brightness.
- The red accent survives even degraded projection environments.
- The slide border will appear as a visible frame even from the back of a large room.
- Impact uppercase headings at 3.2em are readable from 30+ meters away.

**Viewports:**
- At smaller screens, the slide border may clip slightly. This is acceptable — the constraint reads as intentional.
- Short, uppercase headings do not word-wrap awkwardly like long serif text would.
- Code blocks use overflow scroll — they don't break the layout.

**PDF export:**
- Black-and-white printing is as good as color — the three-color palette (black/white/red) reduces to two (black/white) without loss of hierarchy.
- The slide borders print cleanly and create a poster-like page grid.

---

## 9. Agent Prompt Guide

This section tells AI agents (Claude, Gemini, Copilot, etc.) how to create presentations using the Brutalist theme effectively.

### Core philosophy
Brutalist is the hardest theme to write for. The temptation is to fill the vast, empty white slides with text — to explain, qualify, soften. Resist this completely. The power of Brutalist comes entirely from what is NOT there. Your job is not to write slides — it is to cut everything until only the essential remains.

**The single rule**: If a slide has more than 5 words, ask "what can I cut?" Keep cutting.

### Slide creation rules
1. **Maximum 5 words for H1 slides.** A single H1 with 2–3 words and nothing else is ideal.
2. **Titles are declarations, not topics.** "WE FAILED" beats "Failure Analysis."
3. **H3 (red) for the one thing that must land.** Use it once per slide, not as a structural element.
4. **em/italic = red.** Don't use `*emphasis*` decoratively — only for the word that changes everything.
5. **No sub-bullets.** If content needs sub-bullets, it's too complex for this theme.
6. **Silence is a slide.** A single word centered in a bordered white slide is more powerful than 10 bullets.

### Word economy — the brutalist constraint
Before finalizing each slide, apply this test:
- Can this H1 be 1 word instead of 5?
- Is every bullet 4 words or fewer?
- Does any word on this slide not earn its place?

If you cannot cut a word without losing meaning, it stays. Every other word goes.

### Color usage for agents
- Red appears automatically on H3, em, bullets (markers), links, blockquote border, progress bar.
- Do NOT add any additional color. The palette is closed: black, white, red.
- Don't use bold for decorative emphasis — Impact headings are already bold. Use em (red) for the one word that matters.

### Tone — write like a protest sign
The best Brutalist slides read like protest signs, not reports:
- **Yes**: "THIS IS BROKEN", "THE DATA LIES", "START OVER", "IT WORKS"
- **No**: "Key findings from the Q3 analysis of distributed systems performance"

Short, declarative, present tense. No hedging. No qualifiers. No "however." State the thing.

### Structure recommendation
For a 12-slide Brutalist talk:
- Slide 1: Your name / talk title. H1 in Impact. 3 words maximum.
- Slide 2: THE PROBLEM. One sentence. H2. Nothing else.
- Slide 3: The evidence. 3 bullets. Each bullet: subject + verb + object. No more.
- Slides 4–7: Each slide is one claim. H1 or H2. Maybe 2 bullets.
- Slide 8: The worst moment. H3 (red). The thing that almost killed it.
- Slide 9: The turning point. H2. Short.
- Slide 10: The outcome. One number. H1 at maximum size.
- Slide 11: What you learned. H2 + 3 bullets. Complete sentences.
- Slide 12: The ask / the call. H1. 5 words or fewer.

### Warning
Brutalist presentations are high-risk, high-reward. They can feel amateurish if the content doesn't match the style — raw visual confidence demands intellectual confidence. Only use this theme if the ideas are genuinely challenging, the speaker owns the room, and the goal is to be remembered.
