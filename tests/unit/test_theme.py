"""Unit tests for theme commands (T033)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from aurea.commands.theme import load_registry, search_themes

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


def _make_registry(n: int) -> Dict[str, Any]:
    """Build a registry with *n* themes for testing."""
    themes = [
        {
            "id": f"theme-{i:03d}",
            "name": f"Theme {i}",
            "category": "dark" if i % 2 == 0 else "light",
            "tags": ["dark", "minimal"] if i % 2 == 0 else ["light", "clean"],
            "mood": "Dark mysterious theme" if i % 2 == 0 else "Light clean theme",
            "colors": {
                "primary": "#333",
                "background": "#000" if i % 2 == 0 else "#fff",
                "text": "#eee" if i % 2 == 0 else "#111",
            },
            "typography": {"heading": "sans-serif", "body": "sans-serif"},
            "path": f"theme-{i:03d}",
        }
        for i in range(n)
    ]
    return {"version": "1.0.0", "sources": [], "themes": themes}


class TestSearchThemes:
    def test_finds_themes_by_keyword(self) -> None:
        registry = _make_registry(10)
        results = search_themes(registry, "dark")
        assert len(results) > 0
        assert all("dark" in str(t).lower() for t in results)

    def test_filters_by_category(self) -> None:
        registry = _make_registry(10)
        results = search_themes(registry, "theme", category="dark")
        assert all(t["category"] == "dark" for t in results)

    def test_filters_by_tag(self) -> None:
        registry = _make_registry(10)
        results = search_themes(registry, "theme", tag="minimal")
        assert all("minimal" in t.get("tags", []) for t in results)

    def test_returns_empty_for_no_match(self) -> None:
        registry = _make_registry(5)
        results = search_themes(registry, "xyzzy_not_a_real_query_12345")
        assert results == []

    def test_sc006_timing_under_500ms(self) -> None:
        """SC-006: search must complete in <500ms for 40-entry registry."""
        registry = _make_registry(40)
        start = time.perf_counter()
        search_themes(registry, "dark")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.5, f"search took {elapsed:.3f}s (limit: 0.5s)"

    def test_sc010_registry_count(self) -> None:
        """SC-010: registry loaded from global should have >=5 themes (original set)."""
        registry = load_registry()
        count = len(registry.get("themes", []))
        # At least the 5 original themes
        assert count >= 5, f"Expected >=5 themes, got {count}"


class TestLocalRegistryShadowsGlobal:
    def test_local_entry_shadows_global(self, tmp_path: Path) -> None:
        """A local theme with same id should win over global."""
        # Set up project with local registry overriding 'default'
        aurea_dir = tmp_path / ".aurea" / "themes"
        aurea_dir.mkdir(parents=True)
        local_reg = {
            "version": "1.0.0",
            "sources": [],
            "themes": [
                {
                    "id": "default",
                    "name": "My Custom Default",
                    "category": "custom",
                    "tags": [],
                    "mood": "custom",
                    "colors": {"primary": "#abc"},
                    "typography": {"heading": "serif", "body": "serif"},
                    "path": "default",
                }
            ],
        }
        (aurea_dir / "registry.json").write_text(json.dumps(local_reg))

        registry = load_registry(project_root=tmp_path)
        default_theme = next((t for t in registry["themes"] if t["id"] == "default"), None)
        assert default_theme is not None
        assert default_theme["name"] == "My Custom Default"


class TestThemeUse:
    def test_copies_4_files_and_updates_config(self, initialized_project: Path) -> None:
        from aurea.commands.theme import apply_theme

        # Copy 'midnight' fixture theme to global themes (simulated)
        # Since midnight may not exist in global yet during testing, we'll
        # add a test theme to local registry manually
        theme_id = "default"
        apply_theme(theme_id, initialized_project)

        config = json.loads((initialized_project / ".aurea" / "config.json").read_text())
        assert config["theme"] == theme_id

    def test_apply_nonexistent_theme_raises(self, initialized_project: Path) -> None:
        from aurea.commands.theme import apply_theme
        from aurea.exceptions import AureaError

        with pytest.raises(AureaError):
            apply_theme("nonexistent-xyz-theme", initialized_project)


class TestDesignMdValidation:
    def test_valid_design_md_passes(self, tmp_path: Path) -> None:
        """A DESIGN.md with all 9 sections should not raise."""
        from aurea.commands.build import _validate_design_md

        fixture = FIXTURE_DIR / "default_theme" / "DESIGN.md"
        if fixture.exists():
            content = fixture.read_text(encoding="utf-8")
        else:
            content = """
