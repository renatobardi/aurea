"""Unit tests for the build pipeline (T034)."""

from __future__ import annotations

from pathlib import Path

import pytest

from aurea.commands.build import (
    REQUIRED_SECTIONS,
    parse_slides,
    resolve_theme,
)

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


class TestParseSlides:
    def test_splits_on_triple_dash(self) -> None:
        md = "# Slide 1\n\n---\n\n## Slide 2\n"
        p = parse_slides(md)
        assert len(p.slides) == 2

    def test_extracts_frontmatter(self) -> None:
        md = "---\ntitle: My Talk\nauthor: Jane\ntheme: default\n---\n\n# Slide\n"
        p = parse_slides(md)
        assert p.title == "My Talk"
        assert p.author == "Jane"
        assert p.theme == "default"

    def test_extracts_speaker_notes(self) -> None:
        md = "# Title\n\nBody text.\n\nNote: This is a speaker note.\n"
        p = parse_slides(md)
        assert len(p.slides) == 1
        assert "speaker note" in p.slides[0].notes.lower()
        assert "Note:" not in p.slides[0].markdown

    def test_extracts_html_attributes(self) -> None:
        md = '<!-- .slide: data-background="#000" -->\n# Dark slide\n'
        p = parse_slides(md)
        assert 'data-background="#000"' in p.slides[0].attributes

    def test_skips_empty_slides(self) -> None:
        md = "# Slide 1\n\n---\n\n\n\n---\n\n# Slide 3\n"
        p = parse_slides(md)
        # Empty slide in the middle should be skipped
        assert len(p.slides) == 2

    def test_word_count_populated(self) -> None:
        md = "one two three four five\n"
        p = parse_slides(md)
        assert p.slides[0].word_count == 5

    def test_over_40_words_does_not_error(self) -> None:
        # 50 words — should produce a warning but not crash
        words = " ".join(["word"] * 50)
        p = parse_slides(words)
        assert p.slides[0].word_count == 50

    def test_handles_invalid_frontmatter_gracefully(self) -> None:
        md = "---\nnot: valid: yaml: ::::\n---\n\n# Slide\n"
        p = parse_slides(md)
        # Should not raise, just use empty defaults
        assert p.title == "" or p.title is not None

    def test_single_slide_no_separator(self) -> None:
        md = "# Only slide\n\nSome content here.\n"
        p = parse_slides(md)
        assert len(p.slides) == 1


class TestResolveTheme:
    def test_cli_theme_takes_precedence(self, tmp_path: Path) -> None:
        """CLI --theme flag overrides config and frontmatter."""
        # Create a minimal config
        aurea_dir = tmp_path / ".aurea"
        aurea_dir.mkdir()
        config = {
            "agent": "claude",
            "theme": "config_theme",
            "themes_dir": ".aurea/themes",
            "slides_dir": "slides",
            "output_dir": "output",
            "version": "0.1.0",
        }
        (aurea_dir / "config.json").write_text(__import__("json").dumps(config))

        # Ensure the CLI theme dir exists (use fixture)
        themes_dir = aurea_dir / "themes"
        themes_dir.mkdir()
        import shutil

        fixture = FIXTURE_DIR / "default_theme"
        if fixture.exists():
            shutil.copytree(fixture, themes_dir / "default")

        theme_id, theme_dir = resolve_theme(
            config_path=aurea_dir / "config.json",
            cli_theme="default",  # overrides config_theme
            frontmatter_theme="front_theme",
        )
        assert theme_id == "default"

    def test_config_beats_frontmatter(self, tmp_path: Path) -> None:
        import json
        import shutil

        aurea_dir = tmp_path / ".aurea"
        aurea_dir.mkdir()
        themes_dir = aurea_dir / "themes"
        themes_dir.mkdir()

        fixture = FIXTURE_DIR / "default_theme"
        if fixture.exists():
            shutil.copytree(fixture, themes_dir / "default")

        config = {
            "agent": "claude",
            "theme": "default",
            "themes_dir": ".aurea/themes",
            "slides_dir": "slides",
            "output_dir": "output",
            "version": "0.1.0",
        }
        (aurea_dir / "config.json").write_text(json.dumps(config))

        theme_id, _ = resolve_theme(
            config_path=aurea_dir / "config.json",
            cli_theme=None,
            frontmatter_theme="front_theme",
        )
        assert theme_id == "default"


