# Tasks: Aurea CLI and Presentation Toolkit

**Input**: `/specs/001-aurea-cli-toolkit/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/cli-commands.md ✅ quickstart.md ✅

**Tests**: Included — Constitution Art. IX mandates test-first with ≥80% coverage.

**Organization**: Tasks grouped by user story. US1 (Scaffolding) → US2 (Themes + Build) → US3 (Extraction). US2 and US3 depend on US1 foundational completion; beyond that, each story is independently testable.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton, tooling configuration, and CI/CD setup that blocks all subsequent work.

- [X] T001 Create `pyproject.toml` with: name `aurea`, version `0.1.0`, python `>=3.8`, core deps (`typer[all]>=0.9.0,<0.21`, `jinja2>=3.0`, `mistune>=2.0.5,<3.1`, `rich>=13.0`, `watchdog>=3.0`, `pyyaml>=6.0`), extract extras (`httpx>=0.25`, `beautifulsoup4>=4.12`, `cssutils>=2.10`, `lxml>=4.9`), dev deps (`pytest>=7.0`, `pytest-cov>=4.0`, `mypy>=1.0`, `ruff>=0.1.0`, `pyinstaller>=6.0`), entry point `aurea = aurea.cli:app`; include mypy config section: `[tool.mypy]\npython_version = "3.8"\nignore_missing_imports = true\nwarn_unused_ignores = true`; **Art. VII size gate**: add a comment block in pyproject.toml listing each dep with its approximate wheel size; any future PR adding a new dependency MUST include a size justification comment and manually verify that `pip install aurea` total remains under 50 MB — the CI `1-lint-test.yml` step should also include `pip install -e . && pip show aurea` to surface the install footprint in the build log
- [X] T002 [P] Create `ruff.toml` with: `target-version = "py38"`, `line-length = 100`, select `["E", "F", "I", "UP"]`, exclude `["src/aurea/vendor"]`
- [X] T003 [P] Create `src/aurea/__init__.py` with `__version__ = "0.1.0"` and package docstring
- [X] T004 [P] Create `src/aurea/_log.py`: configure `logging.getLogger("aurea")` with `RichHandler(console=Console(stderr=True))`, levels DEBUG/INFO/WARNING/ERROR, exported `_log` instance
- [X] T005 [P] Create `.github/workflows/1-lint-test.yml`: sequential jobs (lint → typecheck → test), triggers on PR only (not push to main), steps: `ruff check .` + `ruff format --check .` → `mypy src/` → `pytest tests/ --cov=src/aurea --cov-fail-under=80`; **add Art. VII size gate step** before lint: `pip install -e . && pip show aurea` — this surfaces the install footprint in the CI build log so reviewers can spot size regressions when new deps are added
- [X] T006 [P] Create `.github/workflows/2-build-dist.yml`: triggers on release tag `v*`, jobs: build PyInstaller exe (Windows + macOS + Linux) + build zipapp `.pyz` + publish to PyPI
- [X] T007 [P] Create `.github/workflows/3-sync-themes.yml`: scheduled nightly, runs `python scripts/import-awesome-designs.py`, exits 0 on upstream failure (silent failure per FR-clarification), commits updated themes if changed
- [X] T008 [P] Create `build/aurea.spec` (PyInstaller): `Analysis(['src/aurea/cli.py'])`, datas including `src/aurea/vendor`, `src/aurea/themes`, `src/aurea/agent_commands`, `src/aurea/templates`; `hiddenimports=['typer', 'jinja2', 'mistune', 'rich', 'watchdog', 'yaml', 'urllib.robotparser']` — `yaml` is the `pyyaml` import name and may not be detected by static analysis; `urllib.robotparser` is stdlib but sometimes missed in frozen mode
- [X] T009 Create `tests/` directory structure: `tests/unit/`, `tests/integration/`, `tests/fixtures/`; create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`; create `tests/conftest.py` with `tmp_path`-based project fixture

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared internal utilities and the CLI skeleton that ALL user story implementations depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T010 Create `src/aurea/commands/__init__.py` (empty, marks package)
- [X] T010a [P] Create `src/aurea/exceptions.py`: define `class AureaError(Exception): pass`; this is the single shared exception base for all Aurea-specific errors raised across commands and utilities
- [X] T011 [P] Create `src/aurea/_regex.py`: compile and export regex constants: `SLIDE_SEP` (split on `^---$`), `SPEAKER_NOTES` (match `\nNote:` or `\nNotes:`), `HTML_ATTR` (match `<!-- .slide: ... -->`), `HEX_COLOR` (`#[0-9a-fA-F]{6}\b`), `EXTERNAL_LINK` (match `<(link|script)[^>]+https?://[^>]*>`)
- [X] T012 [P] Create `src/aurea/_tpl.py`: initialize `jinja2.Environment(loader=PackageLoader("aurea", "templates"), autoescape=False)`, export `render_template(name, **ctx) -> str` helper, add custom filter `inline_file(path) -> str` that reads a file and returns its text content
- [X] T013 [P] Create `src/aurea/_http.py`: add `from aurea.exceptions import AureaError` at module top; implement `check_robots(url, user_agent) -> bool` using `urllib.robotparser.RobotFileParser`; if `RobotFileParser.read()` raises `urllib.error.URLError` (robots.txt unreachable or returns non-200), return `True` (allow by default — permissive fallback; aligns with T048 test which asserts `True` when robots.txt is unreachable); implement `fetch_sync(url, user_agent, timeout) -> str` using `httpx.Client`; handle `TimeoutException` → `AureaError`, `HTTPStatusError` 403/404 → `AureaError` with specific messages; **lazy-import httpx** at call time (not at module level) since `httpx` is in the `[extract]` optional group — use `try: import httpx except ImportError: raise AureaError("httpx not installed. Run: pip install aurea[extract]")` inside `fetch_sync()`
- [X] T014 Create `src/aurea/cli.py`: `app = typer.Typer(name="aurea")`; `--version` callback with `is_eager=True`; register single commands with `@app.command()` for `init`, `build`, `serve`, `extract`; create `theme_app = typer.Typer()` and register as `app.add_typer(theme_app, name="theme")` (only the `theme` group uses `add_typer`; other commands use `@app.command()` directly); **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` instead (Constitution Art. I exception for Typer modules); **do NOT import `src/aurea/commands/extract.py` at module top level** — `extract` depends on `[extract]` optional deps; import it lazily inside the `extract` command callback body with a `try/except ImportError` guard that raises `AureaError`; all other command bodies are stubs (`typer.echo("not implemented"); raise typer.Exit(1)`) — wired in later tasks
- [X] T015 Vendor reveal.js 5.x: download latest 5.x release from GitHub, place `dist/reveal.js`, `dist/reveal.css`, `dist/reset.css`, `dist/plugin/markdown.mjs`, `dist/plugin/highlight.mjs`, `dist/plugin/notes.mjs`, `dist/plugin/zoom.mjs` into `src/aurea/vendor/revealjs/`; record exact version in `src/aurea/vendor/revealjs/VERSION`
- [X] T016 [P] Create `tests/fixtures/default_theme/`: minimal but complete theme — `DESIGN.md` (9 sections with placeholder content), `theme.css` (CSS custom properties with test values), `layout.css` (empty rules), `meta.json` (`{"id": "default", "name": "Default", "category": "general", "tags": ["clean"], "mood": "Neutral", "colors": {"primary": "#333", "background": "#fff", "text": "#111"}, "typography": {"heading": "sans-serif", "body": "sans-serif"}}`)
- [X] T017 [P] Create `tests/fixtures/sample_slides.md`: 5-slide presentation with YAML frontmatter, `---` separators, at least one `Note:` block, one `<!-- .slide: data-background="#000" -->` attribute, one code block, and one slide with >40 words (for warning test)

**Checkpoint**: Foundation complete — `aurea --version` works, all internal utilities importable, CI workflow files exist.

---

## Phase 3: User Story 1 — Scaffolding and AI-Guided Presentation Creation (Priority: P1) 🎯 MVP

**Goal**: `aurea init` creates a complete project with agent-native prompt templates, `config.json`, and the selected theme.

**Independent Test**: `aurea init my-demo --agent claude --theme default` → verify directory structure, 7 `.md` files in `.claude/commands/`, valid `config.json`, `$ARGUMENTS` placeholder present in templates.

### Tests for User Story 1 ⚠️ Write first — verify they FAIL before implementing

- [X] T018 [P] [US1] Write integration test `tests/integration/test_init_e2e.py`: test `aurea init` creates full directory structure, config.json has correct fields, 7 command files exist in correct agent dir; test `--here` flag; test `--force` preserves `slides/`; test defaults applied + stderr message; test unknown theme → exit code 1; **add SC-001 timing assertion**: wrap CLI invocation with `time.perf_counter()` and assert `elapsed < 2.0` (e.g., `start = time.perf_counter(); runner.invoke(app, [...]); assert time.perf_counter() - start < 2.0`)
- [X] T019 [P] [US1] Write unit test `tests/unit/test_init.py`: test `AGENT_CONFIG` lookup for all 8 agents; test placeholder substitution logic (`{{DESIGN_MD_PATH}}` → correct path); test `--lang` fallback fires for any lang other than `en` (v1 English-only scope per FR-002); test that Gemini templates in `src/aurea/agent_commands/gemini/` are `.toml` format with `{{args}}` placeholder (verifying authoring-time conversion was done correctly in T023 — there is no runtime conversion); **add FR-028 Mode 1 fallback assertion**: load `src/aurea/agent_commands/claude/aurea.extract.md` and assert body contains keywords indicating agent-native web fetch (e.g., `"fetch"`, `"no CLI"` or `"without aurea"`) and generates DESIGN.md + theme.css inline — verifying zero-install capability without the CLI; **add SC-002 structural assertion**: iterate all 8 entries in `AGENT_CONFIG` and assert each of the 7 expected template files exists in `src/aurea/agent_commands/<agent>/` and is non-empty with at least `name:` in its content — total 56 files asserted (SC-002 structural coverage without live agent execution)

### Implementation for User Story 1

- [X] T020 [US1] Implement `AGENT_CONFIG` dict in `src/aurea/commands/init.py`: 8 entries mapping agent id → `(commands_dir, file_format, arg_placeholder)` per contracts/cli-commands.md agent table
- [X] T021 [US1] Implement `ProjectConfig` dataclass + `write_config(path, agent, theme, themes_dir, slides_dir, output_dir) -> None` in `src/aurea/commands/init.py`; serialize to JSON with `json.dump`
- [X] T022 [P] [US1] Create 7 canonical Claude prompt templates in `src/aurea/agent_commands/claude/`: `aurea.theme.md`, `aurea.outline.md`, `aurea.generate.md`, `aurea.refine.md`, `aurea.visual.md`, `aurea.extract.md`, `aurea.build.md`; each with YAML frontmatter (`name`, `description`) + Markdown body enforcing the 7 template principles (context-first, DESIGN.md reference, narrative arc, ≤40 words, speaker notes, visual-first, do's/don'ts); use `{{DESIGN_MD_PATH}}`, `{{CONFIG_PATH}}`, `$ARGUMENTS` placeholders
- [X] T023 [P] [US1] Create 7 Gemini prompt templates in `src/aurea/agent_commands/gemini/` as `.toml` files; convert from canonical Claude templates replacing `$ARGUMENTS` with `{{args}}`; TOML format: `[command]\nname = "..."\ndescription = "..."\nbody = """..."""`
- [X] T024a [P] [US1] Create 7 Copilot templates in `src/aurea/agent_commands/copilot/` as `.agent.md` files; converted from canonical Claude templates with `$ARGUMENTS` placeholder preserved; Copilot is the only agent requiring the `.agent.md` extension (all others use `.md`)
- [X] T024b [P] [US1] Create 7 templates each for windsurf, devin, chatgpt, cursor, and generic in `src/aurea/agent_commands/{agent}/` as `.md` files; all 5 share identical format and `$ARGUMENTS` placeholder — copy from Claude canonical with agent-specific frontmatter `name` field only
- [X] T025 [US1] Implement `substitute_placeholders(template_text, paths) -> str` in `src/aurea/commands/init.py`: replace all 7 placeholders (`{{DESIGN_MD_PATH}}`, `{{THEME_CSS_PATH}}`, `{{CONFIG_PATH}}`, `{{REGISTRY_PATH}}`, `{{SLIDES_DIR}}`, `{{OUTPUT_DIR}}`, agent-specific arg placeholder)
- [X] T026 [US1] Implement `copy_agent_commands(agent_id, project_root, paths, commands_dir_override=None) -> None` in `src/aurea/commands/init.py`: if `commands_dir_override` is not None (from `--commands-dir` CLI option), use it as the write target; otherwise use the default from `AGENT_CONFIG[agent_id].commands_dir`; read pre-built per-agent templates (T022–T024b already created them in their native formats — no runtime format conversion needed), substitute placeholders via `substitute_placeholders()`, write to target `commands_dir`; the `.toml`/`.agent.md`/`.md` format distinction is resolved at authoring time (T022–T024b), not at `aurea init` time
- [X] T027 [US1] Create `src/aurea/templates/slide_readme.md.j2`: Jinja2 template for the project README.md scaffold — include placeholders for `{{ project_name }}`, `{{ agent }}`, `{{ theme }}`, and a quick-start usage section showing the 7 workflow commands; then implement `scaffold_project(project_dir, agent, theme, lang, no_git, force, commands_dir=None) -> None` in `src/aurea/commands/init.py`: create dirs (`.aurea/`, `slides/`, `output/`), copy selected theme files, write `config.json`, call `copy_agent_commands(agent, project_dir, paths, commands_dir_override=commands_dir)` passing the `commands_dir` value through, render and write `README.md` from the `slide_readme.md.j2` template, optionally run `git init`
- [X] T028 [US1] Create `src/aurea/themes/default/` with production-quality files: `DESIGN.md` (9 sections describing a clean, minimal default), `theme.css` (CSS custom properties: `--r-background-color: #ffffff`, `--r-main-color: #333`, `--r-main-font: "Helvetica Neue", Helvetica, Arial, sans-serif`, etc.), `layout.css` (standard grid + animations), `meta.json`
- [X] T028a [P] [US1] Create `src/aurea/themes/midnight/` with 4 files: `DESIGN.md` (9 sections: dark background `#0d0d0d`, accent `#7c3aed`, minimal sans-serif), `theme.css` (CSS custom properties for dark theme), `layout.css`, `meta.json` (`{"id": "midnight", "category": "dark", "tags": ["dark", "minimal", "purple"], "mood": "Focused, mysterious, elegant"}`)
- [X] T028b [P] [US1] Create `src/aurea/themes/aurora/` with 4 files: `DESIGN.md` (9 sections: dark background with gradient accents in teal/green `#10b981`/`#06b6d4`), `theme.css`, `layout.css`, `meta.json` (`{"id": "aurora", "category": "dark", "tags": ["dark", "gradient", "teal"], "mood": "Vibrant, futuristic, energetic"}`)
- [X] T028c [P] [US1] Create `src/aurea/themes/editorial/` with 4 files: `DESIGN.md` (9 sections: white background, serif typography, newspaper-inspired layout, `#1a1a1a` text), `theme.css`, `layout.css`, `meta.json` (`{"id": "editorial", "category": "print", "tags": ["serif", "white", "classic"], "mood": "Authoritative, trustworthy, refined"}`)
- [X] T028d [P] [US1] Create `src/aurea/themes/brutalist/` with 4 files: `DESIGN.md` (9 sections: high-contrast black/white, bold sans-serif, raw aesthetic, thick borders), `theme.css`, `layout.css`, `meta.json` (`{"id": "brutalist", "category": "experimental", "tags": ["bold", "contrast", "raw"], "mood": "Bold, provocative, unconventional"}`)
- [X] T029 [US1] Create initial `src/aurea/themes/registry.json` with all 5 original themes (default + midnight + aurora + editorial + brutalist — now with real files from T028–T028d); set `version: "1.0.0"`, `sources: []`
- [X] T030 [US1] Wire `aurea init` Typer command in `src/aurea/commands/init.py` per contracts/cli-commands.md: `PROJECT_NAME` argument, all 7 options (`--agent`, `--theme`, `--here`, `--force`, `--no-git`, `--commands-dir`, `--lang`), apply defaults + stderr report, call `scaffold_project(project_dir, agent, theme, lang, no_git, force, commands_dir=commands_dir_option)` — explicitly pass the `--commands-dir` option value as the `commands_dir` keyword argument so it threads through to `copy_agent_commands()`; register command in `src/aurea/cli.py`; **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` for all Typer option/argument types (Art. I exception: same rule as cli.py)

**Checkpoint**: `aurea init my-demo --agent claude --theme default` creates complete project. Unit + integration tests pass. This is the MVP.

---

## Phase 4: User Story 2 — Theme Library, Search, and Build Pipeline (Priority: P2)

**Goal**: `aurea theme` commands browse/apply 36+ themes; `aurea build` produces offline-capable reveal.js HTML; `aurea serve` provides live preview.

**Independent Test**: `aurea theme search "dark"` returns results; `aurea theme use midnight`; copy `tests/fixtures/sample_slides.md` to a project; `aurea build` → `output/presentation.html` opens offline with zero external resource refs.

### Tests for User Story 2 ⚠️ Write first — verify they FAIL before implementing

- [X] T031 [P] [US2] Write integration test `tests/integration/test_build_e2e.py`: test full pipeline from `sample_slides.md` + fixture theme → verify output HTML exists, no `https://` in output, HTML contains `<div class="reveal">`, slide count matches, speaker notes not in main content; test `--theme` flag overrides config; test empty slides → exit code 1; test `--minify` reduces file size; **add SC-008 byte-range assertion**: `html_bytes = Path("output/presentation.html").read_bytes(); assert 200_000 < len(html_bytes) < 500_000` (without `--embed-fonts`)
- [X] T032 [P] [US2] Write integration test `tests/integration/test_serve_e2e.py`: test server starts on default port, serves HTML file, responds with HTTP 200; test port conflict → finds next available port; test server shuts down cleanly on Ctrl+C; **add SC-009 timing assertion**: `start = time.perf_counter(); [start server]; [make GET request]; assert time.perf_counter() - start < 1.0` — server must be accepting connections within 1 second of launch
- [X] T033 [P] [US2] Write unit test `tests/unit/test_theme.py`: test `search_themes()` fulltext across name/tags/mood/category; test local registry shadows global; test `theme_use()` copies 4 files + updates config.json; test missing theme → error; test DESIGN.md validation (9 sections); **add SC-006 timing assertion**: build in-memory registry with 40 theme entries, call `search_themes(registry, "dark")` and assert `elapsed < 0.5`; **add SC-010 registry count assertion**: after running import script or loading a 36-entry fixture, assert `len(registry["themes"]) >= 36`; **add FR-011 swatches assertion**: call `theme_info(theme_id, registry)` (or capture Rich console output) and assert the returned string contains at least one ANSI color escape sequence or Rich color markup (`[#` or `\x1b[`) corresponding to the theme's primary/background/text color values
- [X] T034 [P] [US2] Write unit test `tests/unit/test_build.py`: test `parse_slides()` splits on `---`, extracts frontmatter, extracts `Note:` to speaker notes, extracts `<!-- .slide: -->` to attributes; test word count > 40 emits warning; test `resolve_theme()` precedence (CLI flag > config > frontmatter)

