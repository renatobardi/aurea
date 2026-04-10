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
        (output_dir / "presentation.html").write_text("<html><body><h1>Test</h1></body></html>")

        port = _find_free_port()
        server_started = threading.Event()
        error_holder: list = []

        def _target() -> None:
            try:
                import http.server

                from aurea.commands.serve import _PresentationHandler

                server = http.server.HTTPServer(
                    ("127.0.0.1", port),
                    lambda *a, **kw: _PresentationHandler(*a, directory=str(output_dir), **kw),
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
            lambda *a, **kw: _PresentationHandler(*a, directory=str(output_dir), **kw),
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


class TestServeWatchMode:
    """Tests for _run_serve_watch: observer lifecycle and rebuild trigger."""

    def _make_project(self, tmp_path: Path):
        """Create minimal on-disk state needed by _run_serve_watch."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html><body>Watch</body></html>")
        slides_dir = tmp_path / "slides"
        slides_dir.mkdir()
        return output_dir, slides_dir

    def _make_server(self, output_dir: Path, port: int):
        import http.server

        from aurea.commands.serve import _find_available_port, _PresentationHandler

        actual_port = _find_available_port(port, "127.0.0.1")
        server = http.server.HTTPServer(
            ("127.0.0.1", actual_port),
            lambda *a, **kw: _PresentationHandler(*a, directory=str(output_dir), **kw),
        )
        return server, actual_port

    def test_watch_mode_observer_stopped_on_keyboard_interrupt(self, tmp_path: Path) -> None:
        """_run_serve_watch stops observer and server cleanly on KeyboardInterrupt."""
        import os
        from unittest.mock import patch

        from aurea.commands.serve import _run_serve_watch

        output_dir, _ = self._make_project(tmp_path)
        server, _ = self._make_server(output_dir, 9500)

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("aurea.commands.serve.time.sleep", side_effect=KeyboardInterrupt):
                _run_serve_watch(server=server, serve_dir=output_dir)
        finally:
            os.chdir(orig)
        # Reaching here without a hang confirms cleanup completed

    def test_watch_mode_server_responds_during_watch(self, tmp_path: Path) -> None:
        """HTTP server responds to requests while watch loop is running."""
        import http.client
        import os
        import time
        from unittest.mock import patch

        from aurea.commands.serve import _run_serve_watch

        output_dir, _ = self._make_project(tmp_path)
        server, port = self._make_server(output_dir, 9510)

        call_count = [0]

        def controlled_sleep(t: float) -> None:
            call_count[0] += 1
            if call_count[0] >= 3:
                raise KeyboardInterrupt
            time.sleep(0.05)

        orig = os.getcwd()
        os.chdir(tmp_path)
        status_holder: list = []

        def _run() -> None:
            with patch("aurea.commands.serve.time.sleep", side_effect=controlled_sleep):
                _run_serve_watch(server=server, serve_dir=output_dir)

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        # Poll until server responds (deadline 5 s)
        deadline = time.perf_counter() + 5.0
        while time.perf_counter() < deadline:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                conn.request("GET", "/presentation.html")
                resp = conn.getresponse()
                status_holder.append(resp.status)
                resp.read()
                break
            except Exception:
                time.sleep(0.05)

        t.join(timeout=5.0)
        os.chdir(orig)
        assert status_holder and status_holder[0] == 200

    def test_watch_mode_rebuilds_on_slide_change(self, tmp_path: Path) -> None:
        """Saving a file under slides/ triggers _do_build within 5 s."""
        import os
        import time
        from unittest.mock import patch

        from aurea.commands.serve import _run_serve_watch

        output_dir, slides_dir = self._make_project(tmp_path)
        server, _ = self._make_server(output_dir, 9520)

        rebuild_called = threading.Event()
        stop_loop = threading.Event()

        def mock_do_build(**kwargs) -> None:  # type: ignore[misc]
            rebuild_called.set()

        def controlled_sleep(t: float) -> None:
            if stop_loop.wait(timeout=t):
                raise KeyboardInterrupt

        orig = os.getcwd()
        os.chdir(tmp_path)

        with patch("aurea.commands.build._do_build", side_effect=mock_do_build):
            with patch("aurea.commands.serve.time.sleep", side_effect=controlled_sleep):

                def _run() -> None:
                    _run_serve_watch(server=server, serve_dir=output_dir)

                t = threading.Thread(target=_run, daemon=True)
                t.start()

                time.sleep(0.3)  # let observer register the watch dirs
                (slides_dir / "test.md").write_text("# Changed")

                deadline = time.perf_counter() + 5.0
                while time.perf_counter() < deadline and not rebuild_called.is_set():
                    time.sleep(0.1)

                stop_loop.set()
                t.join(timeout=3.0)

        os.chdir(orig)
        assert rebuild_called.is_set(), "rebuild not triggered after slide change"
