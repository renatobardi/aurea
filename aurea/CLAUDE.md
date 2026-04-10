# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aurea** is a toolkit for generating high-quality HTML presentations via AI agents (Claude Code, Gemini CLI, ChatGPT, Devin, Windsurf, etc.). It emphasizes **portability** and **minimal friction** across different environments—Windows corporate machines, macOS, Linux—without requiring complex toolchains.

The project centers on:
- **CLI** (Python): scaffolding, building, serving, theme management
- **Prompt templates**: structured guides for AI agents through presentation creation phases
- **Design system**: 40+ themes based on real-world design systems (Apple, Stripe, Linear, etc.)
- **Standalone HTML output**: reveal.js-based, offline-capable, no external dependencies

See `aurea-spec.md` for the complete specification.

## Technology Stack

| Layer | Tech | Purpose |
|-------|------|---------|
| CLI | Python 3.8+ / Typer | Portability, argument parsing, ease of distribution |
| Templates | Jinja2 | Lightweight HTML generation |
| Presentation Engine | reveal.js 5.x | Standard, offline-capable, extensible |
| Theme System | Markdown (DESIGN.md) + CSS | Single source of truth for design |
| Web Scraping | httpx + BeautifulSoup4 + cssutils | Theme extraction from URLs |
| Package Manager Support | pip, uv, pipx, PyInstaller, zipapp | Four distribution modes |
| Testing | pytest + pytest-cov | Unit and integration tests |
| Code Quality | ruff (linting), mypy (type checking) | Consistency across Python code |
| CI/CD | GitHub Actions | Lint, test, build, release on all platforms |

## Distribution Modes (Portability Strategy)

The project supports **four modes**, each self-contained:

1. **Zero-install (copy & paste)**: Clone/download, copy `commands/` dir to agent, create slides in Markdown, invoke agentcommands inline. No CLI needed, no dependencies.

2. **Zipapp (Python 3.8+)**: Single `.pyz` file containing vendored dependencies. One command to install, zero pip/uv friction. Works on Windows, macOS, Linux.

3. **Standalone Executable (PyInstaller)**: `.exe` (Windows), binaries (macOS/Linux). No Python required. Distribution via SCCM, Intune, Artifactory.

4. **Package Manager (pip/uv/pipx)**: Traditional install for developers. Also works in CI/CD, air-gap environments (wheel bundles).

**Key principle**: Each mode must be fully functional. No mode is "limited"—they differ in convenience, not capability.

## Project Structure

```
aurea/
├── src/aurea/
│   ├── cli.py              # Typer entry point (init, build, serve, theme, extract)
│   ├── init.py             # Scaffolding logic
│   ├── build.py            # Markdown → HTML pipeline
│   ├── serve.py            # Live reload server (watchdog for hot reload)
│   ├── theme.py            # Theme listing, searching, applying
│   ├── extract.py          # Web scraping & design extraction
│   ├── _tpl.py             # Jinja2 template management
│   ├── _regex.py           # Regex utilities for parsing
│   ├── _http.py            # HTTP utilities (httpx wrapper)
│   ├── _log.py             # Logging config (structured logging to stderr)
│   └── __init__.py
├── src/aurea/agent_commands/
│   ├── claude/
│   │   ├── aurea.outline.md
│   │   ├── aurea.generate.md
│   │   ├── aurea.refine.md
│   │   ├── aurea.visual.md
│   │   ├── aurea.theme.md
│   │   ├── aurea.extract.md
│   │   └── aurea.build.md
│   ├── gemini/              (same 7 commands, .md format)
│   ├── copilot/             (same 7 commands, .md format)
│   └── ... (other agents: windsurf, devin, etc.)
├── src/aurea/themes/
│   ├── registry.json        (master index of all themes with metadata)
│   ├── default/
│   │   ├── DESIGN.md        (design system spec, parsed by extract.py)
│   │   ├── theme.css        (reveal.js theme CSS)
│   │   ├── layout.css       (grid, animations)
│   │   └── meta.json        (search metadata)
│   ├── midnight/, aurora/, ... (40+ themes from awesome-design-md)
├── src/aurea/templates/
│   ├── reveal.html          (base reveal.js template, vendored)
│   └── slide.md             (Markdown template for new projects)
├── tests/
│   ├── unit/
│   │   ├── test_cli.py
│   │   ├── test_build.py
│   │   ├── test_theme.py
│   │   └── test_extract.py
│   ├── integration/         (end-to-end: init → build → output)
│   └── fixtures/            (sample slides, themes, expected HTML)
├── docs/
│   ├── architecture.md      (how build pipeline works)
│   ├── theme-system.md      (DESIGN.md format, registry structure)
│   └── agent-commands.md    (workflow phases, command descriptions)
├── build/
│   └── aurea.spec           (PyInstaller spec for standalone .exe/.bin)
├── pyproject.toml           (Python 3.8+, dependencies, entry points)
├── ruff.toml                (linting & formatting config)
├── .github/workflows/
│   ├── 1-lint-test.yml      (PR checks: ruff, mypy, pytest)
│   ├── 2-build-dist.yml     (release: PyInstaller, zipapp, PyPI publish)
│   └── 3-sync-themes.yml    (nightly: fetch from awesome-design-md)
└── aurea-spec.md            (full specification & design decisions)
```

