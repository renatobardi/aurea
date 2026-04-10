# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aurea** is a toolkit for generating high-quality HTML presentations via AI agents (Claude Code, Gemini CLI, ChatGPT, Devin, Windsurf, etc.). It emphasizes **portability** and **minimal friction** across different environments—Windows corporate machines, macOS, Linux—without requiring complex toolchains.

The project centers on:
- **CLI** (Python): scaffolding, building, serving, theme management
- **Prompt templates**: structured guides for AI agents through presentation creation phases
- **Design system**: 64 themes based on real-world design systems (Apple, Stripe, Linear, etc.)
- **Standalone HTML output**: reveal.js-based, offline-capable, no external dependencies

See `aurea-spec.md` for the complete specification and design decisions.

## Development Workflow

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -e ".[dev,extract]"
```

### Common Commands

```bash
# Lint & format
ruff check .
ruff format .

# Type checking
mypy src/

# Tests
pytest                                        # all
pytest tests/unit/ -v                         # unit only
pytest tests/integration/ --tb=long           # integration only
pytest -k "test_init"                         # single test by name
pytest --cov=src/aurea --cov-report=html      # with coverage

# Build distributions
python -m PyInstaller ./build/aurea.spec      # standalone exe/bin
```

## Build Pipeline Architecture

`build.py` orchestrates a strict sequential pipeline:

```
INPUT (slides.md + theme)
  → 1. PARSE    — split on `---`, extract YAML frontmatter, validate structure
  → 2. RESOLVE  — load DESIGN.md from theme dir, merge settings, validate CSS
  → 3. RENDER   — Jinja2 (reveal.html.j2) → per-slide HTML, apply theme vars
  → 4. INLINE   — embed theme.css + layout.css + vendor JS into <style>/<script>
