# Data Model: Aurea CLI and Presentation Toolkit

**Feature**: 001-aurea-cli-toolkit  
**Date**: 2026-04-08  

---

## Entities

### 1. ProjectConfig

Persisted as `.aurea/config.json` within each presentation project.

| Field         | Type     | Required | Description                                      |
|---------------|----------|----------|--------------------------------------------------|
| `agent`       | string   | yes      | Active AI agent id (e.g., `claude`, `gemini`)    |
| `theme`       | string   | yes      | Active theme id (e.g., `default`, `stripe`)      |
| `themes_dir`  | string   | yes      | Relative path to local themes dir (`.aurea/themes`) |
| `slides_dir`  | string   | yes      | Relative path to slides dir (`slides`)           |
| `output_dir`  | string   | yes      | Relative path to output dir (`output`)           |
| `version`     | string   | yes      | Aurea version that created this project          |

**Example**:
```json
{
  "agent": "claude",
  "theme": "default",
  "themes_dir": ".aurea/themes",
  "slides_dir": "slides",
  "output_dir": "output",
  "version": "0.1.0"
}
```

**Constraints**:
- `agent` MUST be one of the 8 known agent ids or `"generic"`
- `theme` MUST match an id in local or global registry
- All path values are relative to project root; no absolute paths stored

---

### 2. Theme

Persisted as a directory (`<themes_dir>/<theme-id>/`) with 4 required files.

| File         | Description                                                         |
|--------------|---------------------------------------------------------------------|
| `DESIGN.md`  | Human-readable + machine-parseable design system (9 sections)      |
| `theme.css`  | CSS custom properties for reveal.js theme variables                |
| `layout.css` | Grid system, animation presets, and layout utilities               |
| `meta.json`  | Searchable metadata (id, name, category, tags, mood, colors, etc.) |

**meta.json schema**:

| Field        | Type           | Required | Description                                     |
|--------------|----------------|----------|-------------------------------------------------|
| `id`         | string         | yes      | Unique slug (e.g., `stripe`, `midnight`)        |
| `name`       | string         | yes      | Display name (e.g., `Stripe`, `Midnight Blue`)  |
| `category`   | string         | yes      | Category slug (e.g., `fintech`, `devtools`)     |
| `tags`       | `List[string]` | yes      | Searchable tags (e.g., `["clean", "blue"]`)     |
| `mood`       | string         | yes      | Short mood description (≤100 chars)             |
| `colors`     | object         | yes      | Named color dict with at minimum `primary`, `background`, `text` |
| `typography` | object         | yes      | `heading` and `body` font-family strings        |
| `source`     | string         | no       | Origin URL or repo reference                    |
| `version`    | string         | no       | Theme version (defaults to `"1.0.0"`)           |

**Constraints**:
- `id` must be lowercase, alphanumeric + hyphens only; unique within registry
- `DESIGN.md` MUST have exactly 9 sections (validated before applying a theme)
- Theme directory names match `id` exactly

---

### 3. Registry

Persisted as `registry.json`. Two instances:
- **Global** (read-only): `src/aurea/themes/registry.json` — bundled with Aurea distribution
- **Local** (read-write): `.aurea/themes/registry.json` — per-project, may have additional extracted themes

| Field     | Type           | Required | Description                                     |
|-----------|----------------|----------|-------------------------------------------------|
| `version` | string         | yes      | Registry schema version (currently `"1.0.0"`)  |
| `sources` | `List[Source]` | yes      | Upstream sources with last sync timestamps      |
| `themes`  | `List[ThemeMeta]` | yes   | Flat array of all theme metadata entries        |

**Source object**:

| Field       | Type   | Required | Description                          |
|-------------|--------|----------|--------------------------------------|
| `repo`      | string | yes      | Source repository reference          |
| `last_sync` | string | yes      | ISO 8601 datetime of last sync       |

**ThemeMeta** in registry: same fields as `meta.json` plus:

| Field  | Type   | Required | Description                                   |
|--------|--------|----------|-----------------------------------------------|
| `path` | string | yes      | Relative path to theme directory from registry root |

**Resolution rule**: When resolving a theme id, local registry entries shadow global entries with the same id.

---

### 4. AgentConfig

In-memory only (not persisted). Defines per-agent output format for `aurea init`.

| Field             | Type   | Description                                          |
|-------------------|--------|------------------------------------------------------|
| `id`              | string | Agent identifier (e.g., `claude`)                   |
| `commands_dir`    | string | Relative path for command files (e.g., `.claude/commands`) |
| `file_format`     | string | File extension: `md`, `toml`, `agent.md`            |
| `arg_placeholder` | string | Argument placeholder token: `$ARGUMENTS` or `{{args}}` |

**Full AGENT_CONFIG table**:

| id        | commands_dir                        | file_format | arg_placeholder |
|-----------|-------------------------------------|-------------|-----------------|
| `claude`  | `.claude/commands`                  | `.md`       | `$ARGUMENTS`    |
| `gemini`  | `.gemini/commands`                  | `.toml`     | `{{args}}`      |
| `copilot` | `.github/copilot-instructions`      | `.agent.md` | `$ARGUMENTS`    |
| `windsurf`| `.windsurf/commands`                | `.md`       | `$ARGUMENTS`    |
| `devin`   | `.devin/commands`                   | `.md`       | `$ARGUMENTS`    |
| `chatgpt` | `.chatgpt/commands`                 | `.md`       | `$ARGUMENTS`    |
| `cursor`  | `.cursor/commands`                  | `.md`       | `$ARGUMENTS`    |
| `generic` | `commands` (or `--commands-dir`)    | `.md`       | `$ARGUMENTS`    |

---

### 5. PromptTemplate