**Current Status**: Phase 0 (spec written, repo initialized). Implementation begins in Phase 1.

## Before Starting Implementation (Phase 1)

**To bootstrap Phase 1, create these files in this order:**

1. **pyproject.toml** — Project metadata and dependencies
   - Name: `aurea`, version: `0.1.0`
   - Python: `>=3.8`
   - Core deps: `typer[all]>=0.9.0`, `jinja2>=3.0`, `httpx>=0.25`, `beautifulsoup4>=4.12`, `cssutils>=2.10`, `watchdog>=3.0` (for serve)
   - Dev deps: `pytest>=7.0`, `pytest-cov>=4.0`, `mypy>=1.0`, `ruff>=0.1.0`, `pyinstaller>=6.0` (for distributions)
   - Extract extras: add `cssutils`, `httpx` to optional group
   - Entry point: `aurea = aurea.cli:app`

2. **src/aurea/__init__.py** — Package init with `__version__ = "0.1.0"`

3. **.github/workflows/1-lint-test.yml** — PR workflow (sequential: lint → type check → tests)
   - Run `ruff check .` and `ruff format --check .`
   - Run `mypy src/`
   - Run `pytest tests/ --cov=src --cov-fail-under=80`
   - Do NOT run on-push to main (only on PR)

4. **src/aurea/cli.py** — Typer entry point with 6 commands: `init`, `build`, `serve`, `theme`, `extract`, `--version`

