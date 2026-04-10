# Feature Specification: Aurea CLI and Presentation Toolkit

**Feature Branch**: `001-aurea-cli-toolkit`
**Created**: 2026-04-08
**Status**: Draft

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Scaffolding and AI-Guided Presentation Creation (Priority: P1)

As a developer or tech lead who uses AI agents daily,
I want to initialize a presentation project with `aurea init`, have prompt templates automatically
installed in my AI agent, and create a complete presentation following the guided workflow
(theme → outline → generate → refine → visual → build),
so that I produce high-quality presentations with structured narrative, consistent design system,
and standalone HTML output — without needing to know CSS, reveal.js, or design.

**Why this priority**: Core value proposition. All other features depend on this foundation.

**Independent Test**: Run `aurea init my-presentation --agent claude --theme default`, execute
the 7 workflow commands in sequence, and verify `output/presentation.html` opens offline in a
browser.

**Acceptance Scenarios**:

1. **Given** Aurea is installed in any mode, **When** `aurea init my-talk --agent claude
   --theme stripe` runs, **Then** `my-talk/` is created with `.aurea/config.json`,
   `.aurea/themes/stripe/` (DESIGN.md, theme.css, layout.css, meta.json),
   `.aurea/themes/registry.json`, `.claude/commands/` with 7 `.md` files, `slides/`,
   `output/`, and `README.md`; git is initialized unless `--no-git` is passed.

2. **Given** `aurea init project --agent gemini`, **When** init completes, **Then** the 7
   prompt templates are in `.gemini/commands/` in `.toml` format with `{{args}}` placeholders.

3. **Given** `aurea init . --here --agent claude` in an existing directory, **When** init
   completes, **Then** structure is created in place without a subdirectory; existing files
   are not overwritten unless `--force` is passed.

4. **Given** a project with the stripe theme, **When** `/aurea.outline "Microservices for CTOs"`
   runs, **Then** the agent reads `.aurea/config.json`, loads stripe's DESIGN.md, and generates
   `slides/outline.md` with audience, narrative arc (opening → development → climax → conclusion),
   slide list with estimated timing, and visual constraints referencing the design system.

5. **Given** a completed outline, **When** `/aurea.generate` runs, **Then**
   `slides/presentation.md` is created with reveal.js syntax (`---` separators, `Note:` speaker
   notes, `<!-- .slide: -->` attributes), ≤40 words per slide body, theme colors/typography
   applied, and `<!-- VISUAL: description -->` markers on slides needing assets.

6. **Given** a generated presentation, **When** `/aurea.build` runs, **Then** `aurea build`
   executes (or agent generates inline HTML in Mode 1) and produces `output/presentation.html`
   with all CSS and JS inlined and zero external resource references.

---

### User Story 2 — Theme Library, Search, and Build Pipeline (Priority: P2)

As a developer creating presentations,
I want to browse a library of 40+ themes based on real design systems, search by mood/category/tag,
apply themes to my project, and compile my Markdown into standalone HTML with the applied theme,
so that my presentations have professional visual identity that works offline in any browser.

**Why this priority**: Themes are the quality differentiator. Without them, output is generic.

**Independent Test**: Run `aurea theme list`, `aurea theme search "dark"`, `aurea theme use
linear`, `aurea build`, then verify output HTML opens offline with correct styling.

**Acceptance Scenarios**:

1. **Given** the registry contains all themes, **When** `aurea theme list` runs, **Then** a
   table shows id, name, category, mood (truncated), and primary colors for all 36+ themes.

2. **Given** all themes are indexed, **When** `aurea theme search "dark minimal elegant"` runs,
   **Then** 3–10 results are returned ordered by relevance, with `--category`, `--tag`, and
   `--format table|json` filters supported.

3. **Given** an active project, **When** `aurea theme use linear` runs, **Then**
   `linear/` (DESIGN.md, theme.css, layout.css, meta.json) is copied to `.aurea/themes/linear/`,
   `config.json` is updated with `active_theme: linear`, and local `registry.json` reflects the
   change.

4. **Given** `slides/presentation.md` and an active theme in `config.json`, **When**
   `aurea build` runs, **Then** the pipeline parses YAML frontmatter → resolves theme CSS →
   splits slides on `---` → converts each to HTML → renders via Jinja2 with reveal.js 5.x and
   theme CSS inlined → writes `output/presentation.html`. Output MUST have zero
   `<link href="https://...">` or `<script src="https://...">` and MUST open offline in
   Chrome, Firefox, Safari, and Edge.

5. **Given** `aurea build --watch` is running, **When** any file in `slides/` or
   `.aurea/themes/` changes, **Then** build triggers automatically and reports build time
   to stderr.

