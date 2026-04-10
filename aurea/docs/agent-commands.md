# Aurea Agent Commands

## Overview

Aurea ships 7 prompt templates that guide AI agents through a structured presentation creation workflow. Each template is pre-built for 8 agent formats (56 total files).

## The 7 Commands

### 1. `/aurea.theme`
**Purpose**: Select and internalize the active design system.

The agent reads `DESIGN.md` from the active theme, internalizes the color palette, typography rules, component styles, and the "Agent Prompt Guide" section. This is typically the first command in any presentation workflow.

**Key behavior**: The agent does NOT generate slides yet — it only loads the design context that will constrain all subsequent commands.

### 2. `/aurea.outline`
**Usage**: `/aurea.outline "<topic>"`

**Purpose**: Plan the presentation narrative before generating any slides.

The agent produces `slides/outline.md` with:
- Audience and objective
- Narrative arc (opening → development → climax → conclusion)
- Slide-by-slide plan with time estimates
- Visual constraints from DESIGN.md

**Why outline first**: Forces the agent to think structurally before content, avoiding disconnected slides.

### 3. `/aurea.generate`
**Purpose**: Generate the full presentation Markdown from the outline.

The agent reads `outline.md` + `DESIGN.md` and produces `slides/presentation.md` in reveal.js format:
- Slides separated by `---`
- Speaker notes using `Note:` blocks
- HTML attributes using `<!-- .slide: ... -->`
- Max 40 words per slide (enforced by the prompt)
- Visual placeholder comments: `<!-- VISUAL: description -->`

### 4. `/aurea.refine`
**Usage**: `/aurea.refine "<instructions>"`

**Purpose**: Improve specific slides or the overall presentation.

The agent reads the current `presentation.md`, applies targeted changes, and validates the result against `outline.md` and `DESIGN.md`. Reports what changed.

### 5. `/aurea.visual`
**Purpose**: Add visual elements to slides marked with `<!-- VISUAL: ... -->`.

The agent identifies visual placeholders, reads DESIGN.md for palette and constraints, and generates SVG graphics, mermaid diagrams, or CSS backgrounds inline in the presentation.

### 6. `/aurea.extract`
**Usage**: `/aurea.extract "<url>" [name: "<theme-name>"]`

**Purpose (Mode 2+)**: Run `aurea extract <url>` to scrape a site's design tokens.

**Purpose (Mode 1 fallback)**: When the CLI is not available, the agent uses native web fetch to retrieve the URL, parse CSS, extract colors and fonts, and generate `DESIGN.md` + `theme.css` directly.

This command is intentionally dual-mode to support zero-install environments.

### 7. `/aurea.build`
**Purpose (Mode 2+)**: Run `aurea build` to compile Markdown to standalone HTML.

**Purpose (Mode 1 fallback)**: Generate complete reveal.js HTML inline, embedding all CSS and JavaScript, producing a self-contained presentation file without running any CLI tool.

## Workflow Order

```
/aurea.theme    ← Load design context
/aurea.outline  ← Plan narrative
/aurea.generate ← Draft all slides
/aurea.refine   ← Polish (repeat as needed)
/aurea.visual   ← Add visual elements
/aurea.build    ← Compile to HTML
```

`/aurea.extract` is an optional preprocessing step that creates a new theme from any website before starting the main workflow.

## Agent Formats

| Agent | Directory | Format | Arg placeholder |
|-------|-----------|--------|----------------|
| Claude | `.claude/commands/` | `.md` | `$ARGUMENTS` |
| Gemini | `.gemini/commands/` | `.toml` | `{{args}}` |
| Copilot | `.github/copilot-instructions/` | `.agent.md` | `$ARGUMENTS` |
| Windsurf | `.windsurf/commands/` | `.md` | `$ARGUMENTS` |
| Devin | `.devin/commands/` | `.md` | `$ARGUMENTS` |
| ChatGPT | `.chatgpt/commands/` | `.md` | `$ARGUMENTS` |
| Cursor | `.cursor/commands/` | `.md` | `$ARGUMENTS` |
| Generic | `.commands/` | `.md` | `$ARGUMENTS` |

## Template Principles

All 7 templates follow these principles:

1. **Context-first**: Load DESIGN.md and config.json before doing anything
2. **Design system respect**: Every output decision references the active theme
3. **Narrative arc**: Outline must include an opening, development, and conclusion
4. **Slides are lean**: Hard limit of 40 words per slide (speaker notes are unlimited)
5. **Speaker notes are first-class**: Every slide should have notes for the presenter
6. **Visual-first**: Flag slides needing visuals before drafting text
7. **Do's and Don'ts**: Always check the theme's constraints before generating

## Installing Commands

Run `aurea init` to install all 7 templates for your agent:

```bash
aurea init my-presentation --agent claude --theme default
```

This copies the pre-built templates from `src/aurea/agent_commands/claude/` to `.claude/commands/` in your project, with project-specific paths substituted.

## Zero-Install (Mode 1)

Users without Python can copy templates manually:

1. Go to `src/aurea/agent_commands/<your-agent>/`
2. Copy the 7 files to your agent's commands directory
3. Edit the `{{DESIGN_MD_PATH}}` placeholder to point to your DESIGN.md
4. The templates will guide the agent through the full workflow without any CLI