5. **tests/fixtures/** — Sample slides, themes, expected HTML (use for integration tests)

**Key rule**: Do not merge Phase 1 until **all 6 CLI commands exist** (even if stubs), tests run, and workflows are green.

## Development Workflow

### Setup

```bash
# Clone and enter directory
cd /path/to/aurea

# Create Python venv (3.8+)
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  (Windows)

# Install with dev dependencies
pip install -e ".[dev,extract]"

# Verify
aurea --version
aurea --help
```

### Common Commands

```bash
# Lint (ruff check & format)
ruff check .
ruff format .

# Type checking
mypy src/

# Run tests
pytest                          # All tests
pytest tests/unit/              # Unit tests only
pytest tests/unit/test_cli.py   # Single file
pytest -k "test_init"           # Single test
pytest --cov=src                # With coverage

# Build distributions
python -m PyInstaller ./build/aurea.spec  # Standalone .exe/.bin
python -c "import shutil; shutil.make_archive('aurea', 'zip', 'dist')"  # Zipapp

# Serve (development)
aurea serve --watch             # Auto-rebuild on file changes
```

### Testing Conventions

- **Unit tests** (`tests/unit/`): Test individual functions (`parse_slide()`, `resolve_theme()`, etc.). Mock external I/O (httpx, filesystem). Use pytest with fixtures.
  - `test_cli.py` — Typer command parsing, argument validation, help text
  - `test_build.py` — Markdown parsing, Jinja2 rendering, CSS inlining
  - `test_theme.py` — Theme loading, registry lookup, theme switching
  - `test_extract.py` — HTML parsing, CSS extraction, DESIGN.md generation

- **Integration tests** (`tests/integration/`): End-to-end workflows. Use **real temp directories** and files (no mocks).
  - `test_init.py` — `aurea init myproject` creates correct structure
  - `test_build_end_to_end.py` — Markdown in → valid reveal.js HTML out
  - `test_serve.py` — Server starts, responds to requests, file changes trigger rebuild
  - `test_extract_end_to_end.py` — URL in → DESIGN.md + theme.css out

- **Fixtures** (`tests/fixtures/`): Store reusable test data
  - `sample_slides.md` — Example presentation Markdown
  - `default_theme/` — Minimal but complete theme for testing
  - `expected_output.html` — Known-good reveal.js output (for regression tests)

- **Coverage goal**: 80%+ for `src/aurea/` (unit + integration combined). CLI arg handling may be lower.

**Important**: Integration tests should **not** mock the build pipeline. They verify the entire workflow works, catching real integration bugs.

## Build Pipeline Architecture

Understanding how Aurea works internally is key to implementing each phase:

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: Markdown slides (slides.md)                           │
│        + theme choice (via CLI or config)                    │
│        + optional reveal.js settings (JSON)                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
                  [build.py pipeline]
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. PARSE (Markdown → internal representation)                │
│    - Split by `---` (slide separators)                       │
│    - Extract metadata (title, author, etc. from YAML front)  │
│    - Validate slide structure                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RESOLVE THEME (registry.json + theme dir)                 │
│    - Load DESIGN.md from theme/                              │
│    - Merge with global theme settings                        │
│    - Validate theme CSS is valid                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. RENDER (Jinja2 template → HTML per slide)                 │
│    - Load reveal.html template                               │
│    - For each slide: render Markdown → HTML (markdown lib)   │
│    - Apply theme CSS variables (via Jinja2 context)          │
│    - Insert syntax highlighting (via Pygments)               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. INLINE (CSS → HTML, remove external refs)                 │
│    - Load theme.css + layout.css + reveal.js CSS             │
│    - Inline into <style> tags                                │
│    - Vendor reveal.js JS into <script> tags                  │
│    - Strip any <link> or <script src="...">                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Single .html file (~2-5 MB)                          │
│         Ready to send via email, upload, or open locally     │
└─────────────────────────────────────────────────────────────┘
```

**Key modules**:
- `_tpl.py` — Jinja2 environment setup, custom filters/globals
- `theme.py` — Theme registry lookup, DESIGN.md parsing, CSS validation
- `build.py` — Orchestrates parse → resolve → render → inline pipeline
- `_regex.py` — Markdown parsing utilities (not a full MD parser; use external lib)

**Why inlining matters**: The output must work offline and in email clients. No external resources = guaranteed compatibility.

## Key Implementation Phases

**Phase 0** (done): Repository setup, spec written.

**Phase 1**: Prompt templates (7 commands for each agent type) + CLI scaffolding.
- `aurea init` creates project structure with templates.
- Agents (Claude, Gemini, Copilot, etc.) have formatted command files.

**Phase 2**: Theme system (import 40+ designs, build registry, CLI).
- `aurea theme list/search/use` work locally.
- `registry.json` indexes all themes.
- GitHub Actions syncs from `awesome-design-md`.

**Phase 3**: Build pipeline (Markdown → HTML with Jinja2).
- `aurea build` produces standalone HTML with inlined CSS/JS.
- Reveal.js vendored in dist.
- `aurea serve` with hot reload.

**Phase 4**: Theme extraction (web scraping → DESIGN.md + CSS).
- `aurea extract https://example.com --name mydesign`.
- Automatic DESIGN.md generation from parsed CSS.

**Phase 5**: Distribution (PyInstaller .exe, zipapp, PyPI, code signing).
- GitHub Actions builds all four modes.
- Release artifacts: `.pyz`, `.exe`, `.dmg`, `.tar.gz`, wheels.

## Critical Architectural Decisions

These are non-negotiable constraints from the spec. Decisions here were deliberate:

- **Python 3.8+ only** — Must support Windows 7/10 machines without Microsoft Store. No f-strings with `:=` (walrus), no `@` merge operator. Test on Python 3.8.
  
- **Minimal dependencies** — Keep install size <50MB. Prefer stdlib + Jinja2/Typer/httpx. No Django, numpy, heavy ML libs. This enables zipapp + PyInstaller.

- **Output is 100% standalone HTML** — All CSS/JS inlined into single `.html` file. No CDN, no external requests after generation. Offline-first.
  
- **reveal.js 5.x only** — Do **not** upgrade to 6.x (breaking changes). Pin to `5.0.0+<6.0`. Vendored in dist (not via npm).

- **DESIGN.md is dual-purpose** — Each theme's `DESIGN.md` is both human-readable design system AND parsed by extraction logic. Changes to format must be coordinated.

- **Agent commands are versioned** — Stored in `src/aurea/agent_commands/` and embedded in distributions. They are **not** live-fetched; consistency matters.

- **Distributable is the source of truth** — The zipapp/exe is what end-users see. If something works in dev but not in distribution, the distribution is broken. Test all four modes: CLI, zipapp, PyInstaller, pip.

## Design Principles

- **Portability first**: Minimize external dependencies, support Windows without Python.
- **Templates as product**: Prompts are the real value; CLI is convenience.
- **Autosufficient output**: HTML runs offline, in any browser, no server.
- **Progressive**: Work from "copy-paste templates" to "full CLI + themes + live preview."

## Common Pitfalls & Gotchas

**Python 3.8 compatibility:**
- ❌ Don't use walrus operator `:=`, `|` for unions in type hints, match/case, positional-only params (`/`)
- ✅ Do use `from __future__ import annotations` and `Union[A, B]` for typing

**Offline output is non-negotiable:**
- ❌ Don't add `<link href="https://...">` or `<script src="https://...">`
- ✅ Do vendor CSS/JS into `<style>`/`<script>` tags or base64 data URIs

**Theme system consistency:**
- ❌ Don't change DESIGN.md format without updating extract.py
- ✅ Do document format changes in `docs/theme-system.md` first, then coordinate

**Distribution testing:**
- ❌ Don't assume "works locally" means "works in zipapp/exe"
- ✅ Do test all four modes before releasing
- ❌ Don't use relative imports in CLI entry point (breaks PyInstaller bundling)
- ✅ Do use absolute imports (`from aurea.cli import ...`)

**Agent commands are frozen:**
- ❌ Don't assume you can update agent templates live
- ✅ Do remember they're vendored; users get them from downloaded releases

## Git & PR Workflow

- Create feature branches from `main` for all changes.
- Commit messages should be clear and descriptive (e.g., "Add theme extraction CLI", "Fix Markdown parsing edge case").
- Open a PR for review before merging to `main`.
- Follow existing code style: run `ruff check .` and `mypy src/` before pushing.
- Keep commits atomic—one feature or one bug fix per commit.
- **No AI attribution in commits** — Aurea is 100% your work.

## Specification Reference

The **`aurea-spec.md`** file (32 KB) contains:
- Full product vision, use cases, and design philosophy
- Detailed breakdown of four distribution modes (zero-install, zipapp, PyInstaller, pip)
- Theme system architecture and registry format
- Workflow phases (outline → generate → refine → visual → build)
- Agent command templates structure (why each phase exists, what agents should do)
- Build pipeline technical details (Markdown parsing, Jinja2 rendering, CSS inlining)
- Web scraping strategy for theme extraction
- Accessibility and testing requirements

**When stuck on requirements**, refer to the spec—it's the source of truth. Decisions made in the spec take precedence over intuition.

## Important Notes

- **No AI attribution in docs/commits**: Aurea is your work. If updating README/docstrings, do not mention Claude, AI, or code generation.
- **Config over complexity**: Use Typer for CLI args, YAML for configs. Avoid hand-rolled parsing or custom config formats.
- **Logging to stderr**: CLI output goes to stdout (for piping), logging to stderr (for user visibility). Use a logging config (not print()).
- **Distribution testing is non-optional**: Before releasing, test on:
  - Windows (PowerShell, cmd)
  - macOS (Intel + Apple Silicon)
  - Linux (at least one distro)
  - All four modes: CLI (pip), zipapp, PyInstaller exe, zero-install templates
  - Python 3.8 (oldest supported) + 3.12+ (latest)

## Active Technologies
- Python 3.8+ (target; tested on 3.8 and 3.12+) + `typer[all]>=0.9.0,<0.21`, `jinja2>=3.0`, `mistune>=2.0.5,<3.1`, `rich>=13.0`, `watchdog>=3.0`, `pyyaml>=6.0`; extract extras: `httpx>=0.25`, `beautifulsoup4>=4.12`, `cssutils>=2.10`, `lxml>=4.9` (001-aurea-cli-toolkit)
- Filesystem only — JSON files, Markdown, CSS, HTML (001-aurea-cli-toolkit)

## Recent Changes
- 001-aurea-cli-toolkit: Added Python 3.8+ (target; tested on 3.8 and 3.12+) + `typer[all]>=0.9.0,<0.21`, `jinja2>=3.0`, `mistune>=2.0.5,<3.1`, `rich>=13.0`, `watchdog>=3.0`, `pyyaml>=6.0`; extract extras: `httpx>=0.25`, `beautifulsoup4>=4.12`, `cssutils>=2.10`, `lxml>=4.9`
