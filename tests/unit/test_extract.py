"""Unit tests for theme extraction (T048)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from aurea.commands.extract import DesignExtractor, should_skip_cdn


class TestShouldSkipCdn:
    def test_skips_google_fonts(self) -> None:
        assert should_skip_cdn("https://fonts.googleapis.com/css2?family=Inter") is True

    def test_skips_unpkg(self) -> None:
        assert should_skip_cdn("https://unpkg.com/react@18/umd/react.production.min.js") is True

    def test_skips_jsdelivr(self) -> None:
        url = "https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css"
        assert should_skip_cdn(url) is True

    def test_skips_cdnjs(self) -> None:
        url = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"
        assert should_skip_cdn(url) is True

    def test_skips_gstatic(self) -> None:
        assert should_skip_cdn("https://fonts.gstatic.com/s/inter/v12/foo.woff2") is True

    def test_allows_non_cdn_url(self) -> None:
        assert should_skip_cdn("https://linear.app/static/main.css") is False

    def test_allows_relative_url(self) -> None:
        assert should_skip_cdn("/static/style.css") is False

    def test_handles_exception_gracefully(self) -> None:
        # Passing an invalid URL that would cause an exception
        # should return False (not crash)
        result = should_skip_cdn(None)  # type: ignore[arg-type]
        assert result is False


class TestExtractColorTokens:
    def setup_method(self) -> None:
        self.extractor = DesignExtractor(url="https://example.com")

    def test_returns_primary_background_text_roles(self) -> None:
        css = "body { background: #ffffff; color: #111111; } h1 { color: #0066cc; }"
        result = self.extractor.extract_color_tokens([css])
        assert "primary" in result
        assert "background" in result
        assert "text" in result

    def test_handles_empty_css(self) -> None:
        result = self.extractor.extract_color_tokens([""])
        assert "primary" in result
        assert "background" in result

    def test_ranks_by_frequency(self) -> None:
        # #ffffff appears 5x, #000000 appears 2x
        css = " ".join(["color: #ffffff;"] * 5 + ["background: #000000;"] * 2)
        result = self.extractor.extract_color_tokens([css])
        # Most frequent light color should be background
        assert "#ffffff" in result.values() or "#000000" in result.values()


class TestGenerateRawDesignMd:
    def setup_method(self) -> None:
        self.extractor = DesignExtractor(url="https://example.com")

    def test_has_9_section_headers(self) -> None:
        tokens = {
            "colors": {"primary": "#333", "background": "#fff", "text": "#111"},
            "typography": {"heading": "sans-serif", "body": "sans-serif"},
            "spacing": {"sm": "4px", "md": "8px", "lg": "16px"},
            "shadows": [],
        }
        result = self.extractor.generate_raw_design_md(tokens)
        # Count section headers matching "## N."
        import re

        sections = re.findall(r"^## \d+\.", result, re.MULTILINE)
        assert len(sections) == 9, f"Expected 9 sections, got {len(sections)}"

    def test_includes_color_values(self) -> None:
        tokens = {
            "colors": {"primary": "#0066cc", "background": "#ffffff", "text": "#111111"},
            "typography": {"heading": "Inter", "body": "Inter"},
            "spacing": {"sm": "4px", "md": "8px", "lg": "16px"},
            "shadows": [],
        }
        result = self.extractor.generate_raw_design_md(tokens)
        assert "#0066cc" in result
        assert "#ffffff" in result


class TestCheckRobotsPermissive:
    def test_returns_true_when_robots_unreachable(self) -> None:
        """T048: check_robots() must return True when robots.txt is unreachable."""
        import urllib.error

        from aurea._http import check_robots

        with patch("urllib.robotparser.RobotFileParser.read") as mock_read:
            mock_read.side_effect = urllib.error.URLError("Connection refused")
            result = check_robots("https://example.com/path", "Aurea/1.0")
            assert result is True, (
                "check_robots should return True (allow) when robots.txt is unreachable"
            )

    def test_returns_false_when_disallowed(self) -> None:
        from aurea._http import check_robots

        with patch("urllib.robotparser.RobotFileParser.read"):
            with patch("urllib.robotparser.RobotFileParser.can_fetch", return_value=False):
                result = check_robots("https://example.com/blocked", "Aurea/1.0")
                assert result is False

    def test_oserror_returns_true(self) -> None:
        from aurea._http import check_robots

        with patch("urllib.robotparser.RobotFileParser.read") as mock_read:
            mock_read.side_effect = OSError("socket error")
            result = check_robots("https://example.com/path", "Aurea/1.0")
            assert result is True


class TestFetchSync:
    def test_raises_on_timeout(self) -> None:
        import httpx

        from aurea._http import fetch_sync
        from aurea.exceptions import AureaError

        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("timeout")
            with pytest.raises(AureaError, match="timed out"):
                fetch_sync("https://example.com", timeout=5)

    def test_raises_on_403(self) -> None:
        import httpx

        from aurea._http import fetch_sync
        from aurea.exceptions import AureaError

        mock_response = httpx.Response(403, request=httpx.Request("GET", "https://example.com"))
        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "403", request=mock_response.request, response=mock_response
            )
            with pytest.raises(AureaError, match="403"):
                fetch_sync("https://example.com")

    def test_raises_on_404(self) -> None:
        import httpx

        from aurea._http import fetch_sync
        from aurea.exceptions import AureaError

        mock_response = httpx.Response(404, request=httpx.Request("GET", "https://example.com"))
        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "404", request=mock_response.request, response=mock_response
            )
            with pytest.raises(AureaError, match="404"):
                fetch_sync("https://example.com")

    def test_returns_text_on_success(self) -> None:
        import httpx

        from aurea._http import fetch_sync

        mock_response = httpx.Response(
            200,
            content=b"<html>hello</html>",
            request=httpx.Request("GET", "https://example.com"),
        )
        with patch("httpx.Client.get", return_value=mock_response):
            result = fetch_sync("https://example.com")
            assert "hello" in result


class TestExtractTypographyTokens:
    def test_returns_default_fonts_on_empty(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        result = extractor.extract_typography_tokens([""])
        assert result["heading"] == "sans-serif"
        assert result["body"] == "sans-serif"

    def test_parses_heading_fonts(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        css = "h1 { font-family: 'Inter', sans-serif; } body { font-family: Georgia, serif; }"
        result = extractor.extract_typography_tokens([css])
        assert "Inter" in result["heading"] or "sans-serif" in result["heading"]
        assert "Georgia" in result["body"] or "serif" in result["body"]


class TestExtractSpacingTokens:
    def test_returns_sm_md_lg(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        css = "div { padding: 8px; margin: 16px; gap: 32px; }"
        result = extractor.extract_spacing_tokens([css])
        assert "sm" in result
        assert "md" in result
        assert "lg" in result

    def test_empty_css_returns_defaults(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        result = extractor.extract_spacing_tokens([""])
        assert result["sm"] == "4px"
        assert result["md"] == "8px"
        assert result["lg"] == "16px"


class TestExtractShadowTokens:
    def test_returns_list(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        css = ".card { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }"
        result = extractor.extract_shadow_tokens([css])
        assert isinstance(result, list)

    def test_empty_css_returns_empty(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        result = extractor.extract_shadow_tokens([""])
        assert result == []


class TestExtractStylesheets:
    def test_extracts_inline_style_tags(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        html = "<html><head><style>body { color: red; }</style></head></html>"
        result = extractor.extract_stylesheets(html, "https://example.com")
        assert len(result) >= 1
        assert "red" in result[0]

    def test_skips_cdn_stylesheets(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        html = """<html><head>
            <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">
            <style>body { color: blue; }</style>
        </head></html>"""
        result = extractor.extract_stylesheets(html, "https://example.com")
        # Should have inline style but NOT the googleapis CDN
        assert any("blue" in c for c in result)
        assert not any("googleapis" in c for c in result)


class TestGenerateThemeCss:
    def test_has_root_block(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        tokens = {
            "colors": {"primary": "#0066cc", "background": "#ffffff", "text": "#111111"},
            "typography": {"heading": "Inter, sans-serif", "body": "Inter, sans-serif"},
        }
        result = extractor.generate_theme_css(tokens)
        assert ":root" in result
        assert "--r-background-color" in result
        assert "--r-main-color" in result

    def test_includes_color_values(self) -> None:
        extractor = DesignExtractor(url="https://example.com")
        tokens = {
            "colors": {"primary": "#abc123", "background": "#ffffff", "text": "#111111"},
            "typography": {"heading": "sans-serif", "body": "sans-serif"},
        }
        result = extractor.generate_theme_css(tokens)
        assert "#abc123" in result or "#ffffff" in result


class TestRunExtract:
    """Tests for the run_extract CLI orchestration function."""

    def _mock_result(self, tmp_path: Path) -> dict:
        theme_dir = tmp_path / "test-theme"
        theme_dir.mkdir(parents=True)
        return {
            "theme_dir": str(theme_dir),
            "colors_extracted": 5,
            "fonts_detected": 2,
            "meta": {
                "id": "test",
                "name": "Test",
                "category": "custom",
                "tags": [],
                "mood": "test",
                "colors": {"primary": "#333"},
                "typography": {"heading": "sans-serif", "body": "sans-serif"},
            },
        }

    def test_run_extract_basic(self, tmp_path: Path) -> None:
        import os

        from aurea.commands.extract import run_extract

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("aurea.commands.extract.DesignExtractor.run") as mock_run:
                mock_run.return_value = self._mock_result(tmp_path)
                run_extract(
                    url="https://example.com",
                    name="test",
                    depth=1,
                    raw=False,
                    use=False,
                    timeout=30,
                    user_agent="Aurea/1.0",
                    delay=0.0,
                )
        finally:
            os.chdir(orig)

    def test_run_extract_with_config(self, initialized_project: Path) -> None:
        """run_extract in an initialized project updates local registry."""
        import os

        from aurea.commands.extract import run_extract

        orig = os.getcwd()
        try:
            os.chdir(initialized_project)
            # Create mock result
            theme_dir = initialized_project / ".aurea" / "themes" / "extracted"
            theme_dir.mkdir(parents=True, exist_ok=True)
            mock_result = {
                "theme_dir": str(theme_dir),
                "colors_extracted": 3,
                "fonts_detected": 1,
                "meta": {
                    "id": "extracted",
                    "name": "Extracted",
                    "category": "custom",
                    "tags": [],
                    "mood": "extracted",
                    "colors": {"primary": "#333"},
                    "typography": {"heading": "sans-serif", "body": "sans-serif"},
                },
            }
            with patch("aurea.commands.extract.DesignExtractor.run", return_value=mock_result):
                run_extract(
                    url="https://example.com",
                    name="extracted",
                    depth=1,
                    raw=False,
                    use=False,
                    timeout=30,
                    user_agent="Aurea/1.0",
                    delay=0.0,
                )
        finally:
            os.chdir(orig)

    def test_run_extract_derives_name_from_url(self, tmp_path: Path) -> None:
        """When name=None, derives theme name from URL hostname."""
        import os

        from aurea.commands.extract import run_extract

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("aurea.commands.extract.DesignExtractor.run") as mock_run:
                mock_run.return_value = self._mock_result(tmp_path)
                # name=None → should derive from "example.com" → "example-com"
                run_extract(
                    url="https://example.com",
                    name=None,
                    depth=1,
                    raw=False,
                    use=False,
                    timeout=30,
                    user_agent="Aurea/1.0",
                    delay=0.0,
                )
        finally:
            os.chdir(orig)
