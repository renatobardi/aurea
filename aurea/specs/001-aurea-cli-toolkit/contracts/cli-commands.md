# Contract: CLI Commands

**Feature**: 001-aurea-cli-toolkit  
**Date**: 2026-04-08  
**Type**: CLI Command Schema

This document defines the complete contract for all `aurea` CLI commands — their signatures, options, outputs, and error codes. Implementations MUST conform to this contract.

---

## Global Options

```
aurea [--version] [--help] <COMMAND>
```

| Option      | Type | Description                              |
|-------------|------|------------------------------------------|
| `--version` | flag | Print version string and exit (eager)    |
| `--help`    | flag | Show help text and exit                  |

**Output** (`--version`): `aurea 0.1.0` (stdout)  
**Exit codes**: `0` success, `1` user error (bad args), `2` internal error

---

## `aurea init`

Initialize a new presentation project.

```
aurea init [PROJECT_NAME] [OPTIONS]
```

### Arguments

| Name           | Required | Default | Description                                    |
|----------------|----------|---------|------------------------------------------------|
| `PROJECT_NAME` | no       | `.`     | Directory name for the new project. Omit with `--here` |

### Options

| Option           | Type   | Default   | Description                                             |
|------------------|--------|-----------|---------------------------------------------------------|
| `--agent`        | string | `claude`  | Target AI agent id                                      |
| `--theme`        | string | `default` | Initial theme id                                        |
| `--here`         | flag   | false     | Initialize in current directory (no subdirectory)       |
| `--force`        | flag   | false     | Overwrite `.aurea/` and commands dir if they exist      |
| `--no-git`       | flag   | false     | Skip `git init`                                         |
| `--commands-dir` | string | (auto)    | Override commands directory path (for `--agent generic`) |
| `--lang`         | string | `en`      | Language for generated prompt templates                 |

### Outputs

| Stream | Content                                                      |
|--------|--------------------------------------------------------------|
| stdout | Nothing (silent on success)                                  |
| stderr | Applied defaults line (if `--agent`/`--theme` omitted): `Using defaults: --agent claude --theme default` |
| stderr | Language fallback warning (if `--lang` unavailable): `Language 'pt-br' not available, using 'en'` |
| stderr | List of created files/dirs (one per line, prefixed `  +`)    |

### Created structure

```
<PROJECT_NAME>/
├── .aurea/
│   ├── config.json
│   └── themes/
│       ├── registry.json
│       └── <theme>/
│           ├── DESIGN.md
│           ├── theme.css
│           ├── layout.css
│           └── meta.json
├── <commands_dir>/          (e.g., .claude/commands/)
│   ├── aurea.theme.md
│   ├── aurea.outline.md
│   ├── aurea.generate.md
│   ├── aurea.refine.md
│   ├── aurea.visual.md
│   ├── aurea.extract.md
│   └── aurea.build.md
├── slides/
│   └── .gitkeep
├── output/
│   └── .gitkeep
└── README.md
```

### Error conditions

| Condition                             | Exit | Message                                              |
|---------------------------------------|------|------------------------------------------------------|
| Directory exists + no `--force`       | 1    | `Error: directory '<name>' already exists. Use --force to overwrite.` |
| Theme id not found                    | 1    | `Error: theme '<id>' not found. Run 'aurea theme search <id>' to find similar themes.` |
| Invalid agent id                      | 1    | `Error: unknown agent '<id>'. Valid agents: claude, gemini, copilot, windsurf, devin, chatgpt, cursor, generic` |

---

## `aurea build`

Compile `slides/presentation.md` into a standalone HTML presentation.

```
aurea build [OPTIONS]
```

### Options

| Option          | Type   | Default                   | Description                                          |
|-----------------|--------|---------------------------|------------------------------------------------------|
| `--input`       | path   | `slides/presentation.md`  | Source Markdown file                                 |
| `--output`      | path   | `output/presentation.html`| Output HTML file                                     |
| `--theme`       | string | (from config.json)        | Override active theme                                |
| `--minify`      | flag   | false                     | Minify HTML output (removes whitespace)              |
| `--watch`       | flag   | false                     | Watch for changes and rebuild automatically          |
| `--embed-fonts` | flag   | false                     | Inline web fonts as base64 data URIs                 |

