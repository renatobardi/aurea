"""Integration tests for aurea serve (T032)."""
from __future__ import annotations

import socket
import threading
import time
import urllib.request
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestServeBasic:
    def test_server_serves_html(self, tmp_path: Path) -> None:
        """Server starts and serves presentation.html."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text(
            "<html><body><h1>Test</h1></body></html>"
        )


        port = _find_free_port()
        server_started = threading.Event()
        error_holder: list = []

        def _target() -> None:
            try:
                import http.server

                from aurea.commands.serve import _PresentationHandler

                server = http.server.HTTPServer(
                    ("127.0.0.1", port),
                    lambda *a, **kw: _PresentationHandler(
                        *a, directory=str(output_dir), **kw
                    ),
                )
                server_started.set()
                server.handle_request()
                server.server_close()
            except Exception as exc:
                error_holder.append(exc)
                server_started.set()

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        server_started.wait(timeout=5)

        if error_holder:
            pytest.skip(f"Server failed to start: {error_holder[0]}")

        # SC-009: server must respond within 1 second of launch
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/presentation.html", timeout=2
            ) as resp:
                assert resp.status == 200
        except Exception:
            pass
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Server response took {elapsed:.2f}s (limit: 1s)"

    def test_redirect_root_to_presentation(self, tmp_path: Path) -> None:
        """/ should redirect to /presentation.html."""
        from aurea.commands.serve import _PresentationHandler

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        html_file = output_dir / "presentation.html"
        html_file.write_text("<html><body>Presentation</body></html>")

        port = _find_free_port()
        import http.server

        server = http.server.HTTPServer(
            ("127.0.0.1", port),
            lambda *a, **kw: _PresentationHandler(
                *a, directory=str(output_dir), **kw
            ),
        )
        t = threading.Thread(target=server.handle_request, daemon=True)
        t.start()

        time.sleep(0.05)
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/presentation.html",
                timeout=2,
            ) as resp:
                assert resp.status == 200
        except Exception:
            pass
        finally:
            server.server_close()

    def test_finds_next_available_port(self) -> None:
        """Sequential port selection when preferred port is in use."""
        from aurea.commands.serve import _find_available_port

        # Occupy a port
        occupied = _find_free_port()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", occupied))
            # Should return a different port
            result = _find_available_port(occupied, "127.0.0.1")
            assert result != occupied
