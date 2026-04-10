# Aurea

Toolkit for generating high-quality standalone HTML presentations via AI agents. Write slides in Markdown, use structured prompt templates to guide any AI agent through the creation workflow, and get a reveal.js presentation that works offline in any browser.

## How it works

1. `aurea init my-talk` — scaffold a project with your AI agent's command directory populated
2. Run `/aurea.outline`, `/aurea.generate`, `/aurea.refine`, `/aurea.visual` in your agent
3. `aurea build` — compile Markdown slides into a standalone HTML file (~300 KB, zero external dependencies)
4. `aurea serve` — live preview with hot reload

No design skills required. No CSS, no reveal.js configuration.

## Installation

**pip / uv / pipx** (recommended for developers)
```bash
pip install aurea
# or
uv tool install aurea
```

**Zipapp** (single file, Python 3.8+, no pip needed)
```bash
curl -L https://github.com/renatobardi/aurea/releases/latest/download/aurea.pyz -o aurea.pyz
python aurea.pyz --version
```

**Standalone executable** (no Python required, Windows/macOS/Linux)
```bash
# Download aurea.exe / aurea / aurea.app from GitHub Releases
```

**Zero-install** (copy & paste, no CLI, no Python)
```
Copy src/aurea/agent_commands/<your-agent>/ into your agent's commands directory.
All 7 prompts work independently — no CLI needed.
```

## Quickstart

```bash
# Create a project
aurea init my-talk --agent claude --theme stripe

cd my-talk

# In your AI agent, run the workflow commands:
# /aurea.outline "Talk on distributed systems for senior engineers"
# /aurea.generate
# /aurea.refine "Make slide 3 more concrete with numbers"
# /aurea.visual
# /aurea.build

# Or build directly from existing slides:
aurea build

# Preview
aurea serve
# → http://127.0.0.1:8000/presentation.html
```

## Supported AI agents

| Agent | Commands directory | Format |
|-------|--------------------|--------|
| Claude Code | `.claude/commands/` | `.md` |
| Gemini CLI | `.gemini/commands/` | `.toml` |
| GitHub Copilot | `.github/copilot-instructions/` | `.agent.md` |
| Windsurf | `.windsurf/commands/` | `.md` |
| Devin | `.devin/commands/` | `.md` |
| ChatGPT | `.chatgpt/commands/` | `.md` |
| Cursor | `.cursor/commands/` | `.md` |
| Generic | `commands/` | `.md` |

## Themes

64 themes included: 5 original designs + 59 imported from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md).

```bash
aurea theme list                        # browse all 64 themes
aurea theme search "dark minimal"       # search by mood/style
aurea theme info stripe                 # colors, typography, mood
aurea theme use linear                  # apply to current project
aurea theme create my-brand             # scaffold a custom theme
```

## Theme extraction

Extract a design system from any public URL:

```bash
aurea extract https://linear.app --name linear-custom
```

Generates `DESIGN.md` + `theme.css` + `layout.css` + `meta.json` from the site's CSS tokens.

## Build options

```bash
aurea build                             # slides/ → output/presentation.html
aurea build --theme midnight            # override active theme
aurea build --minify                    # smaller output
aurea build --embed-fonts               # embed woff2 fonts as base64
aurea build --watch                     # rebuild on file changes
aurea serve --watch                     # serve + rebuild + reload
```

## Project structure

After `aurea init`:

```
my-talk/
├── .aurea/
│   ├── config.json          # active agent + theme
│   └── themes/
│       ├── stripe/          # DESIGN.md, theme.css, layout.css, meta.json
│       └── registry.json    # local theme index
├── .claude/commands/        # 7 prompt templates (agent-specific)
├── slides/                  # your Markdown files go here
├── output/                  # presentation.html generated here
└── README.md
```

## Output

The generated HTML is 100% standalone:
- reveal.js 5.x inlined
- All CSS inlined
- highlight.js for syntax highlighting
- No `<link href="https://...">` or `<script src="https://...">`
- Works offline, in email, on a USB stick

## Development

```bash
git clone https://github.com/renatobardi/aurea
cd aurea
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,extract]"

pytest                          # all tests
pytest tests/unit/              # unit only
pytest --cov=src                # with coverage
ruff check . && mypy src/       # lint + types
```

Coverage target: ≥ 80% for `src/aurea/`.

## Documentation

- [Architecture](docs/architecture.md) — build pipeline internals
- [Theme system](docs/theme-system.md) — DESIGN.md format, registry schema
- [Agent commands](docs/agent-commands.md) — 7 workflow phases explained
- [Full spec](aurea-spec.md) — complete product specification

## License

MIT
