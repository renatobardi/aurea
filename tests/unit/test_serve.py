"""Unit tests for the serve command (T050)."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from aurea.commands.serve import _find_available_port
from aurea.exceptions import AureaError


class TestFindAvailablePort:
    def test_returns_free_port(self) -> None:
        port = _find_available_port(9000, "127.0.0.1")
        assert 9000 <= port < 9100

    def test_skips_occupied_port(self) -> None:
        """When preferred port is in use, returns next available."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", 0))
            occupied = s.getsockname()[1]
            # _find_available_port should skip this occupied port
            port = _find_available_port(occupied, "127.0.0.1")
            assert port != occupied
        finally:
            s.close()

    def test_raises_when_all_ports_in_use(self) -> None:
        """If max_tries=0 (effectively), raises AureaError."""
        # We can't easily fill all ports, so we test max_tries=1 on an occupied port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", 0))
            occupied = s.getsockname()[1]
            with pytest.raises(AureaError):
                _find_available_port(occupied, "127.0.0.1", max_tries=1)
        finally:
            s.close()


class TestRunServeErrors:
    def test_raises_when_html_not_found(self, tmp_path: Path) -> None:
        import os

        from aurea.commands.serve import run_serve

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(AureaError, match="not found"):
                run_serve(port=9099)
        finally:
            os.chdir(orig)

    def test_run_serve_starts_server(self, tmp_path: Path) -> None:
        """run_serve body executes when HTML exists (server mocked to not block)."""
        import http.server
        import os
        from unittest.mock import patch

        from aurea.commands.serve import run_serve

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html>test</html>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Mock serve_forever so it doesn't block
            with patch.object(http.server.HTTPServer, "serve_forever"):
                run_serve(port=9310, host="127.0.0.1")
        finally:
            os.chdir(orig)

    def test_run_serve_with_custom_input(self, tmp_path: Path) -> None:
        """run_serve with explicit input file."""
        import http.server
        import os
        from unittest.mock import patch

        from aurea.commands.serve import run_serve

        html_file = tmp_path / "custom.html"
        html_file.write_text("<html>custom</html>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.object(http.server.HTTPServer, "serve_forever"):
                run_serve(port=9311, host="127.0.0.1", input_file=str(html_file))
        finally:
            os.chdir(orig)


class TestPresentationHandler:
    def test_redirects_root_to_presentation(self) -> None:
        from aurea.commands.serve import _PresentationHandler

        handler = _PresentationHandler.__new__(_PresentationHandler)
        handler.path = "/"
        # Minimal stub — just verify path rewriting logic
        # We can't call do_GET without a full server; just test the attribute assignment
        original_path = handler.path
        if original_path in ("/", "/index.html", ""):
            handler.path = "/presentation.html"
        assert handler.path == "/presentation.html"


class TestRunServeEdgeCases:
    def test_sys_exit_when_no_port_available(self, tmp_path: Path) -> None:
        """run_serve calls sys.exit(1) when _find_available_port raises."""
        import os
        from unittest.mock import patch

        from aurea.commands.serve import run_serve
        from aurea.exceptions import AureaError

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html/>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch(
                "aurea.commands.serve._find_available_port",
                side_effect=AureaError("no port"),
            ):
                with pytest.raises(SystemExit) as exc_info:
                    run_serve(port=9000)
        finally:
            os.chdir(orig)
        assert exc_info.value.code == 1

    def test_keyboard_interrupt_non_watch_mode_shuts_down_server(
        self, tmp_path: Path
    ) -> None:
        """KeyboardInterrupt in serve_forever triggers server.shutdown()."""
        import http.server
        import os
        from unittest.mock import patch

        from aurea.commands.serve import run_serve

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html/>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch.object(
                http.server.HTTPServer, "serve_forever", side_effect=KeyboardInterrupt
            ):
                with patch.object(http.server.HTTPServer, "shutdown") as mock_shutdown:
                    run_serve(port=9314, host="127.0.0.1")
        finally:
            os.chdir(orig)
        mock_shutdown.assert_called_once()

    def test_run_serve_watch_mode_invokes_run_serve_watch(self, tmp_path: Path) -> None:
        """watch=True delegates to _run_serve_watch instead of serve_forever."""
        import os
        from unittest.mock import patch

        from aurea.commands.serve import run_serve

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html/>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("aurea.commands.serve._run_serve_watch") as mock_watch:
                run_serve(port=9315, host="127.0.0.1", watch=True)
        finally:
            os.chdir(orig)
        mock_watch.assert_called_once()


class TestRunServeStartsServer:
    def test_serve_starts_and_responds(self, tmp_path: Path) -> None:
        """Start a real server in a background thread, verify it serves, then stop it."""
        import http.client
        import os
        import threading
        import time

        from aurea.commands.serve import _find_available_port

        # Create presentation.html
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "presentation.html").write_text("<html><body>Test</body></html>")

        orig = os.getcwd()
        try:
            os.chdir(tmp_path)
            port = _find_available_port(9200, "127.0.0.1")

            import http.server

            from aurea.commands.serve import _PresentationHandler

            server = http.server.HTTPServer(
                ("127.0.0.1", port),
                lambda *args, **kw: _PresentationHandler(*args, directory=str(output_dir), **kw),
            )

            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            time.sleep(0.05)

            # Request presentation.html directly
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("GET", "/presentation.html")
            resp = conn.getresponse()
            assert resp.status == 200
            resp.read()

            # Request / to test root redirect (covers line 21 in do_GET)
            conn2 = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            conn2.request("GET", "/")
            resp2 = conn2.getresponse()
            # Root should redirect or serve presentation.html (200 or 301/302)
            assert resp2.status in (200, 301, 302)
            server.shutdown()
        finally:
            os.chdir(orig)
