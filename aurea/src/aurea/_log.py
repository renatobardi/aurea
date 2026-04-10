"""Aurea logging configuration — structured output to stderr."""

import logging

from rich.console import Console
from rich.logging import RichHandler

_console = Console(stderr=True)

_handler = RichHandler(
    console=_console,
    show_time=False,
    show_path=False,
    show_level=False,
    markup=True,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[_handler],
)

_log = logging.getLogger("aurea")
_log.setLevel(logging.INFO)

__all__ = ["_log"]
