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
from itertools import count
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


@pytest.fixture(scope="session")
def api_client(base_url):
    """Provide a requests-based client to tests using relative API paths.

    Example::

        def test_health(api_client):
            response = api_client.get("/api/health")
            assert response.ok
    """
    class APIClient(requests.Session):
        def __init__(self, base_url):
            super().__init__()
            self.base_url = base_url.rstrip("/")

        def request(self, method, url, *args, **kwargs):
            url = url if url.startswith(("http://", "https://")) else f"{self.base_url}/{url.lstrip('/')}"
            return super().request(method, url, *args, **kwargs)

    return APIClient(base_url)


@pytest.fixture
def auth_token(request, api_client):
    """Return an admin or user token.

    Choose a role with indirect parametrization, e.g.:
        @pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
        def test_admin(api_client, auth_token):
            api_client.get("/api/admin", headers={"Authorization": f"Bearer {auth_token}"})
    Omitting the parameter returns a user token.
    """
    role = getattr(request, "param", "user")
    if role not in ("admin", "user"):
        raise ValueError("auth_token must be 'admin' or 'user'")

    response = api_client.post(
        "/api/auth/login",
        json={"username": f"{role}", "password": f"{role}123"},
    )
    response.raise_for_status()
    return response.json()["token"]


@pytest.fixture
def username():
    return "user"


@pytest.fixture
def password():
    return "user123"


@pytest.fixture
def logged_in_page(page, username, password, base_url):
    """Return a browser page signed in with the supplied credentials."""
    page.goto(f"{base_url}/login")
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.get_by_role("button", name="Login").click()
    return page


@pytest.fixture
def book_factory():
    """Return valid book payloads with unique ISBN-13 values by default.

    Example test usage::

        def test_book_payload(book_factory):
            book = book_factory()
            assert book["title"].startswith("Test Book ")
            assert len(book["isbn"]) == 13

        def test_book_with_known_isbn(book_factory):
            book = book_factory(isbn="9780306406157")
            assert book["isbn"] == "9780306406157"
    """
    isbn_bodies = count(978000000000)

    def make_book(isbn=None):
        if isbn is None:
            body = str(next(isbn_bodies))
            checksum = sum(
                int(digit) * (1 if index % 2 == 0 else 3)
                for index, digit in enumerate(body)
            )
            isbn = f"{body}{(10 - checksum % 10) % 10}"

        return {
            "title": f"Test Book {isbn}",
            "author": "Test Author",
            "isbn": isbn,
            "category": "Fiction",
        }

    return make_book



