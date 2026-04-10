# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# Typer commands added in this module use typing_extensions.Annotated at
# runtime — the future import causes TypeError on Python 3.8 (Art. I).
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple

import yaml

from aurea._log import _log
from aurea._regex import EXTERNAL_LINK, HTML_ATTR, SLIDE_SEP, SPEAKER_NOTES
from aurea.exceptions import AureaError

# ---------------------------------------------------------------------------
# Required DESIGN.md sections (9)
# ---------------------------------------------------------------------------
REQUIRED_SECTIONS: FrozenSet[str] = frozenset(
    {
        "visual theme",
        "color palette",
        "typography",
        "components",
        "layout",
        "depth",
        "do's",
        "responsive",
        "agent prompt",
    }
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Slide:
    index: int
    markdown: str
    html: str = ""
    notes: str = ""
    attributes: str = ""
    word_count: int = 0


@dataclass
class Presentation:
    title: str = ""
    author: str = ""
    theme: str = ""
    slides: List[Slide] = field(default_factory=list)


# ---------------------------------------------------------------------------
# T035 — parse_slides
# ---------------------------------------------------------------------------


def parse_slides(markdown_text: str) -> Presentation:
    """Parse Markdown text into a Presentation with Slide objects."""
    # Split frontmatter from body
    front: Dict = {}
    body = markdown_text

    # Check for YAML frontmatter: opening --- on line 1, closing --- on its own line
    if markdown_text.startswith("---\n"):
        parts = markdown_text.split("\n---\n", 1)
        if len(parts) == 2 and parts[0].startswith("---"):
            try:
                # Remove leading --- and parse remaining YAML
                front = yaml.safe_load(parts[0][3:]) or {}
            except yaml.YAMLError:
                _log.warning("Could not parse YAML frontmatter, using defaults")
            body = parts[1]

    presentation = Presentation(
        title=str(front.get("title", "")),
        author=str(front.get("author", "")),
        theme=str(front.get("theme", "")),
    )

    raw_slides = SLIDE_SEP.split(body)
    index = 0
    for raw in raw_slides:
        raw = raw.strip()
        if not raw:
            continue

        # Extract HTML attributes (<!-- .slide: ... -->)
        attrs_match = HTML_ATTR.search(raw)
        attributes = attrs_match.group(1).strip() if attrs_match else ""
        if attrs_match:
            raw = raw[: attrs_match.start()] + raw[attrs_match.end() :]
            raw = raw.strip()

        # Extract speaker notes
        notes = ""
        notes_match = SPEAKER_NOTES.search(raw)
        if notes_match:
            notes = notes_match.group(1).strip()
            raw = raw[: notes_match.start()].strip()

        # Word count (on slide body, not notes)
        word_count = len(raw.split())

        slide = Slide(
            index=index,
            markdown=raw,
            notes=notes,
            attributes=attributes,
            word_count=word_count,
        )

        if word_count > 40:
            _log.warning(
                "Warning: slide %d has %d words (limit: 40)",
                index + 1,
                word_count,
            )

        presentation.slides.append(slide)
        index += 1

    return presentation


# ---------------------------------------------------------------------------
# T036 — resolve_theme
# ---------------------------------------------------------------------------


def resolve_theme(
    config_path: Optional[Path],
    cli_theme: Optional[str],
    frontmatter_theme: str,
) -> Tuple[str, Path]:
    """Return (theme_id, theme_dir) applying precedence: CLI > config > frontmatter."""
    # Load config
    config_theme = ""
    if config_path and config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            config_theme = cfg.get("theme", "")
        except (json.JSONDecodeError, OSError):
            pass

    theme_id = cli_theme or config_theme or frontmatter_theme or "default"

    # Locate theme dir — local first, then global
    if config_path:
        project_root = config_path.parent.parent
        local_theme = project_root / ".aurea" / "themes" / theme_id
        if local_theme.is_dir():
            _validate_design_md(local_theme / "DESIGN.md", theme_id)
            return theme_id, local_theme

    # Global bundled themes
    global_theme = Path(__file__).parent.parent / "themes" / theme_id
    if global_theme.is_dir():
        _validate_design_md(global_theme / "DESIGN.md", theme_id)
        return theme_id, global_theme

    raise AureaError(
        "Error: no theme set. Run 'aurea theme use <id>' first"
    )


def _validate_design_md(design_md_path: Path, theme_id: str) -> None:
    """Raise AureaError if DESIGN.md is missing or lacks any of the 9 required sections."""
    if not design_md_path.exists():
        raise AureaError(
            f"Error: theme '{theme_id}' DESIGN.md missing or invalid (needs 9 sections)"
        )
    text = design_md_path.read_text(encoding="utf-8").lower()
    missing = [s for s in REQUIRED_SECTIONS if s not in text]
    if missing:
        raise AureaError(
            "Error: theme '{t}' DESIGN.md is missing sections: {m}".format(
                t=theme_id, m=", ".join(sorted(missing))
            )
        )


# ---------------------------------------------------------------------------
# T037 — render_slides (mistune + Pygments)
# ---------------------------------------------------------------------------


def render_slides(presentation: Presentation, theme_dir: Path) -> Presentation:
    """Render each slide's Markdown to HTML using mistune + Pygments."""
    import mistune

    try:
        from pygments import highlight as pyg_highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.util import ClassNotFound

        _formatter = HtmlFormatter(nowrap=True, cssclass="highlight")

        class _HighlightRenderer(mistune.HTMLRenderer):
            def block_code(self, code: str, info: Optional[str] = None, **kwargs) -> str:
                if info:
                    lang = info.strip().split(None, 1)[0]
                    try:
                        lexer = get_lexer_by_name(lang, stripall=True)
                    except ClassNotFound:
                        lexer = guess_lexer(code)
                else:
                    lexer = guess_lexer(code)
                highlighted = pyg_highlight(code, lexer, _formatter)
                return f'<pre><code class="highlight">{highlighted}</code></pre>\n'

        md = mistune.create_markdown(renderer=_HighlightRenderer())
    except ImportError:
        # Pygments not available — use plain mistune renderer
        md = mistune.create_markdown()

    for slide in presentation.slides:
        slide.html = md(slide.markdown)

    return presentation


# ---------------------------------------------------------------------------
# T039 — inline_assets
# ---------------------------------------------------------------------------


def inline_assets(
    theme_dir: Path,
    embed_fonts: bool = False,
) -> Dict[str, str]:
    """Load and return all assets to be inlined in the HTML template."""
    vendor = Path(__file__).parent.parent / "vendor" / "revealjs" / "dist"

    def _read(p: Path) -> str:
        if p.exists():
            content = p.read_text(encoding="utf-8")
            # Escape </script> occurrences so the HTML parser does not
            # prematurely close the enclosing <script> block.  The backslash
            # is valid JavaScript and invisible to the JS engine.
            content = content.replace("</script>", r"<\/script>")
            return content
        _log.warning("Vendor file not found: %s", p)
        return ""

    vendor_root = Path(__file__).parent.parent / "vendor"

    # Reveal.js 5.x ships plugins as pure ES modules (.mjs) that use bare
    # import specifiers (e.g. ``import { marked } from 'marked'``).  These
    # cannot be inlined in a plain ``<script>`` tag without a bundler.
    #
    # Strategy: vendor UMD builds of the dependencies (highlight.js, marked)
    # and expose them as globals, then create minimal IIFE plugin wrappers
    # that use those globals.  The result is a 100 % standalone HTML file
    # with no external requests.

    # Inline plugin stubs
    _plugin_stubs = """\
/* ---- reveal.js plugin shims (IIFE, no ES-module deps) ---- */
// RevealMarkdown — content is already pre-rendered by the build pipeline;
// this stub satisfies Reveal.initialize without re-parsing markdown.
window.RevealMarkdown = (function () {
  var Plugin = {
    id: 'markdown',
    init: function () { return Promise.resolve(); }
  };
  return Plugin;
}());

// RevealHighlight — wraps the vendored highlight.js UMD build.
window.RevealHighlight = (function () {
  var Plugin = {
    id: 'highlight',
    init: function (reveal) {
      reveal.addEventListener('ready', function () {
        reveal.getRevealElement()
          .querySelectorAll('pre code')
          .forEach(function (el) { hljs.highlightElement(el); });
      });
      return Promise.resolve();
    }
  };
  return Plugin;
}());

// RevealNotes — stub (no separate speaker-view window in standalone mode).
window.RevealNotes = (function () {
  return { id: 'notes', init: function () { return Promise.resolve(); } };
}());

// RevealZoom — stub.
window.RevealZoom = function () {
  return { id: 'zoom', init: function () {} };
};
"""

    assets = {
        "reset_css": _read(vendor / "reset.css"),
        "reveal_css": _read(vendor / "reveal.css"),
        "theme_css": _read(theme_dir / "theme.css"),
        "layout_css": _read(theme_dir / "layout.css"),
        "highlight_css": _read(
            vendor / "plugin" / "highlight" / "monokai.css"
        ),
        "reveal_js": _read(vendor / "reveal.js"),
        # UMD builds: no import/export statements, safe to inline directly.
        "highlight_js": _read(vendor_root / "highlight.min.js"),
        "marked_js": _read(vendor_root / "marked.min.js"),
        "plugin_stubs": _plugin_stubs,
        # Keep keys referenced in the template with empty strings so Jinja2
        # does not raise UndefinedError for old templates.
        "markdown_js": "",
        "notes_js": "",
        "zoom_js": "",
    }

    if embed_fonts:
        # Base64-encode any @font-face woff2 references in theme CSS
        import base64

        def _embed_font_urls(css: str, base_dir: Path) -> str:
            def _replace(m: "re.Match") -> str:
                rel_path = m.group(1)
                font_path = base_dir / rel_path
                if font_path.exists():
                    b64 = base64.b64encode(font_path.read_bytes()).decode()
                    return f'url("data:font/woff2;base64,{b64}")'
                return m.group(0)

            return re.sub(r'url\(["\']?([^"\')\s]+\.woff2)["\']?\)', _replace, css)

        assets["theme_css"] = _embed_font_urls(assets["theme_css"], theme_dir)

    return assets


# ---------------------------------------------------------------------------
# T040 — run_build (main orchestrator)
# ---------------------------------------------------------------------------


def run_build(
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    theme_override: Optional[str] = None,
    minify: bool = False,
    watch: bool = False,
    embed_fonts: bool = False,
) -> None:
    """Orchestrate parse → resolve → render → inline → write pipeline."""
    _do_build(
        input_file=input_file,
        output_file=output_file,
        theme_override=theme_override,
        minify=minify,
        embed_fonts=embed_fonts,
    )

    if watch:
        _run_watch(
            input_file=input_file,
            output_file=output_file,
            theme_override=theme_override,
            minify=minify,
            embed_fonts=embed_fonts,
        )


def _do_build(
    input_file: Optional[str],
    output_file: Optional[str],
    theme_override: Optional[str],
    minify: bool,
    embed_fonts: bool,
) -> None:
    """Execute a single build pass."""
    start = time.perf_counter()

    # Resolve paths
    cwd = Path.cwd()
    src = Path(input_file) if input_file else cwd / "slides" / "presentation.md"
    dst = Path(output_file) if output_file else cwd / "output" / "presentation.html"
    config_path = cwd / ".aurea" / "config.json"

    if not src.exists():
        _log.error("Error: input file '%s' not found", src)
        sys.exit(1)

    # Parse
    md_text = src.read_text(encoding="utf-8")
    presentation = parse_slides(md_text)

    if not presentation.slides:
        _log.error(
            "Error: no slides found in '%s'. Check '---' separators", src
        )
        sys.exit(1)

    # Resolve theme
    try:
        theme_id, theme_dir = resolve_theme(
            config_path=config_path if config_path.exists() else None,
            cli_theme=theme_override,
            frontmatter_theme=presentation.theme,
        )
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)

    # Render slides
    presentation = render_slides(presentation, theme_dir)

    # Inline assets
    assets = inline_assets(theme_dir=theme_dir, embed_fonts=embed_fonts)

    # Render Jinja2 template
    from aurea._tpl import render_template

    html = render_template(
        "reveal.html.j2",
        title=presentation.title or "Presentation",
        author=presentation.author,
        slides=presentation.slides,
        **assets,
    )

    # Strip any stray external references (Art. III safety net)
    html = EXTERNAL_LINK.sub("", html)

    # Minify (Art. VII: stdlib only — collapse whitespace between tags)
    if minify:
        html = re.sub(r">\s+<", "><", html)

    # Write output
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html, encoding="utf-8")

    elapsed = time.perf_counter() - start
    size_kb = len(html.encode()) // 1024
    print(str(dst), flush=True)
    _log.info(
        "Built %d slides in %.2fs (%d KB)",
        len(presentation.slides),
        elapsed,
        size_kb,
    )


