"""Jinja2 environment setup and template rendering helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

_env = Environment(
    loader=PackageLoader("aurea", "templates"),
    autoescape=select_autoescape(enabled_extensions=(), disabled_extensions=("j2", "html")),
    keep_trailing_newline=True,
)


def inline_file(path: str | Path) -> str:
    """Read a file and return its text content (Jinja2 custom filter)."""
    return Path(path).read_text(encoding="utf-8")


_env.filters["inline_file"] = inline_file


def render_template(name: str, **ctx: Any) -> str:
    """Render a Jinja2 template by name with the given context variables."""
    return _env.get_template(name).render(**ctx)
