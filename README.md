# Aurea v0.1.0

Generate high-quality, standalone HTML presentations via AI agents. Write slides in Markdown, guide your agent through a structured workflow, and get a beautiful reveal.js presentation that works offline—no design skills or CSS required.

## Why Aurea?

- **Standalone HTML**: All CSS, JavaScript, and fonts inlined. Works offline in any browser. Send via email, USB stick, airplane mode.
- **AI-Guided Workflow**: 7 structured prompt templates guide your agent through outline → generate → refine → visual → build.
- **64 Professional Themes**: 5 original designs + 59 imported from real design systems (Apple, Stripe, Linear, Figma, Notion, etc.).
- **4 Distribution Modes**: Use templates in your agent, run the CLI, or grab a standalone executable. All produce identical output.
- **Zero Design Skills Required**: No CSS, no reveal.js config, no design knowledge. Focus on content; let your agent and Aurea handle the rest.
- **Python 3.8+**: Runs on Windows 7+, macOS 10.13+, Linux glibc 2.17+. Designed for corporate environments.

## Quick Start

### 1. Initialize a Project

```bash
# Install Aurea
pip install aurea
# or: uv tool install aurea
# or: download standalone from releases

# Create a new presentation
aurea init my-talk --agent claude --theme stripe
cd my-talk
```

This creates:
```
my-talk/
├── .aurea/
│   ├── config.json              # Project settings (agent, theme)
│   └── themes/stripe/           # Stripe theme (DESIGN.md, CSS, layout)
├── .claude/commands/            # 7 agent command templates
├── slides/                       # Your Markdown slides go here
├── output/                       # HTML output directory
└── README.md                     # Project guide
```

### 2. Create Your Presentation

In your AI agent (Claude Code, Gemini CLI, ChatGPT, etc.):

```
/aurea.outline "Talk on microservices for senior engineers"
```

The agent reads the design system and creates `slides/outline.md` with:
- Audience, objectives, tone
- Narrative arc (opening → development → climax → conclusion)
- Slide plan with timing estimates

Then:
```
/aurea.generate      # Create full slides from outline
/aurea.refine        # Edit slides (e.g., "Add more data to slide 3")
/aurea.visual        # Add SVG/CSS visuals to slides
/aurea.build         # Compile to HTML
```

### 3. Preview & Share

```bash
# Start live preview
aurea serve --watch

# Open http://127.0.0.1:8000/presentation.html
# Edit slides, auto-rebuild on save

# Output is ready to share
# Send output/presentation.html via email, USB, cloud storage
# Works offline in any browser
```

---

## Installation

### Option 1: pip (Standard)

```bash
pip install aurea

# With optional theme extraction:
pip install aurea[extract]
```

**Requires:** Python 3.8+

### Option 2: Zipapp (Single File)

```bash
# Download from releases
curl -L https://github.com/renatobardi/aurea/releases/latest/download/aurea.pyz -o aurea.pyz
curl -L https://github.com/renatobardi/aurea/releases/latest/download/aurea.pyz.sha256 -o aurea.pyz.sha256

# Verify integrity
sha256sum -c aurea.pyz.sha256

# Run with Python
python aurea.pyz init my-talk --agent claude --theme stripe
```

**Requires:** Python 3.8+

### Option 3: Standalone Executable (No Python)