def _run_watch(
    input_file: Optional[str],
    output_file: Optional[str],
    theme_override: Optional[str],
    minify: bool,
    embed_fonts: bool,
) -> None:
    """Watch mode: rebuild on file changes (uses watchdog)."""
    import threading

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    cwd = Path.cwd()
    watch_dirs = [
        str(cwd / "slides"),
        str(cwd / ".aurea" / "themes"),
    ]

    _debounce_timer: Optional[threading.Timer] = None
    _lock = threading.Lock()

    def _rebuild() -> None:
        start = time.perf_counter()
        try:
            _do_build(
                input_file=input_file,
                output_file=output_file,
                theme_override=theme_override,
                minify=minify,
                embed_fonts=embed_fonts,
            )
            _log.info("Rebuilt in %.2fs (watching...)", time.perf_counter() - start)
        except SystemExit:
            pass

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event) -> None:  # type: ignore[override]
            nonlocal _debounce_timer
            with _lock:
                if _debounce_timer:
                    _debounce_timer.cancel()
                _debounce_timer = threading.Timer(0.5, _rebuild)
                _debounce_timer.start()

    observer = Observer()
    handler = _Handler()
    for d in watch_dirs:
        if Path(d).exists():
            observer.schedule(handler, d, recursive=True)

    observer.start()
    print("Watching for changes... Press Ctrl+C to stop", file=sys.stderr)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
