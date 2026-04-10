"""HTTP utilities — robots.txt checking and synchronous page fetching."""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.robotparser

from aurea.exceptions import AureaError


def check_robots(url: str, user_agent: str = "Aurea/1.0") -> bool:
    """Return True if *url* is allowed for *user_agent* per robots.txt.

    If the robots.txt is unreachable (URLError, non-200, timeout), returns
    True (permissive fallback) — callers should proceed rather than blocking
    on a missing or inaccessible robots.txt.
    """
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except (urllib.error.URLError, OSError):
        # Unreachable or non-200 — allow by default
        return True
    return rp.can_fetch(user_agent, url)


def fetch_sync(url: str, user_agent: str = "Aurea/1.0", timeout: int = 30) -> str:
    """Fetch *url* synchronously and return the response body as a string.

    Raises AureaError for timeouts, 403, and 404 responses.
    httpx is lazy-imported because it lives in the [extract] optional group.
    """
    try:
        import httpx
    except ImportError:
        raise AureaError(
            "httpx is not installed. Run: pip install aurea[extract]"
        )

    headers = {"User-Agent": user_agent}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except httpx.TimeoutException:
        raise AureaError(
            f"Request timed out after {timeout}s. Try --timeout {timeout * 2}"
        )
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        if code == 403:
            raise AureaError(
                "HTTP 403 forbidden — site may require authentication"
            )
        if code == 404:
            raise AureaError("HTTP 404 — URL not found")
        raise AureaError(f"HTTP {code} error fetching {url}")
