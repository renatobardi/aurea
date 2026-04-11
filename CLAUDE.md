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
│   ├── cli.py              # Typer entry point (command routing)
│   ├── commands/           # Command implementations (init, build, serve, theme, extract)
│   │   ├── init.py         # Scaffolding logic
│   │   ├── build.py        # Markdown → HTML pipeline
│   │   ├── serve.py        # Live reload server (watchdog for hot reload)
│   │   ├── theme.py        # Theme listing, searching, applying
│   │   ├── extract.py      # Web scraping & design extraction
│   │   └── __init__.py
│   ├── _tpl.py             # Jinja2 template management
│   ├── _regex.py           # Regex utilities for parsing
│   ├── _http.py            # HTTP utilities (httpx wrapper)
│   ├── _log.py             # Logging config (structured logging to stderr)
│   ├── exceptions.py        # Custom exception types
│   └── __init__.py
├── src/aurea/agent_commands/
│   ├── claude/              # 7 commands, .md format
│   ├── gemini/              # 7 commands, .toml format
│   ├── copilot/             # 7 commands, .agent.md format
│   ├── windsurf/            # 7 commands, .md format
│   ├── devin/               # 7 commands, .md format
│   ├── chatgpt/             # 7 commands, .md format
│   ├── cursor/              # 7 commands, .md format
│   └── generic/             # 7 commands, .md format
├── src/aurea/themes/
│   ├── registry.json        # Master index of all themes with metadata
│   ├── default/
│   │   ├── DESIGN.md        # Design system spec, parsed by extract.py
│   │   ├── theme.css        # reveal.js theme CSS
│   │   ├── layout.css       # Grid, animations, responsive overrides
│   │   └── meta.json        # Search metadata
│   └── ... (40+ themes from awesome-design-md, synced nightly)
├── src/aurea/templates/
│   ├── reveal.html.j2       # Jinja2 template — reveal.js presentation
│   └── slide_readme.md.j2   # README template for new projects
├── src/aurea/vendor/
│   ├── revealjs/dist/       # reveal.js 5.2.1 core (UMD)
│   ├── highlight.min.js     # highlight.js 11.9.0 (UMD)
│   └── marked.min.js        # marked 9.1.6 (UMD)
├── tests/
│   ├── unit/                # Isolated function tests (mock external I/O)
│   ├── integration/         # End-to-end workflows (real filesystem)
│   └── fixtures/            # Sample data for tests
├── docs/
│   ├── architecture.md      # Build pipeline internals & data flow
│   ├── theme-system.md      # DESIGN.md format, registry structure
│   └── agent-commands.md    # Workflow phases, command descriptions
├── build/
│   └── aurea.spec           # PyInstaller spec for standalone binaries
├── pyproject.toml           # Python metadata, dependencies, entry points
├── ruff.toml                # Linting & formatting config
├── .github/workflows/
│   ├── 1-lint-test.yml      # PR checks: ruff, mypy, pytest
│   ├── 2-build-dist.yml     # Release builds: PyInstaller, zipapp, PyPI
│   └── 3-sync-themes.yml    # Nightly theme sync from awesome-design-md
└── aurea-spec.md            # Full specification & design decisions
```

**Current Status**: M0–M3 fully implemented. Production-ready v0.1.0.

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
# Lint (ruff check & format) — line-length 100, targets Python 3.8
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

**Unit tests** (`tests/unit/`): Test individual functions in isolation. Mock external I/O (httpx, filesystem). Use pytest with fixtures.
- Should import from `aurea.commands.*` and utility modules
- Example: `test_build.py` tests `build.parse_markdown()`, `resolve_theme()`, `inline_assets()` separately
- Fixtures go in `conftest.py` — reuse across test files
- Coverage goal: 80%+ for `src/aurea/`

**Integration tests** (`tests/integration/`): Verify end-to-end workflows work. Use **real temp directories** and files (no mocks of the build pipeline).
- Example: `test_init_then_build.py` runs `aurea init myproject && aurea build`, checks output is valid HTML
- Tests the entire chain: CLI parsing → command execution → file generation
- Must not use `unittest.mock` for the core pipeline (init, build, serve, extract)

**Fixtures** (`tests/fixtures/`): Shared test data
- `sample_slides.md` — Example presentation with YAML frontmatter
- `default_theme/` — Complete theme (DESIGN.md, CSS, meta.json)
- `expected_output.html` — Known-good reveal.js output for regression testing

**Running tests:**
```bash
pytest                              # All tests
pytest tests/unit/ -v               # Unit tests with verbose output
pytest tests/integration/ --tb=long # Integration tests with full tracebacks
pytest -k "build and not serve"     # Run tests matching pattern
pytest --cov=src/aurea --cov-report=html  # Coverage with HTML report
```

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

## Implementation Status

- **Phase 0**: ✅ Repository setup, spec written
- **Phase 1**: ✅ Prompt templates (7 commands × 8 agents) + CLI scaffolding (init, build, serve, theme, extract)
- **Phase 2**: ✅ Theme system (64 themes, registry, CLI search/list/use/info/show/create)
- **Phase 3**: ✅ Build pipeline (Markdown → standalone HTML with inlined CSS/JS, hot reload server)
- **Phase 4**: ✅ Theme extraction (web scraping with BeautifulSoup, CSS parsing, DESIGN.md generation)
- **Phase 5**: ⚠️ Distribution (PyInstaller .exe, zipapp, PyPI publish ready; code signing/Intune/SCCM pending)

## Critical Architectural Decisions

These are non-negotiable constraints from the spec. Decisions here were deliberate:

- **Python 3.8+ only** — Must support Windows 7/10 machines without Microsoft Store. No f-strings with `:=` (walrus), no `@` merge operator. Test on Python 3.8.
  
- **Minimal dependencies** — Keep install size <50MB. Prefer stdlib + Jinja2/Typer/httpx. No Django, numpy, heavy ML libs. This enables zipapp + PyInstaller.

- **Output is 100% standalone HTML** — All CSS/JS inlined into single `.html` file. No CDN, no external requests after generation. Offline-first.
  
- **reveal.js 5.x only** — Do **not** upgrade to 6.x (breaking changes). Pin to `5.0.0+<6.0`. Vendored in dist (not via npm).

- **DESIGN.md is dual-purpose** — Each theme's `DESIGN.md` is both human-readable design system AND parsed by extraction logic. Changes to format must be coordinated.

- **Agent commands are versioned** — Stored in `src/aurea/agent_commands/` and embedded in distributions. They are **not** live-fetched; consistency matters.

- **Distributable is the source of truth** — The zipapp/exe is what end-users see. If something works in dev but not in distribution, the distribution is broken. Test all four modes: CLI, zipapp, PyInstaller, pip.

## Key Entry Points & Code Paths

**CLI Entry**:
- `src/aurea/cli.py` — Typer app with command routing (init, build, serve, theme, extract)
- Each command is a separate function; subcommands route to `theme_app` typer group
- Note: `cli.py` uses absolute imports and avoids `from __future__ import annotations` (Python 3.8 typing compatibility)

**Command Implementations**:
- `src/aurea/commands/init.py` — Creates project scaffolding; calls `_tpl.py` for Jinja2 rendering
- `src/aurea/commands/build.py` — Main pipeline: parse → resolve theme → render → inline
- `src/aurea/commands/serve.py` — HTTP server with watchdog file observer for hot reload
- `src/aurea/commands/theme.py` — Theme registry, metadata search, CSS validation
- `src/aurea/commands/extract.py` — Web scraping with httpx/BeautifulSoup; generates DESIGN.md

**Template Rendering**:
- `src/aurea/_tpl.py` — Jinja2 environment setup; loads reveal.html.j2 and slide_readme.md.j2
- Custom filters for theme variables, colors, typography
- Handles context passing from build.py → Jinja2

**Theme System**:
- Global registry: `src/aurea/themes/registry.json` (64 themes, metadata)
- Per-project registry: `.aurea/themes/registry.json` (minimal, only selected theme)
- Theme structure: `DESIGN.md` (dual-purpose: human doc + parsed by extract.py) + CSS + meta.json

**Logging**:
- `src/aurea/_log.py` — Configured for logging.INFO level, structured output to stderr
- All CLI output goes to stdout (for piping); diagnostics to stderr

## Design Principles

- **Portability first**: Minimize external dependencies, support Windows without Python.
- **Templates as product**: Prompts are the real value; CLI is convenience.
- **Autosufficient output**: HTML runs offline, in any browser, no server.
- **Progressive**: Work from "copy-paste templates" to "full CLI + themes + live preview."

## Common Development Tasks

**Adding a new theme**:
1. Create `src/aurea/themes/{theme-id}/` with DESIGN.md (9 sections), theme.css, layout.css, meta.json
2. Add entry to `src/aurea/themes/registry.json` with name, description, tags, colors
3. Test with `aurea theme list`, `aurea theme info {theme-id}`, `aurea init test --theme {theme-id}`
4. Run full build test to ensure CSS inlines correctly

**Modifying the build pipeline**:
- Changes to `src/aurea/commands/build.py` should include both unit tests (mock filesystem) and integration tests (real temp dirs)
- The 4-step pipeline (parse → resolve → render → inline) is sequential; maintain this order
- Always test output is valid HTML and offline-capable (no external links)

**Adding extraction features**:
- Extend `src/aurea/commands/extract.py` carefully — web scraping is fragile
- Add unit tests with mock HTTP responses (use `httpx_mock` from pytest-httpx)
- Test with real URLs in integration tests (may fail if site changes)

**Updating themes from awesome-design-md**:
- Workflow runs nightly via `3-sync-themes.yml`
- Manual sync tool: `scripts/import-awesome-designs.py` — clones/updates `.awesome-design-md/` and imports themes
  - `python scripts/import-awesome-designs.py` — full sync from upstream
  - `python scripts/import-awesome-designs.py --from-local` — rebuild `registry.json` from existing theme `meta.json` files without re-downloading
- Validate all 64 themes still build after changes

**Updating reveal.js**:
- ⚠️ **Must stay on 5.x** — Do NOT upgrade to 6.x (breaking API changes)
- Vendor files in `src/aurea/vendor/revealjs/dist/`
- If updating highlight.js or marked.js, check for ES module syntax (bare `import`/`export` — if present, won't inline)
- Test full build with syntax highlighting and code blocks

## Common Pitfalls & Gotchas

**Python 3.8 compatibility:**
- ❌ Don't use walrus operator `:=`, `|` for unions in type hints, match/case, positional-only params (`/`)
- ✅ Do use `from __future__ import annotations` and `Union[A, B]` for typing

**Offline output is non-negotiable:**
- ❌ Don't add `<link href="https://...">` or `<script src="https://...">`
- ✅ Do vendor CSS/JS into `<style>`/`<script>` tags or base64 data URIs

**reveal.js 5.x plugins are pure ES modules — cannot be inlined:**
- ❌ Don't try to inline `.mjs` plugin files in `<script>` tags — they use `import { marked } from 'marked'` which fails outside ES module context
- ✅ Use `vendor/highlight.min.js` + `vendor/marked.min.js` (UMD builds) and the IIFE shims in `inline_assets()` in `build.py`
- ❌ Don't upgrade the UMD vendor files without checking for bare `import`/`export` statements

**`</script>` literals inside inlined JS:**
- ❌ Any JS file containing the string `</script>` (even in a string literal) will prematurely close the `<script>` block in HTML
- ✅ `_read()` in `build.py` escapes all `</script>` → `<\/script>` before inlining — maintain this for any new vendor files

**Logging level:**
- ❌ `_log.py` was accidentally set to `WARNING` — silences all `_log.info()` calls
- ✅ Always set `level=logging.INFO` in both `basicConfig` and `_log.setLevel()`

**Local registry in `aurea init`:**
- ❌ Don't copy the entire global `registry.json` (64 themes) to the local project — it bakes in stale metadata
- ✅ Create a minimal local registry containing only the selected theme, derived from the theme's `meta.json`

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

## Dependency Map

**Core (always installed)**:
- `typer[all]>=0.9.0,<0.21` — CLI framework + rich (output formatting)
- `jinja2>=3.0` — Template rendering
- `mistune>=2.0.5,<3.1` — Markdown parsing
- `watchdog>=3.0` — File change monitoring (for hot reload)
- `pyyaml>=6.0` — YAML parsing (frontmatter in slides)
- `pygments>=2.10` — Syntax highlighting for code blocks

**Optional [extract]** (for `aurea extract` command):
- `httpx>=0.25` — Async HTTP client
- `beautifulsoup4>=4.12` — HTML parsing
- `cssutils>=2.10` — CSS parsing
- `lxml>=4.9` — XML parsing (bs4 backend)

**Dev [dev]** (testing, linting, building):
- `pytest>=7.0` — Unit & integration tests
- `pytest-cov>=4.0` — Coverage reporting
- `mypy>=1.0` — Type checking
- `ruff>=0.1.0` — Linting & formatting
- `pyinstaller>=6.0` — Standalone binary builds
- `shiv>=1.0.0` — Zipapp building

**Constraint**: Total install size must be <50 MB (enables zipapp distribution).

## Module Dependencies

```
cli.py (entry point)
├── commands/init.py (scaffolding)
│   └── _tpl.py (Jinja2)
├── commands/build.py (main pipeline)
│   ├── _tpl.py (rendering)
│   ├── commands/theme.py (resolution)
│   ├── _regex.py (parsing)
│   └── exceptions.py
├── commands/serve.py (server)
│   └── watchdog (file observer)
├── commands/theme.py (listing, search)
│   └── exceptions.py
├── commands/extract.py (web scraping)
│   ├── _http.py (httpx wrapper)
│   └── exceptions.py
└── _log.py (logging)
```

## Recent Changes
- v0.1.0 (2026-04-09): Full M0–M3 implementation, production-ready
  - CLI: init, build, serve, theme, extract fully working
  - Themes: 64 total (5 original + 59 from awesome-design-md)
  - Build: Markdown → standalone HTML with inlined CSS/JS
  - Extract: Web scraping → DESIGN.md generation
  - Tests: Unit + integration, 80%+ coverage
  - Distribution: pip, zipapp, PyInstaller (exe/bin/dmg)
