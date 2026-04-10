<!--
SYNC IMPACT REPORT
==================
Version change: (none) → 1.0.0 (initial ratification)
Modified principles: N/A — initial document
Added sections:
  - Core Principles (Articles I–IX)
  - Technical Constraints
  - Mandatory Technology Stack
  - Theme Catalog
  - Presentation Workflow
  - Implementation Milestones
  - Governance
Templates requiring updates:
  ✅ .specify/templates/constitution-template.md — copied from global
  ✅ .specify/templates/plan-template.md — copied from global
  ✅ .specify/templates/spec-template.md — copied from global
  ✅ .specify/templates/tasks-template.md — copied from global
  ⚠  CLAUDE.md — already exists, improvements suggested separately
Deferred TODOs: none
-->

# Aurea Constitution

## Core Principles

### I. Portability Above All

All code MUST run on Python 3.8+.

Forbidden constructs:
- Walrus operator (`:=`)
- Union types with pipe (`X | Y` in annotations)
- `match/case` statements
- Positional-only parameters (`/`)

Required patterns:
- `from __future__ import annotations` at the top of every module **except** modules that use
  `Annotated` at runtime (e.g., Typer CLI entry points). Combining `from __future__ import
  annotations` with runtime-evaluated `Annotated` causes a `TypeError` on Python 3.8 — this is
  a known CPython bug. In those modules, import `Annotated` from `typing_extensions` directly
  without the future import.
- `Union[A, B]` for type hints; `Optional[X]` for nullable types
- `from typing_extensions import Annotated` in all Typer CLI modules (not `typing.Annotated`,
  which is Python 3.9+)

**Rationale**: ~80% of users are on corporate Windows machines where Python 3.8–3.10 is the
maximum available. Code that breaks on 3.8 is code that has failed its users.

### II. Four Distribution Modes Are Mandatory

The project MUST function in four fully self-contained modes. No mode is "limited" — they differ
in convenience, not capability:

1. **Zero-install (copy & paste)**: Copy the `commands/<agent>/` directory to the AI agent's
   command path. No CLI, no dependencies. Works on fully locked-down machines.
2. **Zipapp (.pyz)**: Single Python archive with vendored dependencies. One download, zero
   pip/uv friction.
3. **Standalone executable (PyInstaller)**: `.exe`/`.bin` with no Python on PATH. Corporate
   deployment via SCCM/Intune.
4. **Package manager (pip/uv/pipx)**: Traditional install for developers and CI/CD environments.

If something works in development but fails in any one of these four modes, it is **BROKEN**.
Testing all four modes before a release is mandatory, not optional.

### III. 100% Standalone and Offline Output

The generated HTML MUST NEVER contain `<link href="https://...">` or `<script src="https://...">`.

All CSS, JavaScript (reveal.js 5.x), fonts, and assets MUST be inlined via `<style>`, `<script>`,
or base64 data URIs. The final file (~200–500 KB) MUST open in any browser, offline, without a
server.

**Rationale**: Presentations are sent by email, opened on planes, delivered in rooms without Wi-Fi.
Any external dependency is a point of failure.

### IV. Templates Are the Product; CLI Is Convenience

The real value of Aurea is the seven structured prompt templates (outline, generate, refine,
visual, theme, extract, build) that guide AI agents through a creation workflow. The CLI is a
convenience layer.

Zero-install Mode (Mode 1) MUST be as functional as pip Mode (Mode 4). If a feature only works
with the CLI installed, reprioritize it to also work via pure template.

### V. DESIGN.md Is Dual-Purpose and the Source of Truth

Each theme's `DESIGN.md` serves SIMULTANEOUSLY as:
- **(a)** A human-readable document describing the complete design system across 9 sections:
  visual theme, color palette, typography, components, layout, depth, do's/don'ts, responsive,
  agent prompt guide.
- **(b)** A structured source parsed by `extract.py` and consumed by AI agents.

Changes to the DESIGN.md format MUST be coordinated across:
- `docs/theme-system.md` (documentation)
- `extract.py` (parser)
- Agent command templates

Never alter one without updating the others.

### VI. Agent Commands Are Versioned and Frozen

Prompt templates in `src/aurea/agent_commands/` are embedded in distributions (zipapp, exe, pip).
They are NOT live-fetched. Consistency between what the user downloaded and what executes is
mandatory.

Supported agents and their formats:

| Agent     | Commands dir  | File format    |
|-----------|---------------|----------------|
| Claude    | `claude/`     | `.md`          |
| Gemini    | `gemini/`     | `.toml`        |
| Copilot   | `copilot/`    | `.agent.md`    |
| Windsurf  | `windsurf/`   | `.md`          |
| Devin     | `devin/`      | `.md`          |
| ChatGPT   | `chatgpt/`    | `.md`          |
| Cursor    | `cursor/`     | `.md`          |
| Generic   | `generic/`    | `.md`          |

### VII. Minimal and Controlled Dependencies

Install size MUST remain under 50 MB.

**Permitted core dependencies**:
- `typer[all]>=0.9.0`
- `jinja2>=3.0`
- `httpx>=0.25`
- `beautifulsoup4>=4.12`
- `cssutils>=2.10`
- `watchdog>=3.0`

**Permitted dev dependencies**:
- `pytest>=7.0`, `pytest-cov>=4.0`
- `mypy>=1.0`
- `ruff>=0.1.0`
- `pyinstaller>=6.0`

Adding Django, numpy, ML libraries, or any heavy dependency is FORBIDDEN. Each new dependency
MUST justify its existence with an impact analysis across all four distribution modes. If the
stdlib can do it, use the stdlib.

