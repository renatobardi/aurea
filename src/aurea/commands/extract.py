# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# The Typer command at the bottom uses typing_extensions.Annotated at runtime.
# Combining with the future import causes TypeError on Python 3.8 (Art. I).
import collections
import json
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

from aurea._http import check_robots, fetch_sync
from aurea._log import _log
from aurea._regex import HEX_COLOR
from aurea.exceptions import AureaError

# ---------------------------------------------------------------------------
# T050 — CDN filter helper
# ---------------------------------------------------------------------------

_CDN_HOSTNAMES = frozenset(
    {
        "fonts.googleapis.com",
        "fonts.gstatic.com",
        "unpkg.com",
        "cdn.jsdelivr.net",
        "cdnjs.cloudflare.com",
    }
)


def should_skip_cdn(url: str) -> bool:
    """Return True if *url* hostname is a known CDN to skip."""
    try:
        hostname = urllib.parse.urlparse(url).netloc.lower()
        return hostname in _CDN_HOSTNAMES
    except Exception:
        return False


# ---------------------------------------------------------------------------
# DesignExtractor class
# ---------------------------------------------------------------------------


class DesignExtractor:
    def __init__(
        self,
        url: str,
        user_agent: str = "Aurea/1.0",
        timeout: int = 30,
        delay: float = 1.0,
        depth: int = 1,
        raw: bool = False,
    ) -> None:
        self.url = url
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.depth = depth
        self.raw = raw

    def fetch_page(self, url: str) -> str:
        """Fetch *url*, checking robots.txt first."""
        _log.info("Fetching %s...", url)
        if not check_robots(url, self.user_agent):
            raise AureaError(
                f"Error: {url} is disallowed by robots.txt"
            )
        return fetch_sync(url, self.user_agent, self.timeout)

    def extract_stylesheets(self, html: str, base_url: str) -> List[str]:
        """Return list of CSS text strings from <style> tags and external <link> sheets."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise AureaError(
                "beautifulsoup4 is not installed. Run: pip install aurea[extract]"
            )

        soup = BeautifulSoup(html, "lxml")
        css_texts: List[str] = []

        # Inline <style> tags
        for tag in soup.find_all("style"):
            text = tag.get_text()
            if text.strip():
                css_texts.append(text)

        # External <link rel="stylesheet"> tags
        for tag in soup.find_all("link", rel=True):
            rel_vals = tag.get("rel", [])
            if isinstance(rel_vals, list):
                rel_str = " ".join(rel_vals).lower()
            else:
                rel_str = str(rel_vals).lower()

            if "stylesheet" not in rel_str:
                continue

            href = tag.get("href", "")
            if not href:
                continue

            abs_url = urllib.parse.urljoin(base_url, href)

            if should_skip_cdn(abs_url):
                _log.info("Skipping CDN stylesheet: %s", abs_url)
                continue

            try:
                css_texts.append(fetch_sync(abs_url, self.user_agent, self.timeout))
            except AureaError as exc:
                _log.warning("Could not fetch stylesheet %s: %s", abs_url, exc)

        return css_texts

    def extract_color_tokens(self, css_list: List[str]) -> Dict[str, str]:
        """Extract and rank hex colors from CSS, assign semantic roles."""
        merged = "\n".join(css_list)
        all_colors = HEX_COLOR.findall(merged)
        if not all_colors:
            return {
                "primary": "#333333",
                "background": "#ffffff",
                "text": "#111111",
            }

        counter = collections.Counter(c.lower() for c in all_colors)
        ranked = [color for color, _ in counter.most_common(20)]

        def _is_dark(h: str) -> bool:
            r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
            return (r * 0.299 + g * 0.587 + b * 0.114) < 128

        def _is_light(h: str) -> bool:
            r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
            return (r * 0.299 + g * 0.587 + b * 0.114) > 200

        def _is_neutral(h: str) -> bool:
            r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
            max_c, min_c = max(r, g, b), min(r, g, b)
            return (max_c - min_c) < 30

        dark_colors = [c for c in ranked if _is_dark(c)]
        light_colors = [c for c in ranked if _is_light(c)]
        accent_candidates = [c for c in ranked if not _is_neutral(c)]

        result: Dict[str, str] = {}
        result["text"] = dark_colors[0] if dark_colors else "#111111"
        result["background"] = light_colors[0] if light_colors else "#ffffff"
        # Surface is typically a slightly different shade from background (for cards, etc.)
        result["surface"] = (
            light_colors[1] if len(light_colors) > 1 else result["background"]
        )
        result["primary"] = (
            accent_candidates[0]
            if accent_candidates
            else (ranked[0] if ranked else "#333333")
        )
        if len(accent_candidates) > 1:
            result["secondary"] = accent_candidates[1]
        if len(accent_candidates) > 2:
            result["accent"] = accent_candidates[2]

        return result

    def extract_typography_tokens(self, css_list: List[str]) -> Dict[str, str]:
        """Extract heading and body font families using cssutils."""
        try:
            import cssutils

            cssutils.log.setLevel(100)  # suppress cssutils warnings
        except ImportError:
            raise AureaError(
                "cssutils is not installed. Run: pip install aurea[extract]"
            )

        heading_fonts: List[str] = []
        body_fonts: List[str] = []

        _HEADING_SELS = ("h1", "h2", "h3")
        _BODY_SELS = ("body", "p")

        for css_text in css_list:
            try:
                sheet = cssutils.parseString(css_text, validate=False)
                for rule in sheet:
                    if not hasattr(rule, "selectorText"):
                        continue
                    sel = rule.selectorText.lower() if rule.selectorText else ""
                    ff = rule.style.getPropertyValue("font-family")
                    if not ff:
                        continue
                    ff = ff.strip()
                    if any(s in sel for s in _HEADING_SELS):
                        if ff not in heading_fonts:
                            heading_fonts.append(ff)
                    if any(s in sel for s in _BODY_SELS):
                        if ff not in body_fonts:
                            body_fonts.append(ff)
            except Exception:
                continue

        return {
            "heading": heading_fonts[0] if heading_fonts else "sans-serif",
            "body": body_fonts[0] if body_fonts else "sans-serif",
        }

    def extract_spacing_tokens(self, css_list: List[str]) -> Dict[str, str]:
        """Extract dominant spacing values and return sm/md/lg keys."""
        import re

        spacing_re = re.compile(
            r"(?:margin|padding|gap)\s*:\s*([0-9]+(?:\.[0-9]+)?(?:px|rem|em))",
            re.IGNORECASE,
        )
        merged = "\n".join(css_list)
        all_vals = spacing_re.findall(merged)
        counter = collections.Counter(all_vals)
        ranked = [v for v, _ in counter.most_common(10)]

        def _px_val(v: str) -> float:
            try:
                if v.endswith("rem"):
                    return float(v[:-3]) * 16
                if v.endswith("em"):
                    return float(v[:-2]) * 16
                return float(v[:-2])
            except ValueError:
                return 0.0

        ranked_sorted = sorted(ranked, key=_px_val)
        result: Dict[str, str] = {
            "sm": ranked_sorted[0] if len(ranked_sorted) > 0 else "4px",
            "md": ranked_sorted[len(ranked_sorted) // 2] if ranked_sorted else "8px",
            "lg": ranked_sorted[-1] if len(ranked_sorted) > 0 else "16px",
        }
        return result

    def extract_shadow_tokens(self, css_list: List[str]) -> List[str]:
        """Extract unique box-shadow values."""
        import re

        shadow_re = re.compile(r"box-shadow\s*:\s*([^;]+);", re.IGNORECASE)
        merged = "\n".join(css_list)
        shadows: List[str] = []
        for m in shadow_re.finditer(merged):
            val = m.group(1).strip()
            if val not in shadows and val.lower() != "none":
                shadows.append(val)
        return shadows[:5]

    def generate_raw_design_md(self, tokens: Dict[str, Any]) -> str:
        """Generate a 9-section DESIGN.md from extracted tokens (f-strings, not Jinja2)."""
        colors = tokens.get("colors", {})
        typo = tokens.get("typography", {})
        spacing = tokens.get("spacing", {})
        shadows = tokens.get("shadows", [])

        color_lines = "\n".join(
            f"- {k}: `{v}`" for k, v in colors.items()
        )
        shadow_lines = (
            "\n".join(f"- {s}" for s in shadows)
            if shadows
            else "- None detected"
        )

        return """# {url} — Extracted Design System

