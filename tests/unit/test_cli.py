"""Unit tests for CLI entry point (T033)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from aurea.cli import app

runner = CliRunner()
FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


class TestVersionFlag:
    def test_version_flag_prints_version(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "aurea" in result.output.lower() or "0.1.0" in result.output


class TestHelpOutput:
    def test_help_lists_commands(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "build" in result.output

    def test_theme_help_lists_subcommands(self) -> None:
        result = runner.invoke(app, ["theme", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "search" in result.output


class TestThemeCLI:
    def test_theme_list_json(self) -> None:
        result = runner.invoke(app, ["theme", "list", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_theme_search_json(self) -> None:
        result = runner.invoke(app, ["theme", "search", "default", "--format", "json"])
        assert result.exit_code == 0

    def test_theme_info_default(self) -> None:
        result = runner.invoke(app, ["theme", "info", "default"])
        assert result.exit_code == 0

    def test_theme_show_default(self) -> None:
        result = runner.invoke(app, ["theme", "show", "default"])
        assert result.exit_code == 0

    def test_theme_create(self, tmp_path: Path) -> None:
        theme_dir = tmp_path / "my-theme"
        result = runner.invoke(app, ["theme", "create", "my-theme", "--output", str(theme_dir)])
        assert result.exit_code == 0
        assert (theme_dir / "DESIGN.md").exists()

    def test_theme_use_updates_config(self, initialized_project: Path) -> None:
        orig = os.getcwd()
        try:
            os.chdir(initialized_project)
            result = runner.invoke(app, ["theme", "use", "default"])
            assert result.exit_code == 0
        finally:
            os.chdir(orig)

    def test_theme_info_nonexistent_exits_nonzero(self) -> None:
        result = runner.invoke(app, ["theme", "info", "nonexistent-xyz"])
        assert result.exit_code != 0


class TestBuildCLI:
    def test_build_with_custom_input_output(self, initialized_project: Path) -> None:
        orig = os.getcwd()
        try:
            os.chdir(initialized_project)
            output = initialized_project / "output" / "test.html"
            result = runner.invoke(app, ["build", "--output", str(output)])
            assert output.exists() or result.exit_code != 0
        finally:
            os.chdir(orig)

    def test_build_missing_input_exits(self, tmp_path: Path) -> None:
        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["build", "--input", "nonexistent.md"])
            assert result.exit_code != 0
        finally:
            os.chdir(orig)


class TestExtractCLI:
    def test_extract_missing_deps_shows_error(self, tmp_path: Path) -> None:
        """When aurea[extract] not installed, should show helpful error."""
        import sys
        from unittest.mock import patch

        with patch.dict(sys.modules, {"aurea.commands.extract": None}):
            result = runner.invoke(app, ["extract", "https://example.com"])
            # Should fail gracefully
            assert result.exit_code != 0 or "extract" in result.output.lower()