### Implementation for User Story 2

- [X] T035 [US2] Implement `parse_slides(markdown_text) -> Presentation` in `src/aurea/commands/build.py`: parse YAML frontmatter, split on `SLIDE_SEP` regex, extract `Note:` blocks and HTML attributes per slide, populate `Slide` objects with `word_count`, skip empty slides; **do NOT add `from __future__ import annotations`** to this file — later tasks (T040) add Typer commands to `build.py` that require `typing_extensions.Annotated` at runtime (Art. I exception)
- [X] T036 [US2] Implement `resolve_theme(config_path, cli_theme, frontmatter_theme) -> Tuple[str, Path]` in `src/aurea/commands/build.py`: apply precedence rule (CLI > config > frontmatter), locate theme dir (local `.aurea/themes/` first, then global `src/aurea/themes/`); validate 9 DESIGN.md sections exist using a `REQUIRED_SECTIONS` frozenset of 9 lowercase keywords (`{"visual theme", "color palette", "typography", "components", "layout", "depth", "do's", "responsive", "agent prompt"}`) checked via case-insensitive substring match against the DESIGN.md text — raises `AureaError` listing which sections are missing if fewer than 9 match
- [X] T037 [US2] Implement `render_slides(presentation, theme_dir) -> str` in `src/aurea/commands/build.py`: use mistune `create_markdown(renderer=SlideRenderer())` to convert each `Slide.markdown` to `Slide.html`; `SlideRenderer` overrides `block_code()` using `pygments.highlight()` with `HtmlFormatter(nowrap=True, cssclass="highlight")` for syntax-highlighted code blocks — **Pygments is already a transitive dependency via `rich>=13.0`**, no new dependency needed (Art. VII safe)
- [X] T038 [US2] Create `src/aurea/templates/reveal.html.j2`: Jinja2 template that inlines `reset.css`, `reveal.css`, `theme.css`, `layout.css` into `<style>` tags and `reveal.js`, `markdown.mjs`, `highlight.mjs`, `notes.mjs`, `zoom.mjs` into `<script>` tags; renders `<section>` per slide with speaker notes in `<aside class="notes">`; `Reveal.initialize({ plugins: [RevealMarkdown, RevealHighlight, RevealNotes, RevealZoom] })` call at end
- [X] T039 [US2] Implement `inline_assets(html, theme_dir, embed_fonts) -> str` in `src/aurea/commands/build.py`: read reveal.js vendor files + theme CSS, inject into template context; if `embed_fonts=True` base64-encode woff2 files and replace font URLs with data URIs; apply `EXTERNAL_LINK` regex to strip any stray CDN references
- [X] T040 [US2] Implement `aurea build` command in `src/aurea/commands/build.py`: wire together parse → resolve → render → inline → write; accept all 6 options per contract; emit build summary to stderr; implement `--watch` mode via watchdog `Observer` watching `slides/` and `.aurea/themes/` with 500ms debounce; implement `--minify` using stdlib-only approach: apply a single regex pass to collapse consecutive whitespace between HTML tags (`re.sub(r'>\s+<', '><', html)`) — no external minification dependency (Art. VII); register command in `src/aurea/cli.py`; **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` for all Typer option/argument types (Art. I exception)
- [X] T041 [US2] Implement HTTP server in `src/aurea/commands/serve.py`: add `from aurea.exceptions import AureaError` at module top; find available port starting at `--port` default 8000 (try sequential up to 8100), bind to `--host` (default `127.0.0.1`); use a custom handler subclass of `http.server.SimpleHTTPRequestHandler` that overrides `do_GET` to redirect `/` and `/index.html` to `/presentation.html` — so the root URL opens the presentation directly; serve from the `output/` directory; if `output/presentation.html` does not exist, raise `AureaError` with message "No presentation found. Run `aurea build` first."; print URL as `http://{host}:{port}/presentation.html` to stdout
- [X] T042 [US2] Implement `aurea serve` Typer command in `src/aurea/commands/serve.py`: accept `--port`, `--host`, `--watch`, `--input`; with `--watch` start watchdog + rebuild loop + serve; without `--watch` serve only; register command in `src/aurea/cli.py`; **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` for all Typer option/argument types (Art. I exception)
- [X] T043 [US2] Implement theme registry operations in `src/aurea/commands/theme.py`: `load_registry(project_root) -> Registry` (merge local + global, local shadows global); `search_themes(registry, query, category, tag) -> List[ThemeMeta]` (fulltext rank across id/name/tags/mood/category); `apply_theme(theme_id, project_root) -> None` (copy 4 files + update config.json + update local registry); **do NOT add `from __future__ import annotations`** to this file — T044 adds Typer subcommands to `theme.py` that require `typing_extensions.Annotated` at runtime (Art. I exception)
- [X] T044 [US2] Implement all 6 `aurea theme` subcommands in `src/aurea/commands/theme.py` per contract: `list` (Rich table or JSON), `search` (table/JSON with filters), `info` (Rich panel with color swatches), `show` (print DESIGN.md with Rich Markdown), `use` (copy theme + update config), `create` (scaffold 4 files with annotated templates); register theme sub-group in `src/aurea/cli.py`; **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` for all Typer option/argument types (Art. I exception)
- [X] T045 [P] [US2] Create `scripts/import-awesome-designs.py`: clone/update `VoltAgent/awesome-design-md`; for each `design-md/<name>/DESIGN.md`: parse 9 sections for color/typography tokens, generate `meta.json` + `theme.css` + `layout.css`; write to `src/aurea/themes/<name>/`; update `src/aurea/themes/registry.json`; exit 0 on network failure (log warning to stderr)
- [X] T046 [US2] Run `python scripts/import-awesome-designs.py` locally to populate `src/aurea/themes/` with 31+ imported themes; verify `registry.json` has 36+ entries total; commit imported theme files