OUTPUT: single self-contained .html (~2–5 MB)
```

**Key modules:**
- `src/aurea/commands/build.py` — pipeline orchestrator
- `src/aurea/_tpl.py` — Jinja2 env, custom filters, context passing from build.py
- `src/aurea/commands/theme.py` — registry lookup, DESIGN.md parsing, CSS validation
- `src/aurea/commands/extract.py` — web scraping (httpx + BeautifulSoup) → DESIGN.md
- `src/aurea/commands/serve.py` — HTTP server with watchdog hot reload
- `src/aurea/_log.py` — logging to stderr; stdout is reserved for piping

**Theme registries (two levels):**
- Global: `src/aurea/themes/registry.json` — 64 themes, full metadata
- Per-project: `.aurea/themes/registry.json` — minimal, only the selected theme (derived from `meta.json`); do not copy the full global registry here

## Critical Architectural Decisions

These constraints are non-negotiable and were deliberate:

- **Python 3.8+** — Must support Windows 7/10 without Microsoft Store. No walrus `:=`, no `|` union type hints, no match/case. Use `Union[A, B]` and `from __future__ import annotations`.

- **Minimal dependencies, <50 MB total** — enables zipapp + PyInstaller. No Django, numpy, or heavy libs. Core: Typer, Jinja2, mistune, watchdog, PyYAML, Pygments. Optional `[extract]`: httpx, beautifulsoup4, cssutils, lxml.

- **Output is 100% standalone HTML** — all CSS/JS inlined. No CDN, no external requests. Offline-first is non-negotiable.

- **reveal.js 5.x only** — pinned to `5.0.0+,<6.0`. Do NOT upgrade to 6.x (breaking API changes). Vendored in `src/aurea/vendor/revealjs/dist/` — not via npm.

- **DESIGN.md is dual-purpose** — each theme's `DESIGN.md` is both human-readable doc AND parsed by `extract.py`. Format changes must be coordinated with extraction logic and documented in `docs/theme-system.md`.

- **Agent commands are frozen at release** — stored in `src/aurea/agent_commands/`, vendored into distributions. Not live-fetched.

- **Four distribution modes, all fully functional** — zero-install (copy/paste), zipapp (.pyz), PyInstaller (.exe/bin), pip. No mode is limited.

## Testing Conventions

**Unit tests** (`tests/unit/`): test individual functions in isolation; mock external I/O (httpx, filesystem).

**Integration tests** (`tests/integration/`): use real temp directories and files. Must NOT use `unittest.mock` for the core pipeline (init, build, serve, extract). Tests the full chain: CLI → command → file output.

**Fixtures** (`tests/fixtures/`): `sample_slides.md`, `default_theme/`, `expected_output.html` for regression testing.

## Common Pitfalls & Gotchas

**Python 3.8 compatibility:**
- ❌ walrus `:=`, `|` for type unions, match/case, positional-only params
- ✅ `Union[A, B]`, `from __future__ import annotations`
- ❌ `from __future__ import annotations` in `cli.py` — combining it with `typing_extensions.Annotated` causes `TypeError` on Python 3.8 (known CPython bug). Use explicit `Optional[...]` there only.

**Offline output:**
- ❌ `<link href="https://...">` or `<script src="https://...">`
- ✅ Vendor everything into `<style>`/`<script>` or base64 data URIs

**reveal.js plugins are ES modules — cannot be inlined:**
- ❌ Inline `.mjs` plugin files — they use bare `import` which fails outside ES module context
- ✅ Use `vendor/highlight.min.js` + `vendor/marked.min.js` (UMD builds) with IIFE shims in `inline_assets()` in `build.py`
- ❌ Upgrade UMD vendor files without checking for bare `import`/`export` statements

**`</script>` inside inlined JS:**
- ❌ Any JS containing `</script>` (even in a string literal) prematurely closes the `<script>` block
- ✅ `_read()` in `build.py` escapes `</script>` → `<\/script>` — maintain this for any new vendor files

**Logging level:**
- ❌ `_log.py` was once accidentally set to `WARNING`, silencing all `_log.info()` calls
- ✅ Always set `level=logging.INFO` in both `basicConfig` and `_log.setLevel()`

**Local registry:**
- ❌ Copying the entire global `registry.json` to the project — bakes in stale metadata
- ✅ Create a minimal local registry with only the selected theme, derived from its `meta.json`

**DESIGN.md / extract.py coupling:**
- ❌ Changing DESIGN.md format without updating `extract.py`
- ✅ Document format changes in `docs/theme-system.md` first, then coordinate

**Distribution assumptions:**
- ❌ "Works locally" ≠ "works in zipapp/exe"
- ❌ Relative imports in CLI entry point — breaks PyInstaller
- ✅ Absolute imports everywhere (`from aurea.cli import ...`)
- ✅ Test all four modes before releasing

## Common Development Tasks

**Adding a new theme:**
1. Create `src/aurea/themes/{id}/` with DESIGN.md (9 sections), theme.css, layout.css, meta.json
2. Add entry to `src/aurea/themes/registry.json`
3. Test: `aurea theme list`, `aurea theme info {id}`, `aurea init test --theme {id}`, full build

The 9 required DESIGN.md sections (case-insensitive keyword match in `build.py`):
`visual theme`, `color palette`, `typography`, `components`, `layout`, `depth`, `do's`, `responsive`, `agent prompt`

**Modifying the build pipeline:**
- Keep the 4-step order (parse → resolve → render → inline)
- Include both unit tests (mock filesystem) and integration tests (real temp dirs)
- Verify output has no external links (offline-capable)

**Adding extraction features:**
- `extract.py` is fragile — web scraping breaks when sites change
- Unit test with `httpx_mock` (from pytest-httpx); integration test with real URLs
- `httpx` and `beautifulsoup4` are lazy-imported inside `extract.py` and `_http.py` — do not import them at module top-level (keeps core install lightweight; only available with `pip install aurea[extract]`)

## CI/CD Pipelines

Three workflows in `.github/workflows/`, run sequentially:

1. **`1-lint-test.yml`** — triggers on PR and push to `main`. Runs: ruff → mypy → pytest (matrix: Python 3.8 + 3.12). Coverage gate: 80% (`--cov-fail-under=80`). Must pass before merging.

2. **`2-build-dist.yml`** — triggers after workflow 1 succeeds on `main`, or on release published. Builds: zipapp (shiv), executables (PyInstaller on ubuntu/windows/macos), then publishes wheel to PyPI. PyPI publish requires the `pypi` environment and OIDC trusted publishing.

3. **`3-sync-themes.yml`** — scheduled weekly (Monday 03:00 UTC). Clones `VoltAgent/awesome-design-md`, generates theme entries, opens a PR with updates to `src/aurea/themes/`.
