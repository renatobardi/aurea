# Research: Aurea CLI and Presentation Toolkit

**Feature**: 001-aurea-cli-toolkit  
**Date**: 2026-04-08  
**Phase**: 0 — Technology decisions and integration patterns

---

## 1. CLI Framework: Typer + Python 3.8

**Decision**: `typer[all]>=0.9.0,<0.21`  
**Rationale**: Python 3.8 support was dropped in typer 0.21+. Cap at `<0.21` to guarantee compatibility with the corporate Windows baseline.

**Python 3.8 gotchas** (non-negotiable fixes):
- Do NOT use `from __future__ import annotations` together with `Annotated` — known bug on Python 3.8 causes runtime errors
- Use `from typing_extensions import Annotated` (not `typing.Annotated`, which is Python 3.9+)
- Use `typing.List[str]`, `typing.Dict[str, str]`, `typing.Optional[X]`, `typing.Union[A, B]` — never built-in generics like `list[str]` or `dict[str, str]`
- No walrus operator (`:=`), no `match/case`, no `X | Y` union syntax

**App structure**:
```
src/aurea/cli.py            ← main Typer app + --version callback
src/aurea/commands/
  init.py                   ← aurea init
  build.py                  ← aurea build
  serve.py                  ← aurea serve
  theme.py                  ← aurea theme (sub-group: list, search, use, info, show, create)
  extract.py                ← aurea extract
```

**Key patterns**:
- `app = typer.Typer()` in `cli.py`; `theme_app = typer.Typer()` added as `app.add_typer(theme_app, name="theme")`
- `--version` with `is_eager=True` in `@app.callback()`
- All CLI output (`typer.echo`, `rich.print`) → stdout; all logging (`_log.py`) → stderr via `Console(stderr=True)`
- Entry point: `aurea = aurea.cli:app` (absolute import, no relative imports — required for PyInstaller)

**Alternatives considered**:
- `click` directly: Rejected — Typer's type-based interface is cleaner and reduces boilerplate; both wrap click anyway
- `argparse`: Rejected — no sub-group support, more verbose

---

## 2. Presentation Engine: reveal.js 5.x Vendoring

**Decision**: Vendor reveal.js 5.x `dist/` folder in `src/aurea/vendor/revealjs/`; inline all assets at build time.

**Files to vendor** (minimal bundle ~100KB):
```
src/aurea/vendor/revealjs/
  dist/
    reveal.js          ← main library (~60KB minified)
    reveal.css         ← core styles (~20KB)
    reset.css          ← browser resets
  plugin/
    markdown.mjs       ← slide separator + Markdown rendering (REQUIRED)
    highlight.mjs      ← syntax highlighting (REQUIRED)
    notes.mjs          ← speaker notes (STANDARD)
    zoom.mjs           ← alt+click zoom (OPTIONAL)
```

**HTML skeleton** (produced by `src/aurea/templates/reveal.html.j2`):
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ title }}</title>
  <style>/* reset.css inlined */</style>
  <style>/* reveal.css inlined */</style>
  <style>/* theme.css inlined (CSS custom properties from DESIGN.md) */</style>
  <style>/* layout.css inlined */</style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      {% for slide in slides %}
      <section>{{ slide.html | safe }}</section>
      {% endfor %}
    </div>
  </div>
  <script>/* reveal.js inlined */</script>
  <script>/* plugin/markdown.mjs inlined */</script>
  <script>/* plugin/highlight.mjs inlined */</script>
  <script>/* plugin/notes.mjs inlined */</script>
  <script>
    Reveal.initialize({
      hash: true,
      plugins: [RevealMarkdown, RevealHighlight, RevealNotes]
    });
  </script>
</body>
</html>
```

**CSS custom properties** (DESIGN.md tokens map to these reveal.js variables):

| reveal.js variable        | DESIGN.md token           |
|---------------------------|---------------------------|
| `--r-background-color`    | Background / bg           |
| `--r-main-color`          | Text color                |
| `--r-main-font`           | Body font-family          |
| `--r-main-font-size`      | Base font size (42px def) |
| `--r-heading-color`       | Heading color             |
| `--r-heading-font`        | Heading font-family       |
| `--r-heading-font-weight` | Heading weight            |
| `--r-heading1-size`       | H1 size                   |
| `--r-link-color`          | Link / accent color       |
| `--r-selection-background-color` | Selection highlight |

**Alternatives considered**:
- Impress.js: Rejected — less popular, fewer themes, no speaker notes standard
- Slidev: Rejected — Node.js dependency violates zero-install + Python-only constraint
- Custom CSS/JS: Rejected — reveal.js is the established standard for this use case

---

## 3. Markdown-to-HTML Pipeline: mistune 2.x

**Decision**: `mistune>=2.0.5,<3.1` — Python 3.8 compatible, zero extra dependencies.

**API pattern**:
```python
import mistune
from mistune import HTMLRenderer

