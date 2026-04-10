# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# Typer subcommands in this module use typing_extensions.Annotated at runtime.
# The future import causes TypeError on Python 3.8 (Art. I exception).
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from aurea._log import _log
from aurea.exceptions import AureaError

_console = Console()

# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def _global_themes_dir() -> Path:
    return Path(__file__).parent.parent / "themes"


def _load_registry_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": "1.0.0", "sources": [], "themes": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": "1.0.0", "sources": [], "themes": []}


def load_registry(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Merge local + global registry; local entries shadow global by id."""
    global_reg = _load_registry_file(_global_themes_dir() / "registry.json")

    if project_root is None:
        project_root = Path.cwd()
    local_reg = _load_registry_file(project_root / ".aurea" / "themes" / "registry.json")

    # Merge: local shadows global
    theme_map: Dict[str, Dict[str, Any]] = {}
    for t in global_reg.get("themes", []):
        theme_map[t["id"]] = t
    for t in local_reg.get("themes", []):
        theme_map[t["id"]] = t  # local wins

    return {
        "version": global_reg.get("version", "1.0.0"),
        "sources": global_reg.get("sources", []),
        "themes": list(theme_map.values()),
    }


# ---------------------------------------------------------------------------
# T043 — search_themes
# ---------------------------------------------------------------------------


def _score_theme(theme: Dict[str, Any], query: str) -> int:
    """Return a relevance score for *theme* against *query* (higher = better)."""
    q = query.lower()
    score = 0
    fields = [
        theme.get("id", ""),
        theme.get("name", ""),
        theme.get("mood", ""),
        theme.get("category", ""),
        " ".join(theme.get("tags", [])),
    ]
    for f in fields:
        if q in f.lower():
            score += 1
        for word in q.split():
            if word in f.lower():
                score += 1
    return score


def search_themes(
    registry: Dict[str, Any],
    query: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Full-text search across id/name/tags/mood/category."""
    themes = registry.get("themes", [])

    if category:
        themes = [t for t in themes if t.get("category", "").lower() == category.lower()]
    if tag:
        themes = [t for t in themes if tag.lower() in [x.lower() for x in t.get("tags", [])]]

    scored = [(t, _score_theme(t, query)) for t in themes]
    scored = [(t, s) for t, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [t for t, _ in scored[:10]]


def apply_theme(theme_id: str, project_root: Path) -> None:
    """Copy theme files to .aurea/themes/ and update config.json."""
    # Find theme source
    local_themes = project_root / ".aurea" / "themes"
    registry = load_registry(project_root)
    theme_meta = next((t for t in registry.get("themes", []) if t["id"] == theme_id), None)

    if theme_meta is None:
        raise AureaError(
            f"Error: theme '{theme_id}' not found. Try 'aurea theme search {theme_id}'"
        )

    # Locate source dir
    src_dir: Optional[Path] = None
    global_candidate = _global_themes_dir() / theme_id
    if global_candidate.is_dir():
        src_dir = global_candidate
    local_candidate = local_themes / theme_id
    if local_candidate.is_dir():
        src_dir = local_candidate

    if src_dir is None:
        raise AureaError(f"Error: theme '{theme_id}' files not found on disk.")

    # Copy to local themes (skip if already in place)
    dst_dir = local_themes / theme_id
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_dir.resolve() != dst_dir.resolve():
        for fname in ("DESIGN.md", "theme.css", "layout.css", "meta.json"):
            src_f = src_dir / fname
            if src_f.exists():
                shutil.copy2(src_f, dst_dir / fname)

    # Update config.json
    config_path = project_root / ".aurea" / "config.json"
    if not config_path.exists():
        raise AureaError("Error: not in an Aurea project directory (no .aurea/config.json found)")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    cfg["theme"] = theme_id
    config_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    # Update local registry entry
    local_reg_path = local_themes / "registry.json"
    local_reg = _load_registry_file(local_reg_path)
    existing_ids = [t["id"] for t in local_reg.get("themes", [])]
    if theme_id not in existing_ids:
        theme_meta_copy = dict(theme_meta)
        theme_meta_copy["path"] = theme_id
        local_reg.setdefault("themes", []).append(theme_meta_copy)
        local_reg_path.write_text(json.dumps(local_reg, indent=2), encoding="utf-8")

    _log.info("Theme '%s' applied. Config updated.", theme_id)


# ---------------------------------------------------------------------------
# T044 — theme sub-commands
# ---------------------------------------------------------------------------


def cmd_list(format_: str = "table") -> None:
    """List all themes."""
    registry = load_registry()
    themes = registry.get("themes", [])

    if format_ == "json":
        print(json.dumps(themes, indent=2))
        return

    table = Table(title="Available Themes", show_header=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Mood", max_width=40)
    table.add_column("Colors")

    for t in sorted(themes, key=lambda x: x.get("id", "")):
        colors = t.get("colors", {})
        color_str = " ".join(f"[{v}]■[/{v}]" for v in list(colors.values())[:3])
        table.add_row(
            t.get("id", ""),
            t.get("name", ""),
            t.get("category", ""),
            t.get("mood", "")[:40],
            color_str,
        )

    _console.print(table)


def cmd_search(
    query: str,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    format_: str = "table",
) -> None:
    """Search themes by keyword."""
    registry = load_registry()
    results = search_themes(registry, query, category=category, tag=tag)

    if not results:
        _log.warning("No themes found for query '%s'", query)
        return

    if format_ == "json":
        print(json.dumps(results, indent=2))
        return

    table = Table(title=f"Search: {query}", show_header=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Mood", max_width=40)

    for t in results:
        table.add_row(
            t.get("id", ""),
            t.get("name", ""),
            t.get("category", ""),
            t.get("mood", "")[:40],
        )

    _console.print(table)


def cmd_info(theme_id: str) -> None:
    """Show full metadata for a theme with color swatches."""
    registry = load_registry()
    theme = next((t for t in registry.get("themes", []) if t["id"] == theme_id), None)

    if theme is None:
        _log.error("Error: theme '%s' not found", theme_id)
        sys.exit(1)

    colors = theme.get("colors", {})
    color_lines = []
    for role, hex_val in colors.items():
        color_lines.append(
            f"  {role.ljust(12)}: [bold]{hex_val}[/bold]  [{hex_val}]■■■[/{hex_val}]"
        )

    typo = theme.get("typography", {})
    info = (
        "[bold]{name}[/bold] ({id})\n\n"
        "[dim]Category:[/dim] {category}\n"
        "[dim]Tags:[/dim] {tags}\n"
        "[dim]Mood:[/dim] {mood}\n\n"
        "[dim]Colors:[/dim]\n{colors}\n\n"
        "[dim]Typography:[/dim]\n"
        "  Heading: {heading}\n"
        "  Body: {body}\n"
    ).format(
        name=theme.get("name", theme_id),
        id=theme_id,
        category=theme.get("category", ""),
        tags=", ".join(theme.get("tags", [])),
        mood=theme.get("mood", ""),
        colors="\n".join(color_lines),
        heading=typo.get("heading", ""),
        body=typo.get("body", ""),
    )

    _console.print(Panel(info, title="Theme Info"))


def cmd_show(theme_id: str) -> None:
    """Print the DESIGN.md of a theme."""
    registry = load_registry()
    theme = next((t for t in registry.get("themes", []) if t["id"] == theme_id), None)

    if theme is None:
        _log.error("Error: theme '%s' not found", theme_id)
        sys.exit(1)

    # Find DESIGN.md
    candidates = [
        _global_themes_dir() / theme_id / "DESIGN.md",
        Path.cwd() / ".aurea" / "themes" / theme_id / "DESIGN.md",
    ]
    design_md: Optional[Path] = None
    for c in candidates:
        if c.exists():
            design_md = c
            break

    if design_md is None:
        _log.error("DESIGN.md not found for theme '%s'", theme_id)
        sys.exit(1)

    _console.print(Markdown(design_md.read_text(encoding="utf-8")))


def cmd_use(theme_id: str) -> None:
    """Apply a theme to the current project."""
    project_root = Path.cwd()
    config = project_root / ".aurea" / "config.json"

    if not config.exists():
        _log.error("Error: not in an Aurea project directory (no .aurea/config.json found)")
        sys.exit(1)

    try:
        apply_theme(theme_id, project_root)
        pass  # apply_theme already logs confirmation via _log.info
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)


def cmd_create(theme_name: str, output: Optional[str] = None) -> None:
    """Scaffold a new custom theme."""
    project_root = Path.cwd()
    if output:
        theme_dir = Path(output)
    else:
        theme_dir = project_root / ".aurea" / "themes" / theme_name

    theme_dir.mkdir(parents=True, exist_ok=True)

    # DESIGN.md scaffold
    design_md = f"""\
# {theme_name.title()} Theme — Design System

## 1. Visual Theme

<!-- Describe the overall visual character of this theme. -->

## 2. Color Palette

<!-- List all colors with their hex values and semantic roles:
     primary, background, text, accent, surface, etc. -->

## 3. Typography

<!-- Heading font, body font, sizes, weights, line height. -->

## 4. Components

<!-- Buttons, code blocks, lists, tables, callouts — describe each. -->

## 5. Layout

<!-- Grid system, max-width, spacing scale, padding conventions. -->

## 6. Depth

<!-- Shadows, border-radius, z-index layers, blur effects. -->

## 7. Do\'s and Don\'ts

<!-- List what to do and what to avoid when using this theme. -->

## 8. Responsive

<!-- Breakpoints, mobile behavior, scaling notes. -->

## 9. Agent Prompt Guide

<!-- How should an AI agent use this theme? What to emphasize?
     What colors to use for what purposes? Maximum words per slide? -->
"""

    (theme_dir / "DESIGN.md").write_text(design_md, encoding="utf-8")

    # theme.css skeleton
    theme_css = f"""\
/**
 * {theme_name.title()} theme — reveal.js CSS custom properties
 * Edit the values below to define your visual style.
 */

:root {{
  --r-background-color: #ffffff;
  --r-main-color: #111111;
  --r-main-font: sans-serif;
  --r-main-font-size: 1.1rem;
  --r-heading-color: #333333;
  --r-heading-font: sans-serif;
  --r-heading-font-weight: 700;
  --r-heading-text-transform: none;
  --r-heading1-size: 2.5em;
  --r-heading2-size: 1.8em;
  --r-heading3-size: 1.4em;
  --r-link-color: #0066cc;
  --r-link-color-hover: #004499;
  --r-code-font: monospace;
  --r-block-margin: 20px;
}}
"""

    (theme_dir / "theme.css").write_text(theme_css, encoding="utf-8")

    # layout.css
    (theme_dir / "layout.css").write_text(
        "/* Layout overrides — customize as needed */\n:root {}\n",
        encoding="utf-8",
    )

    # meta.json stub
    meta = {
        "id": theme_name,
        "name": theme_name.title(),
        "category": "custom",
        "tags": ["custom"],
        "mood": "Custom theme",
        "colors": {
            "primary": "#333333",
            "background": "#ffffff",
            "text": "#111111",
        },
        "typography": {"heading": "sans-serif", "body": "sans-serif"},
        "version": "1.0.0",
    }
    (theme_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Created theme scaffold: {theme_dir}", file=sys.stderr)
    for f in ("DESIGN.md", "theme.css", "layout.css", "meta.json"):
        _log.info("  + %s", theme_dir / f)