### VIII. reveal.js 5.x — Pinned, No Upgrade

Use EXCLUSIVELY reveal.js `>=5.0.0, <6.0`. The 6.x line introduces breaking changes.

reveal.js MUST be vendored in the project (not installed via npm). Its JavaScript and CSS MUST be
inlined in the HTML output. CDN references and external `src` attributes are forbidden.

### IX. Test-First with Minimum 80% Coverage

Tests MUST be written before or alongside implementation (TDD).

- **Coverage minimum**: 80% for `src/aurea/`
- **Unit tests** (`tests/unit/`): Mock external I/O (httpx, filesystem)
- **Integration tests** (`tests/integration/`): Use real temp directories — DO NOT mock the build
  pipeline. A test that passes with mocks but fails on a real filesystem is worthless.
- **Framework**: `pytest` + `pytest-cov`
- **Linting**: `ruff check .` + `ruff format --check .`
- **Type checking**: `mypy src/`

---

## Technical Constraints

### Logging and Output

- CLI output → `stdout` (for piping)
- Logs → `stderr` (for user visibility)
- Use the configured `_log.py` module. `print()` for operational logging is FORBIDDEN.
- Structured logging with levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### Imports and Code Structure

- ALWAYS use absolute imports (`from aurea.cli import ...`). Relative imports break PyInstaller
  bundling.
- Entry point: `aurea = aurea.cli:app` (Typer)
- Internal utility modules MUST be prefixed with underscore: `_tpl.py`, `_regex.py`, `_http.py`,
  `_log.py`

### Git and Commits

- Feature branches from `main` for all changes
- Atomic commits: one feature or one bug fix per commit
- Clear, descriptive commit messages
- No AI attribution in commits, docs, or code
- PR required before merge to `main`

### CI/CD (GitHub Actions)

- **`1-lint-test.yml`**: `ruff check` + `ruff format --check` + `mypy` +
  `pytest --cov-fail-under=80`. Runs on PR, NOT on push to main.
- **`2-build-dist.yml`**: PyInstaller + zipapp + PyPI publish. Runs on release.
- **`3-sync-themes.yml`**: Periodic sync with `VoltAgent/awesome-design-md`.

---

## Mandatory Technology Stack

| Layer         | Technology                          | Justification                    |
|---------------|-------------------------------------|----------------------------------|
| CLI           | Python 3.8+ / Typer                 | Maximum portability              |
| Templates     | Jinja2                              | Lightweight, no native deps      |
| Prompt templates | Markdown / pure TOML             | Agent-agnostic                   |
| Presentation  | reveal.js 5.x (vendored)            | Offline-capable                  |
| Themes        | DESIGN.md (9 sections) + CSS props  | Dual-purpose                     |
| Extraction    | httpx + beautifulsoup4 + cssutils   | Robust HTML/CSS parsing          |
| Distribution  | PyInstaller + zipapp + pip          | Four modes                       |
| CI/CD         | GitHub Actions                      | Cross-platform                   |
| Tests         | pytest + pytest-cov                 | Unit + integration               |
| Linting       | ruff                                | Check + format                   |
| Type checking | mypy                                | Consistency                      |

---

## Theme Catalog

### Original Themes (5)

`default`, `midnight`, `aurora`, `editorial`, `brutalist`

### Imported Themes (31+)

Imported from `VoltAgent/awesome-design-md`:
`apple`, `stripe`, `linear`, `claude`, `vercel`, `figma`, `notion`, `ferrari`, `spacex`,
plus 20+ others across categories: AI/ML, DevTools, Infrastructure, Design, Enterprise,
Automotive, Finance, Social/Media.

### Registry Format

`registry.json` MUST index all themes with: `id`, `name`, `category`, `tags`, `mood`, `colors`,
`typography`, `path`.

The import script `scripts/import-awesome-designs.py` automates:
`clone → parse DESIGN.md → generate meta.json + theme.css + layout.css → update registry`

---

## Presentation Workflow (7 Phases)

```
/aurea.theme → /aurea.outline → /aurea.generate → /aurea.refine → /aurea.visual → /aurea.build
/aurea.extract → (new theme generated) → feeds the flow above
```

Each command is independent. `theme` and `extract` are optional.

---

## Implementation Milestones

| Milestone | Scope |
|-----------|-------|
| M0 | Repo + pyproject.toml + CI + CLI with placeholder commands |
| M1 | Prompt templates (7 commands × 8 agents) + CLI scaffolding (`aurea init`) |
| M2 | Theme system (40+ designs imported, registry, `aurea theme` CLI) |
| M3 | Build pipeline (Markdown → HTML via Jinja2, reveal.js vendored, `aurea serve`) |
| M4 | Theme extraction (web scraping → DESIGN.md + CSS, `aurea extract`) |
| M5 | Distribution (PyInstaller, zipapp, PyPI, code signing, GitHub releases) |

---

## Governance

Any amendment to these constitutional articles requires:
1. Explicit documented justification
2. Impact analysis across all four distribution modes
3. Maintainer approval

The constitution exists to protect the project from impulsive decisions — respect it.

**Amendment process**:
- MAJOR version bump: removal or redefinition of a core principle
- MINOR version bump: new principle or section added / materially expanded
- PATCH version bump: clarifications, wording, typo fixes

All PRs and code reviews MUST verify compliance with the active constitutional principles.

**Version**: 1.0.0 | **Ratified**: 2026-04-08 | **Last Amended**: 2026-04-08