**Checkpoint**: `aurea theme list` shows 36+ themes. `aurea build` on `sample_slides.md` produces valid offline HTML. `aurea serve` starts and serves. All US2 tests pass independently.

---

## Phase 5: User Story 3 — Theme Extraction via Web Scraping (Priority: P3)

**Goal**: `aurea extract <url> --name <id>` fetches a public URL, extracts design tokens, and produces a complete Aurea theme.

**Independent Test**: Point `aurea extract` at a local HTTP server serving a sample HTML page with known CSS → verify `.aurea/themes/<name>/` contains 4 valid theme files with tokens matching the source CSS.

### Tests for User Story 3 ⚠️ Write first — verify they FAIL before implementing

- [X] T047 [P] [US3] Write integration test `tests/integration/test_extract_e2e.py`: spin up `http.server` in `tmp_path` serving a hand-crafted HTML + CSS fixture with known hex colors and font-family declarations; run `aurea extract http://localhost:<port> --name test-extract`; verify `DESIGN.md` has 9 sections, `theme.css` contains CSS custom properties, `meta.json` has colors array; test `--raw` skips semantic interpretation; test `robots.txt` blocking → exit code 1; **add SC-014 timing assertion**: `start = time.perf_counter(); [run extract]; assert time.perf_counter() - start < 30.0` — full depth-1 extraction must complete within 30 seconds
- [X] T048 [P] [US3] Write unit test `tests/unit/test_extract.py`: test `DesignExtractor.extract_color_tokens()` returns ranked dict with `primary`/`background`/`text` roles; test CDN filter rejects `fonts.googleapis.com`, `unpkg.com`, `cdn.jsdelivr.net`; test `generate_raw_design_md()` outputs string with exactly 9 section headers; test `check_robots()` returns True when robots.txt unreachable

