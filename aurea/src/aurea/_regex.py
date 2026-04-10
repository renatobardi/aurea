"""Shared regex patterns used across Aurea commands."""

from __future__ import annotations

import re

# Split Markdown into individual slides on bare `---` lines
SLIDE_SEP = re.compile(r"^---$", re.MULTILINE)

# Match speaker notes block (everything after `Note:` or `Notes:` on a new line)
SPEAKER_NOTES = re.compile(r"\n(?:Note|Notes):\s*\n?(.*)", re.DOTALL | re.IGNORECASE)

# Match reveal.js slide HTML attribute comments: <!-- .slide: data-... -->
HTML_ATTR = re.compile(r"<!--\s*\.slide:\s*(.*?)\s*-->", re.DOTALL)

# Match a 6-digit hex color (#RRGGBB), word-bounded
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")

# Match any external <link> or <script> referencing an http(s) URL
EXTERNAL_LINK = re.compile(
    r"<(?:link|script)[^>]+https?://[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
