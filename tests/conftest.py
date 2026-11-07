"""Minimal scaffolding so YOU can write the tests.

Provides:
  live_server / base_url -> starts the app on a free port (or uses BASE_URL if set)
  _reset_state (autouse)  -> reseeds the data before every test

pytest-playwright already gives you: page, context, browser, playwright, expect via
playwright.sync_api. `page.goto("/books")` works because base_url is set here.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    external = os.getenv("BASE_URL")
    if external:
        yield external.rstrip("/")
        return

    port = _free_port()
    env = {**os.environ, "PORT": str(port), "ENABLE_TEST_ROUTES": "1"}
    (ROOT / "reports").mkdir(exist_ok=True)
    log_path = ROOT / "reports" / f"server-{port}.log"
    with open(log_path, "w") as log:
        proc = subprocess.Popen(
            [sys.executable, "run.py"], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT
        )
        url = f"http://127.0.0.1:{port}"
        try:
            deadline = time.time() + 20
            while time.time() < deadline:
                if proc.poll() is not None:
                    pytest.fail(f"Server exited early:\n{log_path.read_text()}")
                try:
                    if requests.get(f"{url}/api/health", timeout=1).ok:
                        break
                except requests.ConnectionError:
                    time.sleep(0.2)
            else:
                pytest.fail("Server did not become healthy in 20s")
            yield url
        finally:
            proc.terminate()
            proc.wait(timeout=5)


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server


@pytest.fixture(autouse=True)
def _reset_state(live_server):
    requests.post(f"{live_server}/api/test/reset", timeout=5).raise_for_status()
