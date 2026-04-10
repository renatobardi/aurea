# Implementation Plan: Aurea CLI and Presentation Toolkit

**Branch**: `001-aurea-cli-toolkit` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/001-aurea-cli-toolkit/spec.md`

---

## Summary

Aurea is a Python 3.8+ CLI toolkit (Typer) for generating standalone HTML presentations via AI agents. The implementation covers three user stories in priority order:

- **P1 (M1)**: `aurea init` with project scaffolding + 7×8 prompt templates (7 commands × 8 agent formats)
- **P2 (M2–M3)**: Theme system (40+ themes, registry, CLI theme commands) + build pipeline (Markdown → reveal.js HTML, watchdog, serve)
- **P3 (M4)**: Theme extraction via web scraping (`aurea extract`, `DesignExtractor` class)

All features must work across four distribution modes: zero-install templates, zipapp `.pyz`, PyInstaller `.exe`, and pip. Output HTML is 100% standalone (no CDN references). Stack: Typer + Jinja2 + mistune + reveal.js 5.x (vendored) + httpx + BeautifulSoup4 + cssutils + watchdog + pytest + ruff + mypy.

---

## Technical Context

**Language/Version**: Python 3.8+ (target; tested on 3.8 and 3.12+)  
**Primary Dependencies**: `typer[all]>=0.9.0,<0.21`, `jinja2>=3.0`, `mistune>=2.0.5,<3.1`, `rich>=13.0`, `watchdog>=3.0`, `pyyaml>=6.0`; extract extras: `httpx>=0.25`, `beautifulsoup4>=4.12`, `cssutils>=2.10`, `lxml>=4.9`  
**Storage**: Filesystem only — JSON files, Markdown, CSS, HTML  
**Testing**: pytest + pytest-cov; integration tests use real temp directories (no pipeline mocks)  
**Target Platform**: Windows 10/11 (primary), macOS, Linux; four distribution modes  
**Project Type**: CLI tool + Python library + template collection  
**Performance Goals**: `aurea init` < 2s; `aurea build` < 5s for typical 20-slide deck; `aurea theme search` < 500ms; `aurea extract` < 30s at depth 1  
**Constraints**: Install size <50MB; output HTML 200KB–500KB (without embed-fonts); Python 3.8 compatible (no walrus, no pipe unions, no match/case)  
**Scale/Scope**: 40+ themes in registry; 7 commands × 8 agent formats = 56 template files; single-user CLI (no concurrency concerns)

---

## Constitution Check

*GATE: Pre-design check. All items MUST pass before implementation begins.*

- [x] **Art. I — Python 3.8+**: No walrus (`:=`), no pipe unions (`X | Y`), no match/case. Use `from typing_extensions import Annotated` (not `typing.Annotated`). Use `typing.List`, `typing.Dict`, `typing.Optional`, `typing.Union`. No `from __future__ import annotations` combined with `Annotated` (known 3.8 bug).
- [x] **Art. II — Four modes**: `aurea init` tested in all four modes (zero-install, zipapp, PyInstaller, pip). `aurea build` same. Template copy (Mode 1) documented in quickstart.
- [x] **Art. III — Offline output**: Build pipeline inlines reveal.js JS, CSS, and fonts into `<style>`/`<script>` tags. Post-render regex strips any stray `<link href="https://...">` or `<script src="https://...">`. Zero CDN references in final HTML.
- [x] **Art. IV — Templates first**: All 7 prompt templates work standalone (Mode 1) without CLI. `/aurea.build` template generates inline HTML. `/aurea.extract` template uses agent's native web fetch as fallback.
- [x] **Art. V — DESIGN.md sync**: 9-section DESIGN.md format defined in `data-model.md`; any format change must update `extract.py` parser AND `docs/theme-system.md` in the same PR.
- [x] **Art. VI — Commands frozen**: Agent command templates live in `src/aurea/agent_commands/` and are embedded in zipapp/exe/pip distributions. No live-fetch at runtime.
- [x] **Art. VII — Deps controlled**: Core install: typer + jinja2 + mistune + rich + watchdog + pyyaml ≈ ~15MB. Extract extras add ~10MB (httpx + bs4 + cssutils + lxml). Well under 50MB. No Django, numpy, ML libs.
- [x] **Art. VIII — reveal.js pinned**: `reveal.js >=5.0.0, <6.0` vendored in `src/aurea/vendor/revealjs/`. Not via npm, not via CDN. Pinned in `pyproject.toml` metadata comments.
- [x] **Art. IX — Tests**: Test-first. Unit tests mock I/O. Integration tests use `tmp_path` (real filesystem, no mocks). Coverage ≥ 80% enforced in CI via `--cov-fail-under=80`.

**No violations. No complexity tracking required.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-aurea-cli-toolkit/
├── plan.md              ← This file
├── research.md          ← Technology decisions (Phase 0)
├── data-model.md        ← Entity definitions (Phase 1)
├── quickstart.md        ← End-to-end validation guide (Phase 1)
├── contracts/
│   └── cli-commands.md  ← CLI command schemas (Phase 1)
└── tasks.md             ← NOT created yet (/speckit.tasks)
```