Canonical in-source format (YAML frontmatter + Markdown body). Converted to agent-native format at `aurea init` time.

| Field         | Location    | Description                                     |
|---------------|-------------|-------------------------------------------------|
| `name`        | frontmatter | Template name (e.g., `aurea.outline`)           |
| `description` | frontmatter | One-line description shown in agent help        |
| `body`        | Markdown    | Template content with placeholder tokens        |

**7 standard templates** (one set per agent):

| Name             | Purpose                                            |
|------------------|----------------------------------------------------|
| `aurea.theme`    | Browse and select a theme for the presentation     |
| `aurea.outline`  | Generate narrative structure and slide plan        |
| `aurea.generate` | Create full Markdown presentation from outline     |
| `aurea.refine`   | Iteratively improve specific slides                |
| `aurea.visual`   | Generate SVG/CSS visual assets for marked slides   |
| `aurea.extract`  | Extract design system from a URL (Mode 1 fallback) |
| `aurea.build`    | Build standalone HTML from slides (Mode 1 fallback)|

---

### 6. Presentation (in-memory)

Parsed from `slides/presentation.md` during `aurea build`. Not persisted.

| Field      | Type           | Description                                    |
|------------|----------------|------------------------------------------------|
| `title`    | string         | Extracted from YAML frontmatter                |
| `author`   | string         | Extracted from YAML frontmatter                |
| `theme`    | string         | Frontmatter theme override (lowest precedence) |
| `slides`   | `List[Slide]`  | Ordered list of parsed slide objects           |

---

### 7. Slide (in-memory)

One parsed slide, split on `---` separator.

| Field        | Type           | Description                                       |
|--------------|----------------|---------------------------------------------------|
| `index`      | int            | Zero-based slide number                           |
| `markdown`   | string         | Raw Markdown content (without speaker notes)      |
| `html`       | string         | Rendered HTML (populated during build)            |
| `notes`      | string         | Speaker notes text (extracted from `Note:` block) |
| `attributes` | `Dict[str, str]`| reveal.js slide attributes from `<!-- .slide: -->`|
| `word_count` | int            | Word count of `markdown` (for ≤40-word validation)|

**Parsing rules**:
- Split on `^---$` (regex, newline-bounded)
- Extract `Note:` section at end of slide (everything after `\nNote:` or `\nNotes:`)
- Extract `<!-- .slide: ... -->` comment for `attributes`
- Empty slides (only whitespace after split) are skipped

---

### 8. DesignExtractor (in-memory)

Instantiated during `aurea extract`. Encapsulates the scraping + token extraction workflow.

| Attribute      | Type   | Description                                        |
|----------------|--------|----------------------------------------------------|
| `url`          | string | Target URL to scrape                               |
| `user_agent`   | string | HTTP User-Agent header (default: `Aurea/1.0`)      |
| `timeout`      | int    | Request timeout in seconds (default: 30)           |
| `delay`        | float  | Delay between page requests in seconds (default: 1)|
| `depth`        | int    | Crawl depth (default: 1)                           |
| `raw`          | bool   | Skip semantic interpretation if True               |

**Methods** (required by FR-023):

| Method                      | Returns            | Description                                   |
|-----------------------------|--------------------|-----------------------------------------------|
| `fetch_page(url)`           | `str`              | Fetch HTML, check robots.txt, apply timeout   |
| `extract_stylesheets(html)` | `List[str]`        | Return merged CSS text from `<style>` + `<link>` |
| `extract_color_tokens(css)` | `Dict[str, str]`   | Top hex colors ranked by frequency with roles |
| `extract_typography_tokens(css)` | `Dict[str, str]` | font-family + size by selector weight     |
| `extract_spacing_tokens(css)` | `Dict[str, str]` | Dominant margin/padding/gap values            |
| `extract_shadow_tokens(css)` | `List[str]`       | Unique `box-shadow` values                    |
| `generate_raw_design_md(tokens)` | `str`         | 9-section DESIGN.md from raw token dict       |
| `generate_theme_css(tokens)` | `str`             | reveal.js CSS custom properties from tokens   |
| `run()`                     | `Dict[str, Any]`   | Orchestrates full pipeline, returns paths     |

---

## Entity Relationships

```
ProjectConfig
  └── active_theme → Theme (resolved via Registry)
  └── agent → AgentConfig

Registry (global, read-only)
Registry (local, read-write)
  └── themes[] → Theme

Theme
  ├── meta.json   → ThemeMeta
  ├── DESIGN.md   → 9-section design spec
  ├── theme.css   → CSS custom properties
  └── layout.css  → grid + animations

Presentation
  └── slides[] → Slide (parsed from slides/presentation.md)

DesignExtractor
  └── produces → Theme (at .aurea/themes/<name>/)
  └── updates  → Registry (local)
```

---

## State Transitions

### Theme activation lifecycle:
1. `bundled` (in `src/aurea/themes/`) → read-only global
2. `init-copied` (copied to `.aurea/themes/<id>/` by `aurea init`) → local read-write
3. `active` (referenced in `config.json` as `active_theme`) → used by build
4. `extracted` (generated by `aurea extract`) → local read-write, can become `active`

### Build pipeline flow:
1. `markdown-raw` (slides/presentation.md) 
2. → `parsed` (split into Slide objects, frontmatter extracted)
3. → `html-fragments` (each slide rendered via mistune)
4. → `html-document` (Jinja2 + inlined CSS/JS)
5. → `standalone` (output/presentation.html — all external refs removed)

### Validation rules:
- A `Theme` transitions to `active` only if `DESIGN.md` has exactly 9 sections
- A `Slide` with `word_count > 40` emits a warning (not an error) during build
- A `Presentation` with no slides (empty after parsing) aborts build with an error