6. **Given** `aurea serve`, **When** a browser opens the local URL, **Then**
   `output/presentation.html` is served; combined with `--watch`, the page reloads on rebuild.

7. **Given** the import script runs, **When** it processes `VoltAgent/awesome-design-md`,
   **Then** each design is transformed into a complete Aurea theme (meta.json + theme.css +
   layout.css) and `registry.json` is updated.

---

### User Story 3 — Theme Extraction via Web Scraping (Priority: P3)

As a developer who wants a specific site's visual identity in their presentation,
I want to extract the design system from any public URL via `aurea extract` and save it as a
reusable theme,
so that I can use any brand's visual identity without manually rebuilding the design system.

**Why this priority**: Valuable differentiator but non-blocking — users can work with bundled
themes while this is unavailable.

**Independent Test**: Run `aurea extract https://linear.app --name linear-custom` and verify
`.aurea/themes/linear-custom/` contains all four required files with real tokens from that site.

**Acceptance Scenarios**:

1. **Given** a reachable URL, **When** `aurea extract https://linear.app --name linear-custom`
   runs, **Then** the pipeline: fetches HTML + CSS (respecting robots.txt) → extracts color,
   typography, spacing, shadow, and border-radius tokens → filters third-party CDN CSS →
   generates 9-section DESIGN.md, theme.css, layout.css, meta.json → saves to
   `.aurea/themes/linear-custom/` → updates local registry. A summary of extracted tokens
   and inferred mood is printed to stdout.

2. **Given** `--depth 2`, **When** extraction runs, **Then** up to 2 levels of internal pages
   are crawled and tokens are aggregated.

3. **Given** `--raw`, **When** extraction runs, **Then** DESIGN.md contains raw tokens without
   semantic interpretation — usable but requiring manual refinement.

4. **Given** `--use`, **When** extraction completes, **Then** `config.json` is updated to
   set the extracted theme as active.

5. **Given** Mode 1 (zero-install), **When** `/aurea.extract "https://cal.com, name: cal-design"`
   runs, **Then** the AI agent uses its native web fetch and generates DESIGN.md + theme.css
   directly in the project.

---

### Edge Cases

- `aurea init` in existing directory: Without `--force` → abort with clear message. With
  `--force` → overwrite `.aurea/` and commands directories but NOT `slides/` (preserve user work).
- Theme not found: `aurea theme use xyz` → "theme 'xyz' not found" + suggest
  `aurea theme search xyz` + list 3 most similar themes.
- Malformed Markdown in build: No `---` separator → treat as single slide. Invalid frontmatter
  → use defaults. Special characters → escape correctly for HTML.
- URL unreachable in extract: Timeout → clear message with `--timeout` suggestion.
  403/404 → specific message. robots.txt blocking → warn and abort.
- CSS-in-JS sites (Tailwind, Styled Components): Extract produces best-effort result and warns
  that manual or AI-assisted refinement is recommended.
- Port 8000 occupied: Try 8001, 8002... until available; display chosen port.
- Corrupted DESIGN.md: Validate 9-section structure before applying; if invalid, warn and
  suggest `aurea theme create` to recreate.
- Build theme precedence: `--theme` CLI flag > `config.json` > Markdown frontmatter.
- Registry resolution: Local `.aurea/themes/` registry resolves before global bundled registry.

---

## Requirements *(mandatory)*

### Functional Requirements

**P1 — Scaffolding and AI Workflow**

- **FR-001**: `aurea init` MUST create: `.aurea/config.json`, `.aurea/themes/<theme>/`
  (DESIGN.md, theme.css, layout.css, meta.json), `.aurea/themes/registry.json`, agent commands
  directory with 7 prompt files, `slides/`, `output/`, and `README.md`.
- **FR-002**: `aurea init` MUST accept: `<project-name>`, `--agent` (optional, default: `claude`),
  `--theme` (optional, default: `default`), `--here`, `--force`, `--no-git`, `--commands-dir`,
  `--lang`. When `--agent` or `--theme` are omitted, the applied defaults MUST be reported on
  stderr (e.g., `Using defaults: --agent claude --theme default`). When `--lang` specifies an
  unavailable language, MUST fall back to `en` and report on stderr:
  `Language '<lang>' not available, using 'en'`. **Scope note (v1)**: Only English (`en`) prompt
  templates are shipped in v1. The `--lang` flag is accepted for forward compatibility; any value
  other than `en` triggers the fallback. Full i18n is out of scope for v1 (see Assumptions).
- **FR-003**: The 7 prompt templates MUST be converted to each agent's native format per
  AGENT_CONFIG: Claude (`.md`, `$ARGUMENTS`), Gemini (`.toml`, `{{args}}`), Copilot
  (`.agent.md`, `$ARGUMENTS`), others (`.md`).