### Implementation for User Story 3

- [X] T049 [US3] Implement `DesignExtractor.__init__()` and `fetch_page(url) -> str` in `src/aurea/commands/extract.py`: add `from aurea.exceptions import AureaError` at module top; accept `url`, `user_agent`, `timeout`, `delay`, `depth`, `raw`; `fetch_page` calls `check_robots()` from `_http.py` first (abort with `AureaError` if disallowed), then calls `fetch_sync()`; log progress to stderr; **lazy-import beautifulsoup4 and lxml** at call time inside methods that use them — use `try: from bs4 import BeautifulSoup except ImportError: raise AureaError("beautifulsoup4 not installed. Run: pip install aurea[extract]")` — same pattern as httpx in `_http.py`; **do NOT add `from __future__ import annotations`** to this file — T057 adds a Typer command to `extract.py` that requires `typing_extensions.Annotated` at runtime (Art. I exception)
- [X] T050 [US3] Implement `DesignExtractor.extract_stylesheets(html, base_url) -> List[str]` in `src/aurea/commands/extract.py`: define module-level helper `should_skip_cdn(url: str) -> bool` that checks the URL hostname against a `frozenset` of known CDN hostnames (`{"fonts.googleapis.com", "fonts.gstatic.com", "unpkg.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"}`) and returns `True` if it should be skipped (FR-024); parse HTML with BeautifulSoup `lxml`, collect `<style>` tag text, collect `<link rel="stylesheet">` hrefs filtered by `should_skip_cdn()`, fetch external CSS sheets via `_http.fetch_sync()`, merge all into list of CSS text strings
- [X] T051 [US3] Implement `DesignExtractor.extract_color_tokens(css_list) -> Dict[str, str]` in `src/aurea/commands/extract.py`: use `_regex.HEX_COLOR` to find all hex colors in merged CSS, rank by frequency with `collections.Counter`, assign semantic roles: most-frequent dark→`text`, most-frequent light→`background`, high-frequency non-neutral→`primary`, next→`secondary`, remainder→`accent`
- [X] T052 [P] [US3] Implement `DesignExtractor.extract_typography_tokens(css_list) -> Dict[str, str]` in `src/aurea/commands/extract.py`: use `cssutils.parseString()` to iterate rules, extract `font-family` values ranked by selector specificity weight, identify heading font (h1/h2 selectors) vs body font (`body`/`p` selectors); **lazy-import cssutils** at call time — use `try: import cssutils except ImportError: raise AureaError("cssutils not installed. Run: pip install aurea[extract]")` — same pattern as httpx in `_http.py`
- [X] T053 [P] [US3] Implement `DesignExtractor.extract_spacing_tokens()` and `extract_shadow_tokens()` in `src/aurea/commands/extract.py`: extract top 3 `margin`/`padding`/`gap` values by frequency → return `Dict[str, str]` with keys `sm`, `md`, `lg` (e.g. `{"sm": "4px", "md": "8px", "lg": "16px"}`); extract unique `box-shadow` values → return `List[str]` of raw shadow strings; these keys are consumed by T054 (DESIGN.md f-string sections 5–6) — keep consistent
- [X] T054 [US3] Implement `DesignExtractor.generate_raw_design_md(tokens) -> str` in `src/aurea/commands/extract.py`: use **f-strings** (not Jinja2/`_tpl.py`) to generate 9-section DESIGN.md — section headers are static strings; token values are simple interpolations; no looping or template logic needed; reserve `_tpl.py` for HTML rendering only — section 1: visual theme summary, section 2: color palette with hex values, section 3: typography, sections 4–8: populated with extracted token data or `<!-- TODO: fill in -->` placeholders, section 9: agent prompt guide boilerplate
- [X] T055 [US3] Implement `DesignExtractor.generate_theme_css(tokens) -> str` in `src/aurea/commands/extract.py`: map extracted color/typography tokens to reveal.js CSS custom properties per research.md token mapping table (`--r-background-color`, `--r-main-color`, `--r-main-font`, `--r-heading-color`, `--r-heading-font`, `--r-link-color`, etc.); wrap in `:root { ... }`
- [X] T056 [US3] Implement `DesignExtractor.run() -> Dict[str, Any]` in `src/aurea/commands/extract.py`: orchestrate full pipeline (fetch → stylesheets → tokens → DESIGN.md + theme.css + layout.css + meta.json); if `depth > 1` extract internal links (same domain only) and crawl with `time.sleep(delay)` between requests; write all 4 files to output theme dir; write `layout.css` as a minimal default: `/* Layout overrides — customize as needed */\n:root {}\n` (theme-specific layout is post-extraction manual work — extracted themes have correct colors/fonts via theme.css but default spacing); update local registry; return dict with output paths and token summary
- [X] T057 [US3] Implement `aurea extract` Typer command in `src/aurea/commands/extract.py` per contract: `URL` argument, all 7 options (`--name`, `--depth`, `--raw`, `--use`, `--timeout`, `--user-agent`, `--delay`); derive theme name from URL hostname if `--name` omitted; on success print token summary to stdout; if `--use` apply theme; register command in `src/aurea/cli.py`; **do NOT use `from __future__ import annotations`** in this file — use `from typing_extensions import Annotated` for all Typer option/argument types (Art. I exception)

