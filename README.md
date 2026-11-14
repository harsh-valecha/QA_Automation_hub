# QA Automation Practice Hub

A small Flask app to practise **Playwright (Python)**, **API testing** and **CI/CD on GitHub Actions**.
The `tests/` tree contains examples organized by API, UI, and end-to-end coverage. The app gives you something to test for every common concept, and every feature is reachable through both the **UI** and the **REST API**.

New to browser automation? Start with the [Playwright with Python cheat sheet](playwright_cheatsheet.md).

## 1. Start

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium

python run.py                          # http://127.0.0.1:5000
```

Log in with `admin / admin123` (can delete) or `user / user123` (cannot delete).

Your first test, to check the setup works (`tests/ui/test_smoke.py`):

```python
from playwright.sync_api import Page, expect

def test_books_page_loads(page: Page):
    page.goto("/books")
    expect(page.get_by_test_id("page-title")).to_have_text("Books")
```
Run it with `pytest`. `tests/conftest.py` starts the app on a free port, sets `base_url` (so `page.goto("/books")` works) and resets the data before every test. Use `BASE_URL=http://... pytest` to test an already running server.

## 2. Features, each testable via UI and API

| Feature | API | UI | Good things to test |
|---|---|---|---|
| Health | `GET /api/health` | footer badge `health-badge` | status, badge text |
| Stats | `GET /api/stats` | widget on `/books` | numbers match in both |
| Login | `POST /api/auth/login` → token | `/login` | 200/401/422, flash message, redirect `?next=` |
| Who am I | `GET /api/auth/me` (Bearer) | header `current-user` | 401 without token, role |
| Logout | drop the token | Logout button | session ends |
| List/search/filter/sort/paginate | `GET /api/books?q&category&min_price&max_price&sort&order&page&per_page` | `/books` | totals, empty state, filters kept across pages |
| Read one | `GET /api/books/{id}` | `/books/{id}` | 200 vs 404 |
| Create | `POST /api/books` | `/books/new` | 201 + `Location`, 422 per field, 409 duplicate ISBN |
| Replace / patch | `PUT` / `PATCH /api/books/{id}` | `/books/{id}/edit` | full vs partial update |
| Delete | `DELETE /api/books/{id}` (admin) | Delete button (confirm dialog) | 204, 403 for `user`, 401 anonymous |
| CSV export | none | `/books/export.csv` link on Playground | download |
| Slow endpoint | `GET /api/slow?ms=2000` | Playground "Load slow data" | waits, spinners, timeouts |
| Reset data | `POST /api/test/reset` (only when `ENABLE_TEST_ROUTES=1`) | none | test isolation |

Seed data: 7 books (3 tech, 2 fiction, 1 science, 1 history), page size 5, so two pages.
API errors always look like `{"error": "...", "message": "...", "details": {...}}`.
Every UI element has a `data-testid`.

## 3. Playwright concepts and where to practise them

| Concept | Where in the app |
|---|---|
| Locators (`get_by_test_id`, `get_by_role`, `get_by_text`, `filter`, `nth`) | `/books` table rows |
| Auto-wait and web-first `expect()` | Playground "Load slow data" (spinner then result) |
| Forms, `fill`, `select_option`, validation errors | `/books/new`, `/login` |
| Checkbox, radio, enabled/disabled button | Playground "Inputs" |
| Dialogs: alert, confirm, prompt (`page.on("dialog")`) | Playground "Dialogs", Delete button on `/books` |
| Hover, keyboard (`press`) | Playground "Hover and keyboard" |
| Drag and drop (`drag_to`) | Playground "Drag and drop" |
| File upload (`set_input_files`) and download (`expect_download`) | Playground "Upload / download" |
| iframe (`frame_locator`) and new tab (`context.expect_page`) | Playground "iframe and new tab" |
| Elements that appear/disappear (`to_have_count`) | Playground "Dynamic list" |
| Network: `expect_response`, `page.route` (mock/abort) | `/api/stats` and `/api/health` are fetched by every page |
| Console and page errors (`page.on("console")`) | any page |
| Redirects and auth (`?next=`, 401/403/404 pages) | `/books/new`, `/books/1/delete` as `user` |
| Storage state / reusing a login (cookies) | log in once, save `context.storage_state()` |
| Browser contexts (two users at once) | admin and user in separate contexts |
| Direct HTTP from the browser session (`context.request`) | POST `/books/1/delete` as `user` → 403 |
| API testing with `requests` or `playwright.request` | everything under `/api` |
| Trace viewer, screenshots, video, `--headed`, `--slowmo`, `PWDEBUG=1` | `pytest.ini` already enables trace and screenshot on failure |
| Parametrize, fixtures, markers, parallel (`-n`) | your tests |

## 4. Writing and running tests

Put tests anywhere under `tests/`. Mark them so CI can split them:

```python
import pytest

@pytest.mark.ui        # needs a browser
def test_...(page): ...

@pytest.mark.api       # no browser
def test_...(): ...
```

```bash
pytest                                  # all
pytest -m ui --headed --slowmo 400      # watch the browser
pytest -m api -n auto                   # parallel (each worker starts its own server)
pytest --browser firefox --browser webkit
pytest -k login
PWDEBUG=1 pytest -k login               # Playwright Inspector
playwright show-trace test-results/<folder>/trace.zip
```
Reports are written to `reports/report.html` and `reports/junit.xml`. Allure test
results are written to `allure-results/`; after installing the Allure CLI, generate
a local report with `allure generate allure-results --clean --output allure-report`
and open `allure-report/index.html`.

Ideas for fixtures to write yourself: an API client with a token, a logged-in `page` from saved cookies, a Page Object per screen, a data factory with unique ISBNs (13 digits).

## 5. CI/CD (GitHub Actions)

```bash
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

`.github/workflows/ci.yml` runs:

```
lint ─┬─► api  (pytest -m "api", parallel)
      └─► ui   (pytest -m ui, matrix: chromium | firefox | webkit)
```
Triggers: push to `main`, pull requests, and manual run (pick a browser). Reports, traces, screenshots and videos are uploaded as artifacts, even when tests fail.

The workflow combines Allure results from the API job and each browser job into a
single report. Pull requests and other branches expose that report as an Actions
artifact; pushes to `main` publish it to
[GitHub Pages](https://harsh-valecha.github.io/QA_Automation_hub/).

To enable Pages in the repository, open **Settings → Pages** and set **Build and
deployment → Source** to **GitHub Actions**. The workflow already declares the
`pages: write` and `id-token: write` permissions required to deploy. After pushing
these changes to `main`, open **Actions**, wait for the CI run to finish, then visit
the Pages URL above. No manually created token or secret is needed.

Things to try: break a test and download the trace artifact, add retries (`pytest-rerunfailures`), add a coverage or Docker step, require status checks via branch protection.

## 6. Layout

```
app/        Flask app: api.py (JSON), ui.py (HTML + playground), validation.py, store.py (in-memory), templates/, static/
tests/      conftest.py only: server + reset fixtures
run.py      local entry point (PORT env var)
Dockerfile  optional container image (ENABLE_TEST_ROUTES is off by default)
```

`ENABLE_TEST_ROUTES=1` turns on the reset endpoint. Never enable it on a real environment.
