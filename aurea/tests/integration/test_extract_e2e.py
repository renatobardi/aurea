"""Integration tests for aurea extract (T047)."""
from __future__ import annotations

import http.server
import socket
import threading
import time
from pathlib import Path

import pytest


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


_SAMPLE_HTML = """\
<!DOCTYPE html>
<html>
<head>
<style>
:root {
  --bg: #ffffff;
  --text: #111111;
  --primary: #0066cc;
}
body {
  background: #ffffff;
  color: #111111;
  font-family: Inter, sans-serif;
  margin: 16px;
  padding: 8px;
}
h1, h2, h3 {
  color: #0066cc;
  font-family: Inter, sans-serif;
  font-size: 2em;
  margin: 32px 0;
}
p {
  font-family: Georgia, serif;
  color: #222222;
  padding: 4px;
}
.card {
  background: #f5f5f5;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  padding: 16px;
}
</style>
</head>
<body>
<h1>Test Page</h1>
<p>This is a test page for Aurea theme extraction.</p>
<div class="card">
  <h2>Card Title</h2>
  <p>Card content here.</p>
</div>
</body>
</html>
"""


@pytest.fixture
def local_server():
    """Spin up a local HTTP server serving the sample HTML."""
    try:
        import cssutils  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        pytest.skip("extract dependencies not installed")

    port = _find_free_port()

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = _SAMPLE_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


class TestExtractBasic:
    def test_produces_4_theme_files(self, tmp_path: Path, local_server: str) -> None:
        from aurea.commands.extract import DesignExtractor

        extractor = DesignExtractor(url=local_server, timeout=10)
        output_dir = tmp_path / "test-extract"
        extractor.run(output_dir)

        assert (output_dir / "DESIGN.md").exists()
        assert (output_dir / "theme.css").exists()
        assert (output_dir / "layout.css").exists()
        assert (output_dir / "meta.json").exists()

    def test_design_md_has_9_sections(self, tmp_path: Path, local_server: str) -> None:
        import re

        from aurea.commands.extract import DesignExtractor

        extractor = DesignExtractor(url=local_server, timeout=10)
        output_dir = tmp_path / "test-extract"
        extractor.run(output_dir)

        design_md = (output_dir / "DESIGN.md").read_text(encoding="utf-8")
        sections = re.findall(r"^## \d+\.", design_md, re.MULTILINE)
        assert len(sections) == 9

    def test_theme_css_has_custom_properties(self, tmp_path: Path, local_server: str) -> None:
        from aurea.commands.extract import DesignExtractor

        extractor = DesignExtractor(url=local_server, timeout=10)
        output_dir = tmp_path / "test-extract"
        extractor.run(output_dir)

        theme_css = (output_dir / "theme.css").read_text(encoding="utf-8")
        assert "--r-background-color" in theme_css
        assert "--r-main-color" in theme_css

    def test_meta_json_has_colors(self, tmp_path: Path, local_server: str) -> None:
        import json

        from aurea.commands.extract import DesignExtractor

        extractor = DesignExtractor(url=local_server, timeout=10)
        output_dir = tmp_path / "test-extract"
        extractor.run(output_dir)

        meta = json.loads((output_dir / "meta.json").read_text(encoding="utf-8"))
        assert "colors" in meta
        assert len(meta["colors"]) > 0

    def test_sc014_timing(self, tmp_path: Path, local_server: str) -> None:
        """SC-014: full depth-1 extraction must complete in <30 seconds."""
        from aurea.commands.extract import DesignExtractor

        extractor = DesignExtractor(url=local_server, timeout=10)
        output_dir = tmp_path / "test-timing"

        start = time.perf_counter()
        extractor.run(output_dir)
        elapsed = time.perf_counter() - start

        assert elapsed < 30.0, f"Extraction took {elapsed:.2f}s (limit: 30s)"


class TestExtractRobotsBlocking:
    def test_blocked_by_robots_raises(self, tmp_path: Path) -> None:
        """robots.txt blocking should raise AureaError."""
        try:
            from bs4 import BeautifulSoup  # noqa: F401
        except ImportError:
            pytest.skip("bs4 not installed")

        from unittest.mock import patch

        from aurea.commands.extract import DesignExtractor
        from aurea.exceptions import AureaError

        extractor = DesignExtractor(url="https://example.com", timeout=5)

        with patch("aurea.commands.extract.check_robots", return_value=False):
            with pytest.raises(AureaError, match="disallowed by robots.txt"):
                extractor.fetch_page("https://example.com")
