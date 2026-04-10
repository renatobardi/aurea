"""Shared pytest fixtures for Aurea tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Return a fresh temporary directory simulating an Aurea project root."""
    return tmp_path


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Return a temporary directory with a minimal initialized Aurea project."""
    aurea_dir = tmp_path / ".aurea"
    themes_dir = aurea_dir / "themes" / "default"
    themes_dir.mkdir(parents=True)
    slides_dir = tmp_path / "slides"
    slides_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Copy fixture theme
    fixture_theme = FIXTURE_DIR / "default_theme"
    if fixture_theme.exists():
        for f in fixture_theme.iterdir():
            shutil.copy(f, themes_dir / f.name)

    # Write config.json
    config: Dict[str, str] = {
        "agent": "claude",
        "theme": "default",
        "themes_dir": ".aurea/themes",
        "slides_dir": "slides",
        "output_dir": "output",
        "version": "0.1.0",
    }
    (aurea_dir / "config.json").write_text(json.dumps(config, indent=2))

    # Write local registry
    registry = {
        "version": "1.0.0",
        "sources": [],
        "themes": [
            {
                "id": "default",
                "name": "Default",
                "category": "general",
                "tags": ["clean", "minimal"],
                "mood": "Neutral",
                "colors": {"primary": "#333", "background": "#fff", "text": "#111"},
                "typography": {"heading": "sans-serif", "body": "sans-serif"},
                "path": "default",
            }
        ],
    }
    (aurea_dir / "themes" / "registry.json").write_text(json.dumps(registry, indent=2))

    # Copy sample slides
    sample = FIXTURE_DIR / "sample_slides.md"
    if sample.exists():
        shutil.copy(sample, slides_dir / "presentation.md")

    return tmp_path
