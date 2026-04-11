# Aurea Architecture

## Overview

Aurea is a Python CLI toolkit that converts structured Markdown presentations into standalone HTML files using reveal.js. The architecture prioritizes portability (Python 3.8+, four distribution modes) and offline output (all assets inlined, no CDN dependencies).

## Component Map

```
src/aurea/
├── cli.py              — Typer entry point, command registration
├── commands/
│   ├── init.py         — Project scaffolding (aurea init)
│   ├── build.py        — Markdown → HTML pipeline (aurea build)
│   ├── serve.py        — Local HTTP server (aurea serve)
│   ├── theme.py        — Theme registry and management (aurea theme *)
│   └── extract.py      — Design extraction from URLs (aurea extract)
├── _http.py            — robots.txt check + httpx wrapper (lazy-imported)
├── _log.py             — Structured logging to stderr via Rich
├── _regex.py           — Compiled regex constants
├── _tpl.py             — Jinja2 environment
├── exceptions.py       — AureaError base exception
├── templates/
│   ├── reveal.html.j2  — Base reveal.js HTML template (all assets inlined)
│   └── slide_readme.md.j2 — Project README template
├── themes/             — Bundled themes (default, midnight, aurora, editorial, brutalist + 59 imported)
│   └── registry.json   — Master theme index
├── agent_commands/     — Pre-built prompt templates (7 commands × 8 agents)
└── vendor/revealjs/    — reveal.js 5.2.1 vendored (no CDN)
```

## Build Pipeline

The core pipeline runs in `commands/build.py`:

```
Markdown input (slides/presentation.md)
    │
    ▼  parse_slides()
Presentation dataclass
    │   - slides list (markdown, notes, attributes, word_count)
    │   - title, author, theme from YAML frontmatter
    │
    ▼  resolve_theme()
(theme_id, theme_dir)
    │   Precedence: --theme CLI > config.json > frontmatter > "default"
    │   Lookup: .aurea/themes/ first, then src/aurea/themes/ (global)
    │
    ▼  render_slides()
Presentation with html field set per slide
    │   Uses mistune (escape=False) + Pygments — raw HTML blocks (SVG, figure, div) pass through verbatim
    │
    ▼  inline_assets()
assets dict (CSS strings, JS strings)
    │   Reads vendor/revealjs/dist/* files
    │   Reads theme.css, layout.css from theme_dir
    │
    ▼  render_template("reveal.html.j2")
HTML string
    │
    ▼  EXTERNAL_LINK.sub("", html)  # Art. III safety net
    │
    ▼  write to output/presentation.html
```

## Theme System

Each theme is a directory with four files:

| File | Purpose |
|------|---------|
| `DESIGN.md` | Design system spec (9 sections, human-readable + agent-parseable) |
| `theme.css` | CSS custom properties (`--r-*` for reveal.js) |
| `layout.css` | Grid, animations, layout overrides |
| `meta.json` | Registry metadata (id, name, category, tags, mood, colors, typography) |

The global registry at `src/aurea/themes/registry.json` indexes all bundled themes. A local project can have additional themes in `.aurea/themes/` with a local `registry.json` — local entries shadow global ones by id.

## Agent Commands

Seven prompt templates guide AI agents through the presentation workflow:

1. `/aurea.theme` — Select and understand the design system
2. `/aurea.outline` — Plan narrative arc and slide structure
3. `/aurea.generate` — Generate slides Markdown from outline
4. `/aurea.refine` — Improve specific slides
5. `/aurea.visual` — Add SVG/CSS visual elements
6. `/aurea.extract` — Extract design from a URL (or Mode 1 fallback)
7. `/aurea.build` — Compile to HTML (or generate inline for Mode 1)

Templates are pre-built for 8 agent formats: Claude (.md), Gemini (.toml), Copilot (.agent.md), and `.md` for Windsurf, Devin, ChatGPT, Cursor, and Generic.

## Distribution Modes

| Mode | Mechanism | Python required |
|------|-----------|----------------|
| Zero-install | Copy `agent_commands/` to agent | No |
| Zipapp | Single `.pyz` with vendored deps | 3.8+ |
| PyInstaller | `.exe` / `.bin` binary | No |
| pip/uv | Traditional install | 3.8+ |

## Dependency Rules (Art. VII)

- Core: `typer[all]`, `jinja2`, `mistune`, `rich`, `watchdog`, `pyyaml`
- Extract (optional): `httpx`, `beautifulsoup4`, `cssutils`, `lxml`
- `httpx` and `bs4` are **lazy-imported** inside `extract.py` and `_http.py`
- Install target: `<50MB` total

## Key Constraints

- **Python 3.8+**: No walrus operator, no pipe unions in type hints, no match/case
- **Art. I exception**: `from __future__ import annotations` is forbidden in `cli.py` and `commands/serve.py` (breaks Typer's `Annotated` at runtime on Python 3.8)
- **Art. III**: HTML output MUST be 100% standalone — no `<link href="https://...">` or `<script src="https://...">`
- **Art. VIII**: reveal.js 5.x only (pinned to `>=5.0.0,<6.0`), vendored in `src/aurea/vendor/revealjs/`