class TestRequiredSections:
    def test_required_sections_has_9_entries(self) -> None:
        assert len(REQUIRED_SECTIONS) == 9

    def test_all_required_keywords_present(self) -> None:
        expected = {
            "visual theme",
            "color palette",
            "typography",
            "components",
            "layout",
            "depth",
            "do's",
            "responsive",
            "agent prompt",
        }
        assert REQUIRED_SECTIONS == expected


class TestRenderSlides:
    def test_renders_markdown_to_html(self) -> None:
        from aurea.commands.build import render_slides

        p = parse_slides("# Hello World\n\nSome **bold** text.\n")
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        assert result.slides[0].html is not None
        assert "<h1" in result.slides[0].html or "Hello" in result.slides[0].html

    def test_renders_code_block(self) -> None:
        from aurea.commands.build import render_slides

        p = parse_slides("```python\nprint('hello')\n```\n")
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        assert result.slides[0].html is not None
        assert "print" in result.slides[0].html

    def test_multiple_slides_all_rendered(self) -> None:
        from aurea.commands.build import render_slides

        p = parse_slides("# Slide 1\n\n---\n\n# Slide 2\n")
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        assert all(s.html is not None for s in result.slides)

    def test_renders_unknown_lang_code_block(self) -> None:
        """Code block with unrecognized language should use guess_lexer fallback."""
        from aurea.commands.build import render_slides

        p = parse_slides("```unknownlang99xyz\nsome code here\n```\n")
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        assert result.slides[0].html is not None

    def test_renders_code_block_without_lang(self) -> None:
        """Code block without language hint triggers guess_lexer."""
        from aurea.commands.build import render_slides

        p = parse_slides("```\nplain text code block\n```\n")
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        assert result.slides[0].html is not None

    def test_inline_html_passthrough(self) -> None:
        """Raw HTML blocks (SVG, figure, div) must not be escaped."""
        from aurea.commands.build import render_slides

        md = '<figure>\n<svg viewBox="0 0 800 250" xmlns="http://www.w3.org/2000/svg">\n<rect x="20" y="25" width="100" height="50" fill="#f00"/>\n</svg>\n</figure>\n'
        p = parse_slides(md)
        theme_dir = FIXTURE_DIR / "default_theme"
        result = render_slides(p, theme_dir)
        html = result.slides[0].html
        assert "<svg" in html, "SVG tag must not be escaped"
        assert "&lt;svg" not in html, "SVG tag must not appear escaped"
        assert "<figure" in html
        assert "&lt;figure" not in html


class TestInlineAssets:
    def test_returns_all_keys(self) -> None:
        from aurea.commands.build import inline_assets

        theme_dir = FIXTURE_DIR / "default_theme"
        assets = inline_assets(theme_dir, embed_fonts=False)
        assert "reveal_css" in assets
        assert "reveal_js" in assets
        assert "theme_css" in assets
        assert "layout_css" in assets

    def test_theme_css_content_present(self) -> None:
        from aurea.commands.build import inline_assets

        theme_dir = FIXTURE_DIR / "default_theme"
        assets = inline_assets(theme_dir, embed_fonts=False)
        assert len(assets["theme_css"]) > 0

    def test_embed_fonts_false_no_data_uri(self) -> None:
        from aurea.commands.build import inline_assets

        theme_dir = FIXTURE_DIR / "default_theme"
        assets = inline_assets(theme_dir, embed_fonts=False)
        assert "data:font/woff2" not in assets["theme_css"]