Download from [releases page](https://github.com/renatobardi/aurea/releases):

| Platform | File | SHA256 |
|----------|------|--------|
| Windows | `aurea.exe` | `aurea.exe.sha256` |
| macOS (Intel) | `aurea` | `aurea.sha256` |
| macOS (Apple Silicon) | `aurea.app` | `aurea.app.sha256` |
| Linux | `aurea` | `aurea.sha256` |

Verify integrity before running:
```bash
# macOS / Linux
sha256sum -c aurea.sha256

# Windows (PowerShell)
Get-FileHash aurea.exe | Select-String (Get-Content aurea.exe.sha256).Split()[0]
```

No Python required. Works on Windows 7+, macOS 10.13+, Linux glibc 2.17+.

### Option 4: Zero-Install (No CLI)

Copy agent command templates from this repo:

```bash
git clone https://github.com/renatobardi/aurea.git
cp -r aurea/src/aurea/agent_commands/claude ~/.claude/commands/
```

Use agent commands in your AI agent. No CLI needed. Works completely offline.

---

## Usage

### Initialize a Project

```bash
aurea init <project-name> [options]

Options:
  --agent {claude|gemini|copilot|windsurf|devin|chatgpt|cursor|generic}
           AI agent to configure (default: claude)
  --theme {theme-id}
           Theme to use (default: default)
  --here   Initialize in current directory instead of creating subdirectory
  --force  Overwrite existing project
  --no-git Skip git initialization
  --lang {en|pt-br|...}
           Language for templates (default: en)
```

### Build

```bash
aurea build [options]

Options:
  --input <file>      Input Markdown file (default: slides/presentation.md)
  --output <file>     Output HTML file (default: output/presentation.html)
  --theme <id>        Override active theme
  --minify            Minify HTML (smaller output)
  --embed-fonts       Embed fonts as base64 (larger file, works without @font-face)
  --watch             Rebuild on file changes
```

### Preview

```bash
aurea serve [options]

Options:
  --port <n>    Server port (default: 8000, auto-increment if busy)
  --host <addr> Server address (default: 127.0.0.1)
  --watch       Auto-rebuild on file changes + live reload
```

### Theme Management

```bash
# List all available themes
aurea theme list

# Search themes by keyword
aurea theme search "dark minimal"

# Show theme details and colors
aurea theme info stripe

# Display theme design system
aurea theme show stripe

# Apply theme to current project
aurea theme use linear

# Create custom theme
aurea theme create my-brand
```

### Extract Design System from URL

```bash
aurea extract https://linear.app --name linear-custom

Options:
  --name <id>      Theme name (required)
  --depth <n>      Crawl depth (default: 1, max: 3)
  --raw            Generate raw tokens without AI refinement
  --use            Apply extracted theme to current project
  --timeout <s>    HTTP timeout (default: 30)
```

---

## Themes

**64 themes included** in the registry:

### Original Designs (5)
- `default` — Clean, minimal, professional
- `midnight` — Dark, elegant, high contrast
- `aurora` — Colorful, modern, gradient-heavy
- `editorial` — Typography-focused, print-inspired
- `brutalist` — Harsh, raw, anti-design

### Imported from [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (59)

Design systems from real companies and projects:
- **Tech**: stripe, linear, apple, figma, notion, vercel, github, slite
- **Automotive**: ferrari, lamborghini, porsche
- **AI/ML**: openai, anthropic, midjourney, stability, huggingface
- **Finance**: stripe, square, wise, kraken, coinbase
- **Social**: twitter, instagram, tiktok, discord
- **Design**: dribbble, behance, figma, framer
- **And 40+ more...**

Search by mood or category:

```bash
aurea theme search "dark minimal elegant"
aurea theme search --category design --tag gradient
```

---

## Project Structure

After `aurea init my-talk`:

```
my-talk/
├── .aurea/                          # Aurea configuration
│   ├── config.json                  # Project settings (agent, theme)
│   └── themes/
│       ├── stripe/                  # Active theme files
│       │   ├── DESIGN.md            # Design system specification
│       │   ├── theme.css            # Theme stylesheet
│       │   ├── layout.css           # Grid & layout overrides
│       │   └── meta.json            # Theme metadata
│       └── registry.json            # Local theme index
├── .claude/commands/                # Agent command templates
│   ├── aurea.outline.md             # Step 1: Plan narrative
│   ├── aurea.generate.md            # Step 2: Create slides
│   ├── aurea.refine.md              # Step 3: Edit slides
│   ├── aurea.visual.md              # Step 4: Add visuals
│   ├── aurea.theme.md               # Manage themes
│   ├── aurea.extract.md             # Extract design from URL
│   └── aurea.build.md               # Build to HTML
├── slides/                           # Your Markdown files
│   ├── presentation.md              # Main slides (or multiple files)
│   └── .gitkeep
├── output/                           # Generated output
│   ├── presentation.html            # Standalone reveal.js presentation
│   └── .gitkeep
└── README.md                         # Project guide
```

---

## Slide Format

### Basic Slides

```markdown
---
title: "My Presentation"
author: "Your Name"
theme: stripe
---

# Slide 1: Title

This is your first slide.

---

# Slide 2: Content

- Bullet 1
- Bullet 2

```code
console.log("code blocks are supported");
```

---

# Slide 3: With Speaker Notes

Main slide content here.

Note: Speaker notes go here. Not visible in presentation mode (unless notes plugin enabled).
```

### Slide Attributes

```markdown
# Slide with Custom Background

<!-- .slide: data-background-color="#ffffff" data-transition="fade" -->

Custom reveal.js attributes work here.
```

### Rules

- **Separator**: Use `---` on its own line to separate slides
- **Word limit**: Max 40 words per slide (excluding speaker notes) — keeps slides focused
- **Speaker notes**: Start with `Note:` on its own line
- **Code blocks**: Fenced with ` ``` ` — syntax highlighting automatic (Pygments)
- **Attributes**: HTML comment with `<!-- .slide: ... -->` for reveal.js options

---

## Frontmatter

The YAML block at the top of `presentation.md`:

```yaml
---
title: "My Presentation Title"
author: "Your Name"
theme: stripe
---
```

**Fields:**
- `title`: Presentation title (appears in browser tab and HTML metadata)
- `author`: Author name (HTML metadata)
- `theme`: Default theme (overridable with `aurea build --theme`)

---

## Output Guarantee

The generated HTML is **100% standalone**:

✅ **Included:**
- reveal.js 5.2.1 core (inlined)
- All CSS (theme + reveal.js + syntax highlighting)
- Fonts (as CSS custom properties or base64)
- Syntax highlighting definitions

❌ **NOT included:**
- External CSS links (`<link href="https://...">`)
- External script tags (`<script src="https://...">`)
- CDN references
- Web fonts via Google Fonts API

**Result:** Works offline in any browser, anytime, anywhere. Email it, put it on a USB stick, open it on an airplane.

---

## Design System (DESIGN.md)

Each theme includes a `DESIGN.md` with **9 required sections**:

1. **Visual Theme** — Overall character, mood, inspiration
2. **Color Palette** — Named colors with semantic roles (primary, secondary, background, surface, text, accent)
3. **Typography** — Heading and body font families, sizes, weights, line heights
4. **Components** — Buttons, cards, code blocks, form elements, visual styles
5. **Layout** — Grid, spacing, proportions, alignment rules
6. **Depth** — Shadows, z-index layers, 3D effects if applicable
7. **Do's & Don'ts** — Visual guidelines (what works, what doesn't)
8. **Responsive** — Mobile breakpoints, touch targets, readability at different sizes
9. **Agent Prompt Guide** — Instructions for AI agents on how to design slides using this theme

---

## Agent Commands (7 Templates)

All 7 commands follow the same pattern:

1. **Load context** (DESIGN.md, config, current slides)
2. **Generate or refine** (using design system guidance)
3. **Validate** (against design system constraints)
4. **Output** (markdown to slides directory)

### Workflow Phases

| Command | Input | Output | Purpose |
|---------|-------|--------|---------|
| `/aurea.outline` | Topic + audience | `slides/outline.md` | Plan narrative structure |
| `/aurea.generate` | Outline + DESIGN.md | `slides/presentation.md` | Create full slides |
| `/aurea.refine` | Feedback | Updated slides | Edit & improve |
| `/aurea.visual` | Slide list | Updated slides with visuals | Add SVG/CSS/mermaid |
| `/aurea.theme` | Theme ID | Updated theme in .aurea/ | Manage themes |
| `/aurea.extract` | URL | New DESIGN.md + CSS | Extract design system |
| `/aurea.build` | (none) | `output/presentation.html` | Compile to HTML |

Each command is independent and can be used standalone.

---

## Examples

### Example 1: Quick Presentation (Zipapp)

```bash
python aurea.pyz init "Kubernetes for Devs" --agent claude --theme linear
cd "Kubernetes for Devs"

# Use in Claude Code:
# /aurea.outline "Kubernetes for developers, 30 min talk, hands-on audience"
# /aurea.generate
# /aurea.refine "Add more YAML examples to slide 4"
# /aurea.visual
# /aurea.build

aurea serve --watch
# Open http://127.0.0.1:8000/presentation.html
```

### Example 2: Corporate Deployment (PyInstaller)

```bash
# IT distributes aurea.exe via SCCM
# User runs:
aurea.exe init "Q2 Strategy" --agent claude --theme default
cd "Q2 Strategy"

# User creates slides/presentation.md manually or with agent
# Build:
aurea.exe build --minify --embed-fonts

# Share output/presentation.html via internal portal
```

### Example 3: Theme Extraction

```bash
aurea init "Design Showcase" --agent claude

# Extract Stripe's design system
aurea extract https://stripe.com --name stripe-custom --depth 2

# Apply it
aurea theme use stripe-custom
aurea serve --watch

# Now create presentations with Stripe's colors & typography
```

---

## Supported AI Agents

Aurea works with any AI agent via command templates:

| Agent | Command Dir | Format | Placeholder |
|-------|-------------|--------|-------------|
| **Claude Code** | `.claude/commands/` | `.md` | `$ARGUMENTS` |
| **Gemini CLI** | `.gemini/commands/` | `.toml` | `{{args}}` |
| **GitHub Copilot** | `.github/copilot-instructions/` | `.agent.md` | `$ARGUMENTS` |
| **Windsurf** | `.windsurf/commands/` | `.md` | `$ARGUMENTS` |
| **Devin** | `.devin/commands/` | `.md` | `$ARGUMENTS` |
| **ChatGPT** | `.chatgpt/commands/` | `.md` | `$ARGUMENTS` |
| **Cursor** | `.cursor/commands/` | `.md` | `$ARGUMENTS` |
| **Generic** | `commands/` | `.md` | `$ARGUMENTS` |

Templates are provided for all agents. They're versioned and frozen in distributions.

---

## Development

### Setup

```bash
git clone https://github.com/renatobardi/aurea.git
cd aurea

python -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate (Windows)

pip install -e ".[dev,extract]"
```

### Commands

```bash
# Lint & format
ruff check .
ruff format .

# Type check
mypy src/

# Tests
pytest                        # All tests
pytest tests/unit/            # Unit only
pytest -k "test_build"        # Single test
pytest --cov=src              # With coverage

# Build distributions
python -m PyInstaller ./build/aurea.spec
python -m shiv -c aurea -o aurea.pyz .
```

### Testing Requirements

- **Unit tests** (157+): Isolated functions, mock I/O
- **Integration tests**: End-to-end workflows, real filesystem
- **Coverage**: ≥80% for `src/aurea/`
- **All tests must pass** before merge to main

---

## Architecture

**For developers contributing to Aurea:**

See [CLAUDE.md](CLAUDE.md) for:
- Project structure and key entry points
- Build pipeline internals (parse → resolve → render → inline)
- CLI routing and command implementations
- Common development tasks (adding themes, modifying pipeline, extraction)
- Dependency map and module relationships
- Testing conventions (unit vs. integration)
- Common pitfalls and design constraints
- Implementation patterns specific to this project

**For users understanding how presentations are built:**

See [docs/architecture.md](docs/architecture.md) for:
- Component interactions
- Data flow through the build pipeline
- Theme system and registry structure
- Caching and performance considerations

---

## Limitations & Roadmap

### v0.1.0 Limitations

- **No PDF export** — reveal.js in browser only
- **No speaker mode** — Notes visible in source, not in presenter view
- **Single language** — English templates only (localizations planned)
- **Limited mermaid** — Renders via mistune, not as SVG
- **No theme marketplace** — Extract manually or use bundled themes

### Planned (Milestone 6+)

- i18n (Portuguese, Spanish, French, Chinese)
- PDF export (headless Chrome)
- Remote presenter mode (WebRTC)
- Theme marketplace & community sharing
- Mermaid diagram rendering
- Custom animation presets

---

## License

MIT License — See LICENSE file

---

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Write tests (unit + integration)
4. Run linting & coverage checks
5. Open a pull request

---

## Links & Resources

**For End Users:**
- **GitHub**: https://github.com/renatobardi/aurea
- **Full Specification**: [aurea-spec.md](aurea-spec.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)

**For Developers:**
- **Developer Guide**: [CLAUDE.md](CLAUDE.md) — Entry points, common tasks, dependencies, gotchas
- **Architecture Details**: [docs/architecture.md](docs/architecture.md)
- **Theme System**: [docs/theme-system.md](docs/theme-system.md)
- **Agent Commands**: [docs/agent-commands.md](docs/agent-commands.md)

---

**Status**: Production-ready (v0.1.0)  
**Last Updated**: 2026-04-11  
**Requires**: Python 3.8+