### Source Code (repository root)

```text
src/aurea/
├── __init__.py                  ← __version__ = "0.1.0"
├── cli.py                       ← Typer app entry point + --version
├── commands/
│   ├── __init__.py
│   ├── init.py                  ← aurea init
│   ├── build.py                 ← aurea build
│   ├── serve.py                 ← aurea serve (watchdog HTTP server)
│   ├── theme.py                 ← aurea theme (sub-group: list/search/use/info/show/create)
│   └── extract.py               ← aurea extract (DesignExtractor class)
├── agent_commands/              ← Canonical template sources (vendored in distributions)
│   ├── claude/
│   │   ├── aurea.theme.md
│   │   ├── aurea.outline.md
│   │   ├── aurea.generate.md
│   │   ├── aurea.refine.md
│   │   ├── aurea.visual.md
│   │   ├── aurea.extract.md
│   │   └── aurea.build.md
│   ├── gemini/                  ← 7 .toml files
│   ├── copilot/                 ← 7 .agent.md files
│   ├── windsurf/                ← 7 .md files
│   ├── devin/                   ← 7 .md files
│   ├── chatgpt/                 ← 7 .md files
│   ├── cursor/                  ← 7 .md files
│   └── generic/                 ← 7 .md files
├── themes/
│   ├── registry.json            ← Global read-only registry (40+ themes)
│   ├── default/
│   │   ├── DESIGN.md
│   │   ├── theme.css
│   │   ├── layout.css
│   │   └── meta.json
│   ├── midnight/                ← (same 4 files)
│   ├── aurora/                  ← (same 4 files)
│   ├── editorial/               ← (same 4 files)
│   ├── brutalist/               ← (same 4 files)
│   └── [31+ imported themes]    ← generated by import script
├── templates/
│   ├── reveal.html.j2           ← Jinja2 template for standalone HTML
│   └── slide_readme.md.j2       ← README.md template for new projects
├── vendor/
│   └── revealjs/
│       └── dist/
│           ├── reveal.js
│           ├── reveal.css
│           ├── reset.css
│           └── plugin/
│               ├── markdown.mjs
│               ├── highlight.mjs
│               ├── notes.mjs
│               └── zoom.mjs
├── _tpl.py                      ← Jinja2 environment setup + custom filters
├── _regex.py                    ← Shared regex patterns (slide split, colors, etc.)
├── _http.py                     ← httpx sync wrapper + robots.txt checker
└── _log.py                      ← Logging config (structured, stderr)

tests/
├── unit/
│   ├── test_init.py
│   ├── test_build.py
│   ├── test_serve.py
│   ├── test_theme.py
│   └── test_extract.py
├── integration/
│   ├── test_init_e2e.py
│   ├── test_build_e2e.py
│   ├── test_serve_e2e.py
│   └── test_extract_e2e.py
└── fixtures/
    ├── sample_slides.md
    ├── default_theme/
    │   ├── DESIGN.md
    │   ├── theme.css
    │   ├── layout.css
    │   └── meta.json
    └── expected_output.html

scripts/
└── import-awesome-designs.py    ← Sync script for VoltAgent/awesome-design-md

build/
└── aurea.spec                   ← PyInstaller spec

.github/workflows/
├── 1-lint-test.yml              ← PR: ruff + mypy + pytest (sequential)
├── 2-build-dist.yml             ← Release: PyInstaller + zipapp + PyPI
└── 3-sync-themes.yml            ← Nightly: sync from awesome-design-md
```

**Structure decision**: Single Python package (Option 1). No frontend/backend split — purely CLI + library. The `commands/` sub-package groups CLI handlers by feature; `_` prefixed modules are internal utilities shared across commands.

---

## Complexity Tracking

> No Constitution Check violations. This section is intentionally left without entries.