class SlideRenderer(HTMLRenderer):
    pass  # override block_code() for Pygments highlighting if needed

md = mistune.create_markdown(renderer=SlideRenderer())
html_fragment = md(slide_markdown_text)
```

**Key properties**:
- `create_markdown()` returns fragments, not full HTML documents — correct for per-slide rendering
- HTML comments (`<!-- .slide: ... -->`) pass through unchanged — no post-processing needed
- Speaker notes (`Note:` lines) must be pre-extracted before passing to mistune (regex split on `\nNote:`)
- `mistune.html(text)` is the one-liner for simple conversion without a custom renderer

**Inlining strategy** (build pipeline):
- CSS: read file → wrap in `<style>...</style>` → inject into Jinja2 template context
- JS (reveal.js): read file → wrap in `<script>...</script>` → inject into Jinja2 template context
- Fonts (`--embed-fonts`): `base64.b64encode(open(font_file, 'rb').read())` → `data:font/woff2;base64,...` URI in inlined CSS
- External link stripping (post-render guard): `re.sub(r'<(link|script)[^>]+https?://[^>]*>', '', html)`

**Alternatives considered**:
- `markdown` (stdlib-ish, via `markdown` package): Rejected — extension API is more complex; mistune is simpler and lighter
- `commonmark`: Rejected — larger dependency, no advantage for this use case

---

## 4. Web Scraping: httpx + BeautifulSoup + cssutils

**Decision**: `httpx>=0.25` (sync client), `beautifulsoup4>=4.12` with `lxml` backend, `cssutils>=2.10` for CSS token extraction.

**robots.txt check** (Python stdlib, no extra deps):
```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

def is_allowed(url: str, user_agent: str = "Aurea/1.0") -> bool:
    parsed = urlparse(url)
    rp = RobotFileParser()
    rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True  # If robots.txt unreachable, assume allowed
```

**httpx sync pattern**:
```python
import httpx

with httpx.Client(follow_redirects=True) as client:
    resp = client.get(url, headers={"User-Agent": user_agent}, timeout=timeout)
    resp.raise_for_status()
    return resp.text
```
- `TimeoutException` → clear message with `--timeout` hint
- `HTTPStatusError` with 403/404 → specific message; other codes → re-raise
- Delay between pages: `time.sleep(delay)` (stdlib; no async needed)

**CDN filter list** (exact domains to skip):
```python
CDN_DOMAINS = {
    "fonts.googleapis.com", "fonts.gstatic.com",
    "unpkg.com", "cdnjs.cloudflare.com", "cdn.jsdelivr.net",
}
```

**Color frequency analysis**:
```python
import re
from collections import Counter

HEX_RE = re.compile(r'#[0-9a-fA-F]{6}\b')

def count_hex_colors(css_text: str) -> Counter:
    return Counter(c.lower() for c in HEX_RE.findall(css_text))
```
Top-N colors by frequency → assign semantic roles: index 0→background, 1→text, 2→primary, 3→secondary, 4+→accent.

**Alternatives considered**:
- `requests` instead of `httpx`: Rejected — httpx is already in core deps; both are sync-capable; httpx is more modern
- `selenium`/`playwright` for JS-rendered sites: Rejected — violates minimal deps (Art. VII); best-effort extraction documented in edge cases
- `tinycss2` instead of `cssutils`: Rejected — cssutils has more complete W3C support for property-level parsing

---

## 5. File Watching: watchdog

**Decision**: `watchdog>=3.0` — Python 3.8 compatible, cross-platform (Windows/macOS/Linux).

**Pattern**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            rebuild()

observer = Observer()
observer.schedule(BuildHandler(), path="slides/", recursive=False)
observer.schedule(BuildHandler(), path=".aurea/themes/", recursive=True)
observer.start()
```
- Watch `slides/` and `.aurea/themes/` directories
- Debounce: skip rebuilds if last rebuild was <500ms ago (prevents duplicate triggers)
- Build time reported to stderr: `Built in 0.42s → output/presentation.html`

---

## 6. Theme Registry: JSON Schema