## 1. Visual Theme

Design system extracted from {url}.

<!-- TODO: Add a description of the overall visual character of this site. -->

## 2. Color Palette

{colors}

## 3. Typography

- Heading font: {heading}
- Body font: {body}

<!-- TODO: Add font sizes, weights, line height if detectable. -->

## 4. Components

<!-- TODO: Describe buttons, cards, code blocks, form elements visible on the site. -->

## 5. Layout

Spacing tokens:
- Small: {sm}
- Medium: {md}
- Large: {lg}

## 6. Depth

Box shadows:
{shadows}

<!-- TODO: Add border-radius, z-index layers if detectable. -->

## 7. Do's and Don'ts

**Do:**
- Use the extracted color palette consistently
- Reference spacing tokens for slide padding

**Don't:**
- Override primary/background colors without reason

## 8. Responsive

<!-- TODO: Fill in responsive breakpoints and mobile behavior. -->

## 9. Agent Prompt Guide

When using this theme:
- Primary color ({primary}) for emphasis and headings
- Background ({background}) with {text} text
- Keep slides to ≤40 words of body text
""".format(
            url=self.url,
            colors=color_lines if color_lines else "- No colors extracted",
            heading=typo.get("heading", "sans-serif"),
            body=typo.get("body", "sans-serif"),
            sm=spacing.get("sm", "4px"),
            md=spacing.get("md", "8px"),
            lg=spacing.get("lg", "16px"),
            shadows=shadow_lines,
            primary=colors.get("primary", "#333"),
            background=colors.get("background", "#fff"),
            text=colors.get("text", "#111"),
        )

    def generate_theme_css(self, tokens: Dict[str, Any]) -> str:
        """Map extracted tokens to reveal.js CSS custom properties."""
        colors = tokens.get("colors", {})
        typo = tokens.get("typography", {})

        return """:root {{
  --r-background-color: {background};
  --r-main-color: {text};
  --r-main-font: {body};
  --r-main-font-size: 1.1rem;
  --r-heading-color: {primary};
  --r-heading-font: {heading};
  --r-heading-font-weight: 700;
  --r-heading-text-transform: none;
  --r-heading1-size: 2.5em;
  --r-heading2-size: 1.8em;
  --r-heading3-size: 1.4em;
  --r-link-color: {accent};
  --r-link-color-hover: {accent};
  --r-code-font: "Courier New", monospace;
  --r-block-margin: 20px;
}}
""".format(
            background=colors.get("background", "#ffffff"),
            text=colors.get("text", "#111111"),
            primary=colors.get("primary", "#333333"),
            heading=typo.get("heading", "sans-serif"),
            body=typo.get("body", "sans-serif"),
            accent=colors.get("accent", colors.get("secondary", "#0066cc")),
        )

    def run(self, output_dir: Path) -> Dict[str, Any]:
        """Orchestrate full extraction pipeline. Returns dict with output paths."""
        # Fetch main page
        html = self.fetch_page(self.url)
        css_list = self.extract_stylesheets(html, self.url)

        # Optionally crawl deeper
        if self.depth > 1:
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                raise AureaError(
                    "beautifulsoup4 is not installed. Run: pip install aurea[extract]"
                )
            parsed_base = urllib.parse.urlparse(self.url)
            base_netloc = parsed_base.netloc
            soup = BeautifulSoup(html, "lxml")
            links = soup.find_all("a", href=True)
            seen = {self.url}
            for link in links[: 20]:  # cap at 20 extra pages
                href = urllib.parse.urljoin(self.url, link["href"])
                parsed = urllib.parse.urlparse(href)
                if parsed.netloc != base_netloc:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                time.sleep(self.delay)
                try:
                    extra_html = self.fetch_page(href)
                    css_list += self.extract_stylesheets(extra_html, href)
                except AureaError:
                    pass

        # Extract tokens
        colors = self.extract_color_tokens(css_list)
        typography = self.extract_typography_tokens(css_list)
        spacing = self.extract_spacing_tokens(css_list)
        shadows = self.extract_shadow_tokens(css_list)

        tokens: Dict[str, Any] = {
            "colors": colors,
            "typography": typography,
            "spacing": spacing,
            "shadows": shadows,
        }

        # Generate output files
        output_dir.mkdir(parents=True, exist_ok=True)

        design_md = self.generate_raw_design_md(tokens)
        design_path = output_dir / "DESIGN.md"
        design_path.write_text(design_md, encoding="utf-8")

        theme_css = self.generate_theme_css(tokens)
        theme_css_path = output_dir / "theme.css"
        theme_css_path.write_text(theme_css, encoding="utf-8")

        layout_css = "/* Layout overrides — customize as needed */\n:root {}\n"
        layout_path = output_dir / "layout.css"
        layout_path.write_text(layout_css, encoding="utf-8")

        theme_name = output_dir.name
        meta = {
            "id": theme_name,
            "name": theme_name.replace("-", " ").title(),
            "category": "extracted",
            "tags": ["extracted"],
            "mood": f"Extracted from {self.url}",
            "colors": colors,
            "typography": typography,
            "source": self.url,
            "version": "1.0.0",
        }
        meta_path = output_dir / "meta.json"
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return {
            "theme_dir": str(output_dir),
            "design_md": str(design_path),
            "theme_css": str(theme_css_path),
            "meta": meta,
            "colors_extracted": len(colors),
            "fonts_detected": len(typography),
        }


# ---------------------------------------------------------------------------
# run_extract entry point (called from cli.py)
# ---------------------------------------------------------------------------


def run_extract(
    url: str,
    name: Optional[str],
    depth: int,
    raw: bool,
    use: bool,
    timeout: int,
    user_agent: str,
    delay: float,
) -> None:
    """Run theme extraction and save to project."""
    cwd = Path.cwd()
    config_path = cwd / ".aurea" / "config.json"

    # Derive theme name from hostname if not provided
    if not name:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.netloc.lstrip("www.").replace(".", "-")
        if hostname:
            name = hostname
        elif not config_path.exists():
            _log.error("Error: --name is required when not in a project directory")
            sys.exit(1)
        else:
            _log.error("Error: --name is required when not in a project directory")
            sys.exit(1)

    # Determine output directory
    if config_path.exists():
        output_dir = cwd / ".aurea" / "themes" / name
    else:
        output_dir = cwd / name

    extractor = DesignExtractor(
        url=url,
        user_agent=user_agent,
        timeout=timeout,
        delay=delay,
        depth=depth,
        raw=raw,
    )

    try:
        result = extractor.run(output_dir)
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)

    # Print summary to stdout
    print(
        "Extracted theme '{n}' \u2192 {d}".format(n=name, d=result["theme_dir"])
    )
    print(
        "Colors extracted: {c}, Fonts detected: {f}".format(
            c=result["colors_extracted"], f=result["fonts_detected"]
        )
    )

    # Update local registry
    if config_path.exists():
        from aurea.commands.theme import _load_registry_file

        local_reg_path = cwd / ".aurea" / "themes" / "registry.json"
        local_reg = _load_registry_file(local_reg_path)
        meta = result["meta"]
        meta["path"] = name
        existing_ids = [t["id"] for t in local_reg.get("themes", [])]
        if name not in existing_ids:
            local_reg.setdefault("themes", []).append(meta)
        else:
            local_reg["themes"] = [
                meta if t["id"] == name else t
                for t in local_reg["themes"]
            ]
        local_reg_path.write_text(json.dumps(local_reg, indent=2), encoding="utf-8")

    # Apply if requested
    if use and config_path.exists():
        from aurea.commands.theme import apply_theme

        try:
            apply_theme(name, cwd)
            print(f"Theme '{name}' applied to project.")
        except AureaError as exc:
            _log.warning("Could not apply theme: %s", exc)