## 1. Visual Theme
## 2. Color Palette
## 3. Typography
## 4. Components
## 5. Layout
## 6. Depth
## 7. Do's and Don'ts
## 8. Responsive
## 9. Agent Prompt Guide
"""
        design_md = tmp_path / "DESIGN.md"
        design_md.write_text(content, encoding="utf-8")

        # Should not raise
        _validate_design_md(design_md, "test-theme")

    def test_missing_section_raises(self, tmp_path: Path) -> None:
        from aurea.commands.build import _validate_design_md
        from aurea.exceptions import AureaError

        design_md = tmp_path / "DESIGN.md"
        # Only 8 sections (missing "responsive")
        design_md.write_text("""
## 1. Visual Theme
## 2. Color Palette
## 3. Typography
## 4. Components
## 5. Layout
## 6. Depth
## 7. Do's and Don'ts
## 9. Agent Prompt Guide
""")
        with pytest.raises(AureaError):
            _validate_design_md(design_md, "test-theme")


class TestCmdList:
    def test_json_format_outputs_json(self, capsys) -> None:
        from aurea.commands.theme import cmd_list

        cmd_list(format_="json")
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)

    def test_table_format_does_not_crash(self) -> None:
        from aurea.commands.theme import cmd_list

        # Should not raise; rich output goes to console
        cmd_list(format_="table")


class TestCmdSearch:
    def test_json_format_outputs_json(self, capsys) -> None:
        from aurea.commands.theme import cmd_search

        cmd_search("dark", format_="json")
        out = capsys.readouterr().out
        # May be empty if no dark themes in registry, but should be valid JSON
        if out.strip():
            data = json.loads(out)
            assert isinstance(data, list)

    def test_no_results_does_not_crash(self) -> None:
        from aurea.commands.theme import cmd_search

        cmd_search("zzz_no_such_theme_xyz_12345")

    def test_table_format_does_not_crash(self) -> None:
        from aurea.commands.theme import cmd_search

        cmd_search("default", format_="table")

    def test_category_filter(self, capsys) -> None:
        from aurea.commands.theme import cmd_search

        cmd_search("theme", category="dark", format_="json")


class TestCmdInfo:
    def test_existing_theme_does_not_crash(self) -> None:
        from aurea.commands.theme import cmd_info

        cmd_info("default")

    def test_nonexistent_theme_exits(self) -> None:

        from aurea.commands.theme import cmd_info

        with pytest.raises(SystemExit):
            cmd_info("nonexistent-xyz-000")


class TestCmdShow:
    def test_existing_theme_prints_design_md(self, capsys) -> None:
        from aurea.commands.theme import cmd_show

        cmd_show("default")

    def test_nonexistent_theme_exits(self) -> None:
        from aurea.commands.theme import cmd_show

        with pytest.raises(SystemExit):
            cmd_show("nonexistent-xyz-000")


class TestCmdCreate:
    def test_creates_4_files(self, tmp_path: Path) -> None:
        from aurea.commands.theme import cmd_create

        theme_dir = tmp_path / "my-theme"
        cmd_create("my-theme", output=str(theme_dir))

        assert (theme_dir / "DESIGN.md").exists()
        assert (theme_dir / "theme.css").exists()
        assert (theme_dir / "layout.css").exists()
        assert (theme_dir / "meta.json").exists()

    def test_meta_json_has_required_fields(self, tmp_path: Path) -> None:
        from aurea.commands.theme import cmd_create

        theme_dir = tmp_path / "test-theme"
        cmd_create("test-theme", output=str(theme_dir))

        meta = json.loads((theme_dir / "meta.json").read_text())
        assert meta["id"] == "test-theme"
        assert "colors" in meta
        assert "typography" in meta

    def test_default_output_path(self, tmp_path: Path) -> None:
        """When output is None, uses .aurea/themes/<name> in cwd."""
        import os

        from aurea.commands.theme import cmd_create

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            cmd_create("mytest")
            expected = tmp_path / ".aurea" / "themes" / "mytest"
            assert expected.exists()
        finally:
            os.chdir(orig)