**Decision**: `registry.json` is the single index file; local registry resolves before global.

**Schema**:
```json
{
  "version": "1.0.0",
  "sources": [
    {
      "repo": "VoltAgent/awesome-design-md",
      "last_sync": "2026-04-08T00:00:00Z"
    }
  ],
  "themes": [
    {
      "id": "stripe",
      "name": "Stripe",
      "category": "fintech",
      "tags": ["clean", "professional", "blue"],
      "mood": "Confident, minimal, trustworthy",
      "colors": {
        "primary": "#635BFF",
        "background": "#FFFFFF",
        "text": "#0A2540"
      },
      "typography": {
        "heading": "Camphor, sans-serif",
        "body": "Camphor, sans-serif"
      },
      "path": "themes/stripe"
    }
  ]
}
```

**Resolution order**: `.aurea/themes/<name>/` (local, writable) → `src/aurea/themes/<name>/` (global, read-only bundled).

---

## 7. Distribution: PyInstaller + Zipapp

**Decision**: Two additional distribution artifacts beyond pip — PyInstaller exe and zipapp `.pyz`.

**PyInstaller** (`build/aurea.spec`):
- `Analysis(['src/aurea/cli.py'], ...)` with `datas=[('src/aurea/vendor', 'aurea/vendor'), ('src/aurea/themes', 'aurea/themes'), ('src/aurea/agent_commands', 'aurea/agent_commands')]`
- `hiddenimports=['typer', 'jinja2', 'mistune', 'rich', 'watchdog']`
- All absolute imports in source — required; relative imports break bundling

**Zipapp** (`dist/aurea.pyz`):
```bash
python -m zipapp src/aurea -p "/usr/bin/env python3" -o dist/aurea.pyz -m "aurea.cli:app"
```
- Vendor dependencies with `pip install --target src/aurea/_deps ...` before zipping
- The `.pyz` file is the `src/aurea/` directory with vendored deps zipped

**Four-mode compatibility test** (required before any release):
1. `pip install -e . && aurea --version`
2. `python aurea.pyz --version`
3. `./aurea.exe --version` (Windows) / `./aurea --version` (macOS/Linux)
4. Copy `commands/claude/` to `.claude/commands/` — execute `/aurea.outline` in Claude Code

---

## 8. Agent Command Templates: Format Matrix

**Decision**: Canonical format is YAML frontmatter + Markdown body. Converted at `aurea init` time.

| Agent    | commands_dir              | file_format  | arg_placeholder |
|----------|---------------------------|--------------|-----------------|
| claude   | `.claude/commands/`       | `.md`        | `$ARGUMENTS`    |
| gemini   | `.gemini/commands/`       | `.toml`      | `{{args}}`      |
| copilot  | `.github/copilot-instructions/` | `.agent.md` | `$ARGUMENTS` |
| windsurf | `.windsurf/commands/`     | `.md`        | `$ARGUMENTS`    |
| devin    | `.devin/commands/`        | `.md`        | `$ARGUMENTS`    |
| chatgpt  | `.chatgpt/commands/`      | `.md`        | `$ARGUMENTS`    |
| cursor   | `.cursor/commands/`       | `.md`        | `$ARGUMENTS`    |
| generic  | (user-specified)          | `.md`        | `$ARGUMENTS`    |

**Placeholders substituted at init time**:
- `{{DESIGN_MD_PATH}}` → `.aurea/themes/<theme>/DESIGN.md`
- `{{THEME_CSS_PATH}}` → `.aurea/themes/<theme>/theme.css`
- `{{CONFIG_PATH}}` → `.aurea/config.json`
- `{{REGISTRY_PATH}}` → `.aurea/themes/registry.json`
- `{{SLIDES_DIR}}` → `slides/`
- `{{OUTPUT_DIR}}` → `output/`
- `$ARGUMENTS` / `{{args}}` → per-agent placeholder, kept as-is in final template

---

## Open Questions (Deferred to Implementation)

1. **Gemini `.toml` format**: Exact TOML schema for Gemini CLI commands — verify against Gemini CLI docs at implementation time.
2. **reveal.js 5.x exact version to vendor**: Pin to latest 5.x release at time of M3 implementation.
3. **Font embedding**: Which web fonts (if any) to bundle by default vs. only on `--embed-fonts` — deferred to M3.
4. **Syntax highlighting CSS (Pygments)**: Whether to inline Pygments CSS or use reveal.js built-in highlight theme — deferred to M3.