**Checkpoint**: `aurea extract` against a local test server produces valid theme files. Unit + integration tests pass independently.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and release readiness.

- [X] T058 [P] Create `tests/fixtures/expected_output.html`: run `aurea build` with fixture theme + sample slides; save output as known-good reference for future regression tests; add assertion in `test_build_e2e.py` that structural markers match
- [X] T059 [P] Create `docs/architecture.md`: document the build pipeline (parse → resolve → render → inline) with the ASCII diagram from CLAUDE.md; explain four distribution modes and how vendoring works
- [X] T060 [P] Create `docs/theme-system.md`: document DESIGN.md 9-section format with field descriptions; document CSS custom property mapping table; document registry.json schema
- [X] T061 [P] Create `docs/agent-commands.md`: document all 7 workflow phases with command signatures, what each prompt instructs the agent to do, placeholder reference table
- [X] T062 Run `quickstart.md` validation: follow all 10 steps manually; verify all 10 checklist items pass; record any deviations; **note**: Step 7 (aurea extract from live URLs) requires internet access and is optional — skip in offline/CI environments; all other 9 steps are mandatory and must pass
- [ ] T063 Four-mode distribution validation: build zipapp (`python -m zipapp`) and PyInstaller exe; run `aurea init` in each mode; confirm identical behavior; document in release notes
- [X] T064 [P] Update `README.md`: installation instructions for all 4 modes, quickstart example (init → build → serve), link to docs/

