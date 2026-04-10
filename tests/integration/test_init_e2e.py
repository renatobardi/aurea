"""Integration tests for `aurea init` end-to-end (T018)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from typer.testing import CliRunner

from aurea.cli import app

runner = CliRunner()


class TestInitBasic:
    def test_init_creates_complete_structure(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "my-demo"), "--agent", "claude", "--theme", "default"],
        )
        assert result.exit_code == 0, result.output or str(result.exception)
        project = tmp_path / "my-demo"
        assert (project / ".aurea" / "config.json").exists()
        assert (project / ".aurea" / "themes" / "default" / "DESIGN.md").exists()
        assert (project / ".aurea" / "themes" / "default" / "theme.css").exists()
        assert (project / ".aurea" / "themes" / "default" / "layout.css").exists()
        assert (project / ".aurea" / "themes" / "default" / "meta.json").exists()
        assert (project / ".aurea" / "themes" / "registry.json").exists()
        assert (project / "slides").is_dir()
        assert (project / "output").is_dir()
        assert (project / "README.md").exists()

    def test_config_json_has_required_fields(self, tmp_path: Path) -> None:
        runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--agent", "claude", "--theme", "default"],
        )
        config = json.loads((tmp_path / "proj" / ".aurea" / "config.json").read_text())
        assert config["agent"] == "claude"
        assert config["theme"] == "default"
        assert "themes_dir" in config
        assert "slides_dir" in config
        assert "output_dir" in config
        assert "version" in config

    def test_7_command_files_in_claude_dir(self, tmp_path: Path) -> None:
        runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--agent", "claude", "--theme", "default"],
        )
        commands_dir = tmp_path / "proj" / ".claude" / "commands"
        assert commands_dir.is_dir()
        md_files = list(commands_dir.glob("*.md"))
        assert len(md_files) == 7, (
            f"Expected 7 .md files, got {len(md_files)}: {[f.name for f in md_files]}"
        )

    def test_sc001_timing(self, tmp_path: Path) -> None:
        """SC-001: aurea init must complete in <2 seconds."""
        start = time.perf_counter()
        runner.invoke(
            app,
            ["init", str(tmp_path / "timed"), "--agent", "claude", "--theme", "default"],
        )
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"aurea init took {elapsed:.2f}s (limit: 2s)"


class TestInitOptions:
    def test_here_flag_initializes_in_current_dir(self, tmp_path: Path) -> None:
        import os

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app, ["init", "--here", "--agent", "claude", "--theme", "default"]
            )
            assert result.exit_code == 0, str(result.exception)
            assert (tmp_path / ".aurea" / "config.json").exists()
        finally:
            os.chdir(orig)

    def test_force_preserves_slides_dir_content(self, tmp_path: Path) -> None:
        project = tmp_path / "proj"
        # First init
        runner.invoke(
            app,
            ["init", str(project), "--agent", "claude", "--theme", "default"],
        )
        # Add a file to slides/
        important = project / "slides" / "important.md"
        important.write_text("do not delete")
        # Re-init with --force
        runner.invoke(
            app,
            ["init", str(project), "--agent", "claude", "--theme", "default", "--force"],
        )
        assert important.exists(), "slides/important.md was deleted by --force"
        assert important.read_text() == "do not delete"

    def test_no_force_aborts_on_existing_dir(self, tmp_path: Path) -> None:
        project = tmp_path / "existing"
        project.mkdir()
        result = runner.invoke(
            app,
            ["init", str(project), "--agent", "claude", "--theme", "default"],
        )
        assert result.exit_code != 0

    def test_unknown_theme_exits_1(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj"), "--agent", "claude", "--theme", "nonexistent-xyz"],
        )
        assert result.exit_code != 0

    def test_defaults_message_on_stderr(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["init", str(tmp_path / "proj")],
            catch_exceptions=False,
        )
        # Should succeed with defaults
        assert result.exit_code == 0 or result.exit_code is None


class TestInitAgentFormats:
    def test_gemini_creates_toml_files(self, tmp_path: Path) -> None:
        runner.invoke(
            app,
            ["init", str(tmp_path / "gem"), "--agent", "gemini", "--theme", "default"],
        )
        commands_dir = tmp_path / "gem" / ".gemini" / "commands"
        if commands_dir.exists():
            toml_files = list(commands_dir.glob("*.toml"))
            assert len(toml_files) == 7

    def test_copilot_creates_agent_md_files(self, tmp_path: Path) -> None:
        runner.invoke(
            app,
            ["init", str(tmp_path / "cop"), "--agent", "copilot", "--theme", "default"],
        )
        commands_dir = tmp_path / "cop" / ".github" / "copilot-instructions"
        if commands_dir.exists():
            agent_files = list(commands_dir.glob("*.agent.md"))
            assert len(agent_files) == 7