### Outputs

| Stream | Content                                                     |
|--------|-------------------------------------------------------------|
| stdout | Path to output file: `output/presentation.html`             |
| stderr | Build summary: `Built 14 slides in 0.42s (312 KB)`          |
| stderr | Slide warnings: `Warning: slide 3 has 47 words (limit: 40)` |
| stderr | Watch mode: `Watching for changes... Press Ctrl+C to stop`  |

### Theme precedence (highest → lowest)

1. `--theme` CLI flag
2. `active_theme` in `.aurea/config.json`
3. `theme` field in Markdown YAML frontmatter

### Error conditions

| Condition                          | Exit | Message                                                       |
|------------------------------------|------|---------------------------------------------------------------|
| Input file not found               | 1    | `Error: input file '<path>' not found`                        |
| No active theme                    | 1    | `Error: no theme set. Run 'aurea theme use <id>' first`       |
| Theme files missing/corrupt        | 1    | `Error: theme '<id>' DESIGN.md missing or invalid (needs 9 sections)` |
| Empty presentation (no slides)     | 1    | `Error: no slides found in '<path>'. Check '---' separators`  |

---

## `aurea serve`

Start a local HTTP server to preview the presentation.

```
aurea serve [OPTIONS]
```

### Options

| Option    | Type   | Default     | Description                                              |
|-----------|--------|-------------|----------------------------------------------------------|
| `--port`  | int    | `8000`      | Preferred port (tries sequential ports if occupied)      |
| `--host`  | string | `127.0.0.1` | Bind address (use `0.0.0.0` for LAN access)              |
| `--watch` | flag   | false       | Rebuild on file changes and auto-reload browser          |
| `--input` | path   | `output/presentation.html` | HTML file to serve                        |

### Outputs

| Stream | Content                                                     |
|--------|-------------------------------------------------------------|
| stdout | `Serving at http://127.0.0.1:8000 — press Ctrl+C to stop`  |
| stderr | Port conflicts: `Port 8000 in use, trying 8001...`          |
| stderr | Rebuild events: `Rebuilt in 0.38s (watching...)`            |

### Error conditions

| Condition                     | Exit | Message                                              |
|-------------------------------|------|------------------------------------------------------|
| No HTML file to serve         | 1    | `Error: '<path>' not found. Run 'aurea build' first` |
| All ports 8000–8100 occupied  | 1    | `Error: no available port in range 8000–8100`        |

---

## `aurea theme` (sub-group)

### `aurea theme list`

```
aurea theme list [OPTIONS]
```

| Option     | Type   | Default  | Description                                 |
|------------|--------|----------|---------------------------------------------|
| `--format` | string | `table`  | Output format: `table` or `json`            |

**Output**: Table or JSON array of all themes from registry. Columns: `ID`, `Name`, `Category`, `Mood` (truncated to 40 chars), `Colors`.

---

### `aurea theme search`

```
aurea theme search QUERY [OPTIONS]
```

| Name       | Required | Description                              |
|------------|----------|------------------------------------------|
| `QUERY`    | yes      | Search string (searched across id, name, tags, mood, category) |

| Option       | Type   | Default | Description                              |
|--------------|--------|---------|------------------------------------------|
| `--category` | string | none    | Filter by category slug                  |
| `--tag`      | string | none    | Filter by tag (can specify multiple)     |
| `--format`   | string | `table` | Output format: `table` or `json`         |

**Output**: Table or JSON array of 3–10 matching themes ordered by relevance.

---

### `aurea theme info`

```
aurea theme info THEME_ID
```

**Output**: Full metadata for theme including terminal color swatches (Rich `[color]` formatting), typography, mood, source.