## Constitution Compliance Checklist

*Required before any PR targeting main. Verify all applicable gates:*

- [ ] Python 3.8 compatibility verified (`python3.8 -m pytest`)
- [ ] Feature tested in all four distribution modes (zero-install, zipapp, PyInstaller, pip)
- [ ] Generated HTML has no external `<link>`/`<script src>` references
- [ ] No new dependency added without justification in PR description
- [ ] reveal.js version unchanged (5.x)
- [ ] Coverage report shows ≥ 80% for `src/aurea/`
- [ ] `ruff check .` + `mypy src/` both pass with zero errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Requires Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Requires Phase 2 — no dependency on US2 or US3
- **US2 (Phase 4)**: Requires Phase 2 + US1 theme files (`src/aurea/themes/default/`, `registry.json`); note T029 specifically depends on T028 + T028a–T028d (all 5 original themes must be created before registry is built)
- **US3 (Phase 5)**: Requires Phase 2 + `_http.py` and `_regex.py` from Foundational
- **Polish (Phase 6)**: Requires US1 + US2 complete; US3 completion optional

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — DELIVERS independent MVP
- **US2 (P2)**: Can start after US1 delivers `src/aurea/themes/default/` and `registry.json`
- **US3 (P3)**: Can start after Foundational — only needs `_http.py`, `_regex.py`, `_tpl.py`