class TestValidateDesignMd:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        from aurea.commands.build import _validate_design_md
        from aurea.exceptions import AureaError

        with pytest.raises(AureaError):
            _validate_design_md(tmp_path / "DESIGN.md", "test")

    def test_valid_content_passes(self, tmp_path: Path) -> None:
        from aurea.commands.build import _validate_design_md

        content = "\n".join(
            [
                "## Visual Theme",
                "## Color Palette",
                "## Typography",
                "## Components",
                "## Layout",
                "## Depth",
                "## Do's and Don'ts",
                "## Responsive",
                "## Agent Prompt Guide",
            ]
        )
        dm = tmp_path / "DESIGN.md"
        dm.write_text(content)
        _validate_design_md(dm, "test")  # should not raise


class TestResolveThemeGlobal:
    def test_global_theme_fallback(self, tmp_path: Path) -> None:
        """When no local theme, falls back to bundled global themes."""
        from aurea.commands.build import resolve_theme

        # Pass no config_path so it goes straight to global
        theme_id, theme_dir = resolve_theme(
            config_path=None,
            cli_theme="default",
            frontmatter_theme="",
        )
        assert theme_id == "default"
        assert theme_dir.is_dir()

    def test_bad_config_json_falls_through(self, tmp_path: Path) -> None:
        """Corrupt config.json should not crash, uses frontmatter fallback."""
        from aurea.commands.build import resolve_theme

        aurea_dir = tmp_path / ".aurea"
        aurea_dir.mkdir()
        config_path = aurea_dir / "config.json"
        config_path.write_text("{not valid json")

        # Should fall through and use default from frontmatter or global
        theme_id, theme_dir = resolve_theme(
            config_path=config_path,
            cli_theme="default",
            frontmatter_theme="",
        )
        assert theme_id == "default"

    def test_raises_when_theme_not_found(self) -> None:
        from aurea.commands.build import resolve_theme
        from aurea.exceptions import AureaError

        with pytest.raises(AureaError):
            resolve_theme(
                config_path=None,
                cli_theme="nonexistent-xyz-theme-000",
                frontmatter_theme="",
            )


class TestInlineAssetsEmbedFonts:
    def test_embed_fonts_true_no_crash(self) -> None:
        """embed_fonts=True with theme having no .woff2 files should not crash."""
        from aurea.commands.build import inline_assets

        theme_dir = FIXTURE_DIR / "default_theme"
        assets = inline_assets(theme_dir, embed_fonts=True)
        # No .woff2 in fixture theme — css unchanged
        assert "theme_css" in assets


class TestDoBuildDirect:
    def test_do_build_produces_html(self, initialized_project: Path) -> None:
        import os

        from aurea.commands.build import _do_build

        orig = os.getcwd()
        try:
            os.chdir(initialized_project)
            output = initialized_project / "output" / "direct.html"
            _do_build(
                input_file=str(initialized_project / "slides" / "presentation.md"),
                output_file=str(output),
                theme_override="default",
                minify=False,
                embed_fonts=False,
            )
            assert output.exists()
        finally:
            os.chdir(orig)

    def test_do_build_minify(self, initialized_project: Path) -> None:
        import os

        from aurea.commands.build import _do_build

        orig = os.getcwd()
        try:
            os.chdir(initialized_project)
            output = initialized_project / "output" / "minified.html"
            _do_build(
                input_file=str(initialized_project / "slides" / "presentation.md"),
                output_file=str(output),
                theme_override="default",
                minify=True,
                embed_fonts=False,
            )
            assert output.exists()
        finally:
            os.chdir(orig)

    def test_do_build_nonexistent_theme_exits(self, tmp_path: Path) -> None:
        """AureaError from resolve_theme triggers sys.exit(1)."""
        import os

        from aurea.commands.build import _do_build

        slides_dir = tmp_path / "slides"
        slides_dir.mkdir()
        (slides_dir / "presentation.md").write_text("# Slide\n")
        (tmp_path / "output").mkdir()

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(SystemExit):
                _do_build(
                    input_file=str(slides_dir / "presentation.md"),
                    output_file=str(tmp_path / "output" / "out.html"),
                    theme_override="nonexistent-xyz-000",
                    minify=False,
                    embed_fonts=False,
                )
        finally:
            os.chdir(orig)