**Error**: Theme not found → `Error: theme '<id>' not found` (exit 1)

---

### `aurea theme show`

```
aurea theme show THEME_ID
```

**Output**: Full DESIGN.md content of the theme, printed with syntax highlighting (Markdown).

---

### `aurea theme use`

```
aurea theme use THEME_ID
```

**Output** (stderr): `Theme 'linear' applied. Config updated.`  
**Effect**: Copies theme files to `.aurea/themes/<id>/`; updates `config.json`.

**Error conditions**:

| Condition         | Exit | Message                                                                    |
|-------------------|------|----------------------------------------------------------------------------|
| Theme not found   | 1    | `Error: theme '<id>' not found. Try 'aurea theme search <id>'`             |
| Not in project    | 1    | `Error: not in an Aurea project directory (no .aurea/config.json found)`   |

---

### `aurea theme create`

```
aurea theme create THEME_NAME [OPTIONS]
```

| Option     | Type   | Default | Description                                  |
|------------|--------|---------|----------------------------------------------|
| `--output` | path   | `.aurea/themes/<name>/` | Where to create the theme scaffold |

**Effect**: Creates annotated scaffold with empty DESIGN.md (9 sections with guide comments), CSS skeleton, meta.json stub.

---

## `aurea extract`

Extract a design system from a URL and save it as a reusable theme.

```
aurea extract URL [OPTIONS]
```

### Arguments

| Name  | Required | Description         |
|-------|----------|---------------------|
| `URL` | yes      | Public URL to scrape |

### Options

| Option         | Type   | Default    | Description                                               |
|----------------|--------|------------|-----------------------------------------------------------|
| `--name`       | string | (derived)  | Output theme id/directory name                            |
| `--depth`      | int    | `1`        | Crawl depth (1 = main page only; 2 = + linked pages)     |
| `--raw`        | flag   | false      | Skip semantic token interpretation; output raw tokens     |
| `--use`        | flag   | false      | Apply extracted theme to current project after extraction |
| `--timeout`    | int    | `30`       | HTTP request timeout in seconds                           |
| `--user-agent` | string | `Aurea/1.0`| HTTP User-Agent header                                    |
| `--delay`      | float  | `1.0`      | Delay in seconds between page requests (for `--depth > 1`)|

### Outputs

| Stream | Content                                                                          |
|--------|----------------------------------------------------------------------------------|
| stdout | Extraction summary: `Extracted theme 'linear-custom' → .aurea/themes/linear-custom/` |
| stdout | Token summary: colors extracted (N), fonts detected (M), mood: <inferred>        |
| stderr | Progress: `Fetching https://linear.app...`, `Processing CSS (3 sheets)...`       |

### Error conditions

| Condition                    | Exit | Message                                                              |
|------------------------------|------|----------------------------------------------------------------------|
| robots.txt blocks URL        | 1    | `Error: https://... is disallowed by robots.txt`                     |
| Timeout                      | 1    | `Error: request timed out after 30s. Try --timeout 60`               |
| 403 Forbidden                | 1    | `Error: HTTP 403 forbidden — site may require authentication`        |
| 404 Not Found                | 1    | `Error: HTTP 404 — URL not found`                                    |
| `--name` not provided        | 1    | `Error: --name is required when not in a project directory`          |
| CSS-in-JS detected (warning) | 0    | `Warning: CSS-in-JS detected — extracted tokens may be incomplete. Manual refinement recommended.` |

---

## Exit Code Summary

| Code | Meaning                                      |
|------|----------------------------------------------|
| `0`  | Success                                      |
| `1`  | User error (invalid args, not found, etc.)   |
| `2`  | Internal / unexpected error                  |

---

## Standard Streams Contract

| Stream | Content                                                     |
|--------|-------------------------------------------------------------|
| stdout | Machine-readable output (paths, JSON, version strings) — safe to pipe |
| stderr | Human-readable progress, warnings, applied-defaults notices |

This separation ensures `aurea build | some-tool` works correctly without being polluted by log messages.