### Within Each User Story

1. Write tests FIRST — verify they FAIL
2. Implement in order: data (entities/config) → logic (services/extractors) → CLI (Typer command)
3. Run tests — verify they PASS
4. Commit with atomic message per task or logical group
5. Stop at checkpoint to validate story independently

---

## Parallel Execution Examples

### Phase 2 (Foundational) — all can run in parallel after Phase 1:

```
T010  commands/__init__.py
T010a exceptions.py         ← parallel
T011  _regex.py             ← parallel
T012  _tpl.py               ← parallel
T013  _http.py              ← parallel (requires T010a for AureaError)
T014  cli.py (stubs)
T015  vendor reveal.js      ← parallel
T016  fixtures/default_theme ← parallel
T017  fixtures/sample_slides ← parallel
```

### US1 Tests (both parallel):

```
T018 integration/test_init_e2e.py  ← parallel
T019 unit/test_init.py             ← parallel
```

### US1 Template creation (all parallel after T020, T021):

```
T022 agent_commands/claude/   ← parallel
T023 agent_commands/gemini/   ← parallel
T024a agent_commands/copilot/ ← parallel
T024b agent_commands/others/  ← parallel
```

### US3 Token extraction (parallel after T050):

```
T052 extract_typography_tokens  ← parallel
T053 extract_spacing/shadow     ← parallel
```