- **FR-004**: Each prompt template MUST use YAML frontmatter + Markdown body as canonical format.
- **FR-005**: Prompt templates MUST enforce 7 principles: load context first, respect design
  system, mandatory narrative arc, ≤40 words per slide body, first-class speaker notes,
  visual-first, theme do's/don'ts compliance.
- **FR-006**: All placeholders (`{{DESIGN_MD_PATH}}`, `{{THEME_CSS_PATH}}`, `{{CONFIG_PATH}}`,
  `{{REGISTRY_PATH}}`, `{{SLIDES_DIR}}`, `{{OUTPUT_DIR}}`, `$ARGUMENTS`) MUST be substituted
  at init time.
- **FR-007**: `config.json` MUST contain: selected agent, active theme, relative paths for
  themes and slides directories.
- **FR-008**: `aurea init` MUST copy the selected theme's four files to `.aurea/themes/<theme>/`.

**P2 — Theme System and Build**

- **FR-009**: `aurea theme list` MUST display all themes from registry with id, name, category,
  mood, and primary colors.
- **FR-010**: `aurea theme search` MUST perform fulltext search across name, tags, mood, and
  category; MUST accept `--category`, `--tag`, `--format table|json`.
- **FR-011**: `aurea theme info` MUST show full metadata with terminal color swatches.
  `aurea theme show` MUST print the complete DESIGN.md with syntax highlighting.
- **FR-012**: `aurea theme use` MUST copy theme to `.aurea/themes/` and update `config.json`.
- **FR-013**: `aurea theme create` MUST scaffold theme with annotated 9-section DESIGN.md,
  theme.css skeleton with CSS custom properties, layout.css defaults, meta.json.
- **FR-014**: `aurea build` MUST execute pipeline: parse YAML frontmatter → resolve theme →
  split on `---` → Markdown-to-HTML per slide (via mistune) → Jinja2 render with reveal.js 5.x
  and theme CSS inlined → produce single HTML file.
- **FR-015**: Generated HTML MUST be 100% standalone: reveal.js 5.x, CSS, and fonts inlined;
  zero external resource references.
- **FR-016**: `aurea build --watch` MUST monitor `slides/` and `.aurea/themes/` via watchdog
  and trigger rebuild on changes.
- **FR-017**: `aurea serve` MUST bind to `127.0.0.1` by default (localhost only); MUST accept
  `--host` to override the bind address (e.g., `--host 0.0.0.0` for LAN access). MUST start
  at an available port (default 8000) with auto-reload when combined with `--watch`.
- **FR-018**: `registry.json` MUST contain: `version`, `sources` (with `repo` and `last_sync`),
  and `themes` array (id, name, category, tags, mood, colors, typography, path).
- **FR-019**: The import script MUST transform each `VoltAgent/awesome-design-md` design into
  a complete Aurea theme (meta.json + theme.css + layout.css).
- **FR-020**: Every theme's DESIGN.md MUST follow the 9-section format: visual theme, color
  palette, typography, components, layout, depth, do's/don'ts, responsive, agent prompt guide.
- **FR-021**: `aurea build` MUST accept: `--input`, `--output`, `--theme` (override),
  `--minify`, `--watch`, `--embed-fonts`.

**P3 — Theme Extraction**

- **FR-022**: `aurea extract <url>` MUST accept: `--name`, `--depth` (default 1), `--raw`,
  `--use`, `--timeout` (default 30s), `--user-agent` (default `Aurea/1.0`), `--delay`
  (default 1s). When `--depth > 1`, a delay of `--delay` seconds MUST be applied between
  each page request to avoid rate limiting.
- **FR-023**: `DesignExtractor` class MUST implement: `fetch_page()`, `extract_stylesheets()`,
  `extract_color_tokens()`, `extract_typography_tokens()`, `extract_spacing_tokens()`,
  `extract_shadow_tokens()`, `generate_raw_design_md()`, `generate_theme_css()`, `run()`.
- **FR-024**: Extractor MUST filter CSS from known CDNs (Google Fonts, unpkg, cdnjs, jsdelivr).
- **FR-025**: Extractor MUST respect `robots.txt` and use the configurable timeout.
- **FR-026**: Extractor MUST group colors by frequency and assign semantic roles: primary,
  secondary, background, surface, text, accent.
- **FR-027**: Extractor MUST generate DESIGN.md compliant with the 9-section standard format.
- **FR-028**: `/aurea.extract` prompt template MUST function as a Mode 1 fallback.

### Key Entities

- **Project**: Presentation workspace. Contains `.aurea/config.json`, theme directory, agent
  commands, `slides/`, `output/`.
- **Theme**: Named design system with 4 files: DESIGN.md (9 sections), theme.css (CSS custom
  properties), layout.css (grid + animations), meta.json (search metadata).
