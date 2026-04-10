"""Import themes from VoltAgent/awesome-design-md into the Aurea theme registry.

Usage:
    python scripts/import-awesome-designs.py [--repo-dir PATH] [--dry-run]

This script:
1. Clones or updates VoltAgent/awesome-design-md
2. For each DESIGN.md in the repo, extracts metadata
3. Generates meta.json, theme.css, layout.css for each theme
4. Updates src/aurea/themes/registry.json
"""
# IMPORTANT: Do NOT use `from __future__ import annotations` in this script.
# It must run in Python 3.8+ without __future__ annotations.

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_URL = "https://github.com/VoltAgent/awesome-design-md.git"
THEMES_DIR = Path(__file__).parent.parent / "src" / "aurea" / "themes"
REGISTRY_PATH = THEMES_DIR / "registry.json"

# Known theme categories by id prefix
_CATEGORY_MAP = {
    "apple": "tech",
    "stripe": "fintech",
    "linear": "devtools",
    "vercel": "devtools",
    "notion": "productivity",
    "figma": "design",
    "claude": "ai",
    "openai": "ai",
    "ferrari": "automotive",
    "spacex": "aerospace",
    "default": "general",
    "midnight": "dark",
    "aurora": "colorful",
    "editorial": "editorial",
    "brutalist": "experimental",
}