---

## Implementation Strategy

### MVP (US1 Only — Phases 1–3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Scaffolding)
4. **STOP**: Run `quickstart.md` Steps 1–3 manually
5. **SHIP MVP**: `aurea init` + prompt templates work in all 4 distribution modes

### Incremental Delivery

1. MVP shipped → US1 complete
2. Add US2 (Phases 4) → `aurea build`, `aurea serve`, `aurea theme` work → ship M2+M3
3. Add US3 (Phase 5) → `aurea extract` works → ship M4
4. Polish (Phase 6) → full release

### Parallel Team Strategy (if multiple developers)

1. Team completes Phases 1–2 together
2. Developer A: US1 (T018–T030)
3. Developer B: US3 (T047–T057) — only needs `_http.py`/`_regex.py` from Foundational
4. Developer A finishes → Developer B integrates into build pipeline (US2 depends on US1 theme files)
5. Developer A/B together: US2 (T031–T046)

---

## Summary

| Phase | Tasks | Story | Parallelizable |
|-------|-------|-------|----------------|
| Phase 1: Setup | T001–T009 (9) | — | T002–T009 (8) |
| Phase 2: Foundational | T010–T017 + T010a (9) | — | T010a, T011–T017 (8) |
| Phase 3: US1 (P1) | T018–T030 + T028a–T028d (18) | US1 | T018–T019, T022–T024b, T028a–T028d |
| Phase 4: US2 (P2) | T031–T046 (16) | US2 | T031–T034, T045 |
| Phase 5: US3 (P3) | T047–T057 (11) | US3 | T047–T048, T052–T053 |
| Phase 6: Polish | T058–T064 (7) | — | T058–T061, T064 |
| **Total** | **70 tasks** | | |

**MVP scope**: T001–T030d + T010a (35 tasks, Phases 1–3). Ships `aurea init` + 5 original themes + all 56 prompt templates.
