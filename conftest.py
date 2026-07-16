"""Starts the demo Flask app (examples/app.py) in a background thread so both
tests/ and generated_tests/ can run real Playwright tests against a live
server, matching the default BASE_URL used by generated test files.
"""
from __future__ import annotations

import sys
import threading
import time
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "examples"))

_PORT = 5000
_BASE_URL = f"http://127.0.0.1:{_PORT}"


def _wait_until_ready(url: str, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"demo app never became ready at {url}")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Pin the browser executable to whatever chromium build is actually
    installed locally, since the pinned playwright package version can
    expect a newer build than what's on disk."""
    import glob

    candidates = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    if candidates:
        return {**browser_type_launch_args, "executable_path": candidates[-1]}
    return browser_type_launch_args


@pytest.fixture(scope="session", autouse=True)
def live_demo_server():
    from app import app  # examples/app.py

    thread = threading.Thread(
        target=lambda: app.run(port=_PORT, use_reloader=False),
        daemon=True,
    )
    thread.start()
    _wait_until_ready(_BASE_URL + "/login")
    yield _BASE_URL
