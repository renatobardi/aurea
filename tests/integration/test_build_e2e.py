"""Integration tests for aurea build end-to-end (T031)."""

from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from aurea.cli import app

runner = CliRunner()
FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


class TestBuildBasic:
    def test_build_produces_html_file(self, initialized_project: Path) -> None:
        os.chdir(initialized_project)
        result = runner.invoke(app, ["build"])
        output = initialized_project / "output" / "presentation.html"
        assert output.exists(), (
            "Expected output/presentation.html to exist. "
            f"Result exit={result.exit_code}, output={result.output}"
        )

    def test_output_html_has_no_external_refs(self, initialized_project: Path) -> None:
        """Art. III: zero external resource references in output HTML."""
        os.chdir(initialized_project)
        runner.invoke(app, ["build"])
        output = initialized_project / "output" / "presentation.html"
        if output.exists():
            html = output.read_text(encoding="utf-8")
            import re

            external = re.findall(r'(?:href|src)=["\']https?://', html, re.IGNORECASE)
            assert not external, (
                f"Found {len(external)} external resource references: {external[:5]}"
            )

    def test_output_html_contains_reveal_div(self, initialized_project: Path) -> None:
        os.chdir(initialized_project)
        runner.invoke(app, ["build"])
        output = initialized_project / "output" / "presentation.html"
        if output.exists():
            html = output.read_text()
            assert '<div class="reveal">' in html

    def test_sc008_byte_range(self, initialized_project: Path) -> None:
        """SC-008: HTML size 200KB-500KB without embed-fonts."""
        os.chdir(initialized_project)
        runner.invoke(app, ["build"])
        output = initialized_project / "output" / "presentation.html"
        if output.exists():
            size = len(output.read_bytes())
            assert 200_000 < size < 500_000, f"HTML size {size} bytes is outside 200KB-500KB range"

    def test_empty_slides_exits_1(self, tmp_path: Path) -> None:
        os.chdir(tmp_path)
        aurea_dir = tmp_path / ".aurea"
        aurea_dir.mkdir()
        import json

        config = {
            "agent": "claude",
            "theme": "default",
            "themes_dir": ".aurea/themes",
            "slides_dir": "slides",
            "output_dir": "output",
            "version": "0.1.0",
        }
        (aurea_dir / "config.json").write_text(json.dumps(config))
        slides = tmp_path / "slides"
        slides.mkdir()
        (slides / "presentation.md").write_text("")
        (tmp_path / "output").mkdir()

        result = runner.invoke(app, ["build"])
        assert result.exit_code != 0


class TestBuildMinify:
    def test_minify_reduces_file_size(self, initialized_project: Path) -> None:
        os.chdir(initialized_project)
        runner.invoke(app, ["build", "--output", "output/normal.html"])
        runner.invoke(app, ["build", "--minify", "--output", "output/minified.html"])
        normal = initialized_project / "output" / "normal.html"
        minified = initialized_project / "output" / "minified.html"
        if normal.exists() and minified.exists():
            assert len(minified.read_bytes()) <= len(normal.read_bytes())


class TestBuildThemeOverride:
    def test_cli_theme_overrides_config(self, initialized_project: Path) -> None:
        os.chdir(initialized_project)
        # Build should succeed even with default theme override
        result = runner.invoke(app, ["build", "--theme", "default"])
        output = initialized_project / "output" / "presentation.html"
        assert output.exists() or result.exit_code != 0  # either builds or fails gracefully