- **Registry**: JSON index of themes. Exists globally (bundled, read-only) and locally
  (per project, writable). Local resolves before global.
- **Prompt Template**: One of 7 structured AI commands. Format and placeholders vary by agent.
- **Agent Config**: Per-agent definition of commands directory, file format, and argument
  placeholder.
- **Presentation**: `slides/presentation.md` — Markdown with YAML frontmatter, `---` separators,
  `Note:` speaker notes, `<!-- .slide: -->` reveal.js attributes.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

**P1 — Scaffolding and AI Workflow**

- **SC-001**: `aurea init project --agent claude --theme default` completes in under 2 seconds
  on any supported platform.
- **SC-002**: All 7 generated prompt templates execute without manual editing in the target agent.
- **SC-003**: The complete workflow (outline → generate → refine → visual → build) produces a
  functional standalone HTML presentation using the selected theme.
- **SC-004**: `aurea init` produces correct output in all 4 distribution modes.

**P2 — Theme System and Build**

- **SC-005**: `aurea theme list` displays 36+ themes readable in an 80-column terminal.
- **SC-006**: `aurea theme search "dark"` returns relevant results in under 500ms.
- **SC-007**: `aurea build` produces HTML that opens correctly offline in Chrome, Firefox,
  Safari, and Edge.
- **SC-008**: Generated HTML is 200KB–500KB without `--embed-fonts`, or 500KB–2MB with it.
- **SC-009**: `aurea serve` starts and serves the presentation in under 1 second.
- **SC-010**: The import pipeline processes 31+ themes from `awesome-design-md` without errors.

**P3 — Theme Extraction**

- **SC-011**: `aurea extract` successfully extracts a usable theme from at least 5 distinct URLs
  (linear.app, stripe.com, vercel.com, notion.so, cal.com) without errors.
- **SC-012**: Generated DESIGN.md has all 9 sections filled with real tokens from the target site.
- **SC-013**: Generated theme.css produces a visually coherent presentation with `aurea build`.
- **SC-014**: Extraction completes in under 30 seconds for typical sites at depth 1.

---

## Clarifications

### Session 2026-04-08

- Q: Quando `aurea init myproject` é executado sem `--agent` e `--theme`, o que acontece? → A: Usa defaults silenciosos `--agent claude --theme default`; exibe no stderr uma linha informando quais defaults foram aplicados.
- Q: O extrator aplica rate limiting entre requisições ao fazer crawl com `--depth > 1`? → A: Delay fixo entre requisições com flag `--delay` (default: 1 segundo) para evitar bloqueio pelos servidores alvo.
- Q: Quando o sync de temas (`3-sync-themes.yml`) falha por indisponibilidade do upstream, o workflow deve falhar? → A: Falha silenciosa — loga aviso no CI, mantém os temas existentes no repo, não falha o workflow.
- Q: Por padrão, `aurea serve` vincula em qual endereço de rede? → A: `127.0.0.1` por padrão (somente localhost); aceita flag `--host` para expor em outras interfaces (ex: `0.0.0.0` para LAN).
- Q: Quando `--lang pt-br` é solicitado mas não há tradução disponível, o que acontece? → A: Fallback silencioso para inglês (`en`); exibe aviso no stderr: `Language 'pt-br' not available, using 'en'`.

---

## Assumptions

- **Target audience**: Developers and tech leads using AI agents in the terminal, comfortable
  with CLI but without expectation of complex toolchains.
- **Primary environment**: Corporate Windows (~80%) with installation restrictions; Python 3.8+
  may or may not be available.
- **Connectivity**: Theme extraction requires internet; generated HTML is 100% offline-capable.
- **reveal.js**: Version 5.x is stable for the Aurea v1 lifecycle.
- **awesome-design-md**: `VoltAgent/awesome-design-md` remains public and active. If the sync
  workflow (`3-sync-themes.yml`) cannot reach the upstream repo, it logs a warning and exits
  successfully — existing bundled themes are preserved and no release is blocked.
- **Agent formats**: Command formats for Claude (`.md`), Gemini (`.toml`), Copilot (`.agent.md`)
  are stable for v1.
- **Runtime dependencies**: core — `typer`, `jinja2`, `mistune`, `rich`, `watchdog`, `pyyaml`;
  extract (optional) — `httpx`, `beautifulsoup4`, `cssutils`, `lxml`.
- **Out of scope for v1**: Full i18n, PDF export, remote presenter mode, theme marketplace,
  Mermaid rendering. These are Milestone 6 (post-v1).
- **Testing**: pytest + pytest-cov, 80% minimum coverage. Integration tests use real temp
  directories — no mocks for the build pipeline.
