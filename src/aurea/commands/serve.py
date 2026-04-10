# IMPORTANT: Do NOT use `from __future__ import annotations` in this file.
# Typer commands in this module require typing_extensions.Annotated at runtime.
# The future import causes TypeError on Python 3.8 (Art. I exception).
import http.server
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from aurea._log import _log
from aurea.exceptions import AureaError


class _PresentationHandler(http.server.SimpleHTTPRequestHandler):
    """Serve from a fixed directory; redirect / to /presentation.html."""

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html", ""):
            self.path = "/presentation.html"
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        # Suppress default request logging — use aurea logger instead
        pass


def _find_available_port(preferred: int, host: str, max_tries: int = 100) -> int:
    """Return the first available port starting from *preferred*."""
    for port in range(preferred, preferred + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                _log.info("Port %d in use, trying %d...", port, port + 1)
    raise AureaError(f"Error: no available port in range {preferred}-{preferred + max_tries - 1}")


def run_serve(
    port: int = 8000,
    host: str = "127.0.0.1",
    watch: bool = False,
    input_file: Optional[str] = None,
) -> None:
    """Start a local HTTP server to serve the presentation."""
    cwd = Path.cwd()
    html_path = Path(input_file) if input_file else cwd / "output" / "presentation.html"

    if not html_path.exists():
        raise AureaError(f"Error: '{html_path}' not found. Run 'aurea build' first")

    serve_dir = html_path.parent

    # Find an available port
    try:
        actual_port = _find_available_port(port, host)
    except AureaError as exc:
        _log.error("%s", exc)
        sys.exit(1)

    handler_class = _PresentationHandler

    server = http.server.HTTPServer(
        (host, actual_port),
        lambda *args, **kwargs: handler_class(*args, directory=str(serve_dir), **kwargs),
    )

    url = f"http://{host}:{actual_port}/presentation.html"
    print(
        f"Serving at {url} \u2014 press Ctrl+C to stop",
        flush=True,
    )

    if watch:
        _run_serve_watch(server=server, serve_dir=serve_dir)
    else:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()


def _run_serve_watch(
    server: http.server.HTTPServer,
    serve_dir: Path,
) -> None:
    """Serve + watch mode: rebuild on file changes with debounce."""
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    cwd = Path.cwd()
    watch_dirs = [
        str(cwd / "slides"),
        str(cwd / ".aurea" / "themes"),
    ]

    _debounce_timer: Optional[threading.Timer] = None
    _lock = threading.Lock()

    def _rebuild() -> None:
        start = time.perf_counter()
        try:
            from aurea.commands.build import _do_build

            _do_build(
                input_file=None,
                output_file=None,
                theme_override=None,
                minify=False,
                embed_fonts=False,
            )
            _log.info("Rebuilt in %.2fs (watching...)", time.perf_counter() - start)
        except SystemExit:
            pass

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event) -> None:  # type: ignore[override]
            nonlocal _debounce_timer
            with _lock:
                if _debounce_timer:
                    _debounce_timer.cancel()
                _debounce_timer = threading.Timer(0.5, _rebuild)
                _debounce_timer.start()

    observer = Observer()
    handler = _Handler()
    for d in watch_dirs:
        if Path(d).exists():
            observer.schedule(handler, d, recursive=True)

    observer.start()

    # Run HTTP server in background thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        server.shutdown()
    observer.join()