def _run(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """Run a subprocess and return exit code."""
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def clone_or_update(repo_dir: Path) -> bool:
    """Clone or pull awesome-design-md. Returns True on success."""
    if repo_dir.exists():
        print(f"Updating {repo_dir}...")
        code = _run(["git", "pull", "--quiet"], cwd=repo_dir)
        return code == 0
    else:
        print(f"Cloning {REPO_URL} into {repo_dir}...")
        code = _run(["git", "clone", "--quiet", "--depth=1", REPO_URL, str(repo_dir)])
        return code == 0


def _extract_hex_colors(text: str) -> List[str]:
    """Extract #rrggbb hex colors from text."""
    return re.findall(r"#[0-9a-fA-F]{6}\b", text)


def _extract_fonts(text: str) -> List[str]:
    """Extract font family names from text (simple heuristic)."""
    fonts = re.findall(r"\bfont(?:-family)?:\s*([A-Za-z][A-Za-z0-9 \-]+)", text, re.IGNORECASE)
    return [f.strip().strip("\"'") for f in fonts if f.strip()]


_SKIP_PREFIXES = (
    "design system details",
    "the design system",
    "this design system",
    "details have been moved",
    ">",
    "<!--",
)


def _infer_mood(design_text: str) -> str:
    """Infer a one-line mood from DESIGN.md content."""
    lines = design_text.splitlines()
    for line in lines[1:30]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lower = stripped.lower()
        if any(lower.startswith(p) for p in _SKIP_PREFIXES):
            continue
        if len(stripped) > 15:
            return stripped[:80]
    return "Professional design system"


def _assign_color_roles(colors: List[str]) -> Dict[str, str]:
    """Assign semantic roles to extracted colors."""

    def _brightness(h: str) -> float:
        try:
            r = int(h[1:3], 16)
            g = int(h[3:5], 16)
            b = int(h[5:7], 16)
            return (0.299 * r + 0.587 * g + 0.114 * b) / 255
        except (ValueError, IndexError):
            return 0.5

    if not colors:
        return {"primary": "#333333", "background": "#ffffff", "text": "#111111"}

    from collections import Counter

    freq = Counter(c.lower() for c in colors)
    ranked = [c for c, _ in freq.most_common(10)]

    light = [c for c in ranked if _brightness(c) > 0.7]
    dark = [c for c in ranked if _brightness(c) < 0.3]
    mid = [c for c in ranked if 0.3 <= _brightness(c) <= 0.7]

    result: Dict[str, str] = {}
    result["background"] = light[0] if light else "#ffffff"
    result["text"] = dark[0] if dark else "#111111"
    result["primary"] = mid[0] if mid else (ranked[0] if ranked else "#333333")
    if len(mid) > 1:
        result["secondary"] = mid[1]
    return result


def parse_design_md(design_md_path: Path) -> Dict[str, Any]:
    """Parse a DESIGN.md file and extract metadata."""
    text = design_md_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Extract title from first heading
    name = design_md_path.parent.name
    for line in lines[:5]:
        m = re.match(r"^#\s+(.+)", line)
        if m:
            name = m.group(1).strip()
            break

    colors = _assign_color_roles(_extract_hex_colors(text))
    fonts = _extract_fonts(text)
    mood = _infer_mood(text)
    theme_id = design_md_path.parent.name.lower().replace(" ", "-")
    category = _CATEGORY_MAP.get(theme_id, "general")

    return {
        "id": theme_id,
        "name": name,
        "category": category,
        "tags": [category, "imported"],
        "mood": mood,
        "colors": colors,
        "typography": {
            "heading": fonts[0] if fonts else "sans-serif",
            "body": fonts[1] if len(fonts) > 1 else "sans-serif",
        },
        "version": "1.0.0",
        "path": theme_id,
        "source": "awesome-design-md",
    }


def generate_theme_css(meta: Dict[str, Any]) -> str:
    """Generate reveal.js theme CSS from metadata."""
    colors = meta.get("colors", {})
    typo = meta.get("typography", {})
    bg = colors.get("background", "#ffffff")
    text = colors.get("text", "#111111")
    primary = colors.get("primary", "#333333")
    heading_font = typo.get("heading", "sans-serif")
    body_font = typo.get("body", "sans-serif")

    return """\
/**
 * {name} theme — reveal.js CSS custom properties
 * Auto-generated by import-awesome-designs.py
 * Source: VoltAgent/awesome-design-md
 */

:root {{
  --r-background-color: {bg};
  --r-main-color: {text};
  --r-main-font: {body_font};
  --r-main-font-size: 1.1rem;
  --r-heading-color: {primary};
  --r-heading-font: {heading_font};
  --r-heading-font-weight: 700;
  --r-heading-text-transform: none;
  --r-heading1-size: 2.5em;
  --r-heading2-size: 1.8em;
  --r-heading3-size: 1.4em;
  --r-link-color: {primary};
  --r-link-color-hover: {text};
  --r-code-font: "Fira Code", "JetBrains Mono", Consolas, monospace;
  --r-block-margin: 20px;
}}
""".format(
        name=meta.get("name", "Theme"),
        bg=bg,
        text=text,
        primary=primary,
        heading_font=heading_font,
        body_font=body_font,
    )


def import_theme(design_md_path: Path, dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """Import a single theme. Returns metadata dict on success, None on failure."""
    try:
        meta = parse_design_md(design_md_path)
        theme_id = meta["id"]

        if not dry_run:
            dst = THEMES_DIR / theme_id
            dst.mkdir(parents=True, exist_ok=True)

            # Copy DESIGN.md
            import shutil

            shutil.copy2(design_md_path, dst / "DESIGN.md")

            # Generate theme.css
            (dst / "theme.css").write_text(generate_theme_css(meta), encoding="utf-8")

            # Generate layout.css
            (dst / "layout.css").write_text(
                "/* Layout overrides — customize as needed */\n:root {}\n",
                encoding="utf-8",
            )

            # Write meta.json (without internal path field)
            meta_copy = {k: v for k, v in meta.items() if k != "path"}
            meta_copy["id"] = theme_id
            (dst / "meta.json").write_text(json.dumps(meta_copy, indent=2), encoding="utf-8")

        print(f"  + {theme_id}: {meta['name']}")
        return meta

    except Exception as exc:
        print(f"  ! Failed {design_md_path}: {exc}", file=sys.stderr)
        return None


def update_registry(themes: List[Dict[str, Any]], dry_run: bool = False) -> None:
    """Update registry.json with new/updated themes."""
    if dry_run:
        print(f"[dry-run] Would update {REGISTRY_PATH} with {len(themes)} themes")
        return

    # Load existing registry
    if REGISTRY_PATH.exists():
        try:
            registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            registry = {"version": "1.0.0", "sources": [], "themes": []}
    else:
        registry = {"version": "1.0.0", "sources": [], "themes": []}

    # Merge: imported themes shadow existing by id
    existing = {t["id"]: t for t in registry.get("themes", [])}
    for theme in themes:
        existing[theme["id"]] = theme

    registry["themes"] = list(existing.values())

    # Update source entry
    sources = registry.setdefault("sources", [])
    source_ids = [s.get("repo") for s in sources]
    if REPO_URL not in source_ids:
        sources.append({"repo": REPO_URL, "last_sync": "auto"})

    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Updated {REGISTRY_PATH} — {len(existing)} total themes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-dir",
        default=str(Path(__file__).parent.parent / ".awesome-design-md"),
        help="Local path for cloned awesome-design-md repo",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without writing files",
    )
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)

    # Clone or update repo
    if not clone_or_update(repo_dir):
        print(
            "Warning: could not clone/update awesome-design-md. Using existing files if available.",
            file=sys.stderr,
        )
        if not repo_dir.exists():
            print("Error: repo not available and no local copy found.", file=sys.stderr)
            return 0  # Silent failure per FR-clarification

    # Find all design files — repo uses README.md inside design-md/*, fallback to DESIGN.md
    design_mds = sorted(
        p
        for p in repo_dir.rglob("README.md")
        if p.parent != repo_dir  # skip root README.md
    )
    if not design_mds:
        design_mds = sorted(p for p in repo_dir.rglob("DESIGN.md") if p.parent != repo_dir)
    if not design_mds:
        print("No design files found in repo.", file=sys.stderr)
        return 0

    print(f"Found {len(design_mds)} design files")

    imported: List[Dict[str, Any]] = []
    for dm in design_mds:
        meta = import_theme(dm, dry_run=args.dry_run)
        if meta:
            imported.append(meta)

    print(f"\nImported {len(imported)} themes")

    if imported:
        update_registry(imported, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
