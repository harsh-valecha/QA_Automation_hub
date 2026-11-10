# Playwright with Python: Practical Cheat Sheet

A hands-on guide for writing browser and API checks with this project. Examples use
**Playwright's synchronous Python API** and **pytest**. You can paste most UI examples into
a file under `tests/ui/`.

> **Try it:** start with the smoke test, change one thing, run it, and watch what happens.
> The app's `/playground` page is a safe place to practise interactions.

## 1. Get started

Install the project's dependencies and a browser (from the repository root):

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
playwright install chromium
```

Run the app and tests in separate terminals if you want to explore manually:

```bash
python run.py                          # app at http://127.0.0.1:5000
pytest tests/ui/test_smoke.py
```

The project's [`tests/conftest.py`](tests/conftest.py) starts a temporary app server,
sets `base_url`, and resets the test data before each test. That is why
`page.goto("/books")` works without a full URL. Set `BASE_URL=http://...` to test an
already-running server instead.

## 2. A first UI test

```python
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_books_page_shows_title(page: Page):
    page.goto("/books")

    expect(page.get_by_test_id("page-title")).to_have_text("Books")
```

What is happening?

1. `page` is a pytest fixture from `pytest-playwright`; it gives this test a browser page.
2. `page.goto()` opens the URL.
3. `get_by_test_id()` finds the element marked with `data-testid="page-title"`.
4. `expect()` waits for the page to reach the expected state, then fails with a useful
   message if it does not.

`@pytest.mark.ui` labels this as a browser test. The project also uses `api`, `e2e`, and
`smoke` markers; see [`pytest.ini`](pytest.ini).

## 3. The Playwright mental model

Think of the browser as a set of nested objects:

```text
Browser
└── BrowserContext  (one isolated user/session)
    ├── Page         (one tab)
    │   └── Locator  (a way to find an element)
    └── Page         (another tab or popup)
```

- **Browser**: Chromium, Firefox, or WebKit.
- **Context**: isolated cookies and browser storage; useful for separate users.
- **Page**: one tab.
- **Locator**: a query that finds elements when you use it. It is not a frozen copy of
  the page.

With the project's pytest plugin, use the provided `page`, `context`, `browser`, and
`playwright` fixtures rather than starting the browser yourself for ordinary tests.

## 4. Finding elements (locators)

Prefer locators that describe what a user sees or that use the project's stable test IDs.

```python
# Best when available: describe the user's intention
page.get_by_role("button", name="Apply")
page.get_by_role("heading", name="Books")
page.get_by_label("Username")
page.get_by_placeholder("Search title or author")

# Stable test hooks used throughout this app
page.get_by_test_id("search-input")

# Other options
page.get_by_text("No books found.")
page.locator("input[name='username']")  # CSS selector; use when needed
```

Locators can be combined to narrow down what you mean:

```python
rows = page.get_by_test_id("book-row")
expect(rows).to_have_count(5)

first_title = rows.first.get_by_test_id("book-title")
expect(first_title).to_contain_text("Book")

# Find a particular row, then work only inside that row
book = rows.filter(has_text="The Hobbit")
book.get_by_role("link", name="The Hobbit").click()
```

Useful locator helpers:

| Helper | Use |
|---|---|
| `.first`, `.last`, `.nth(0)` | Choose one match (indexes start at zero). |
| `.filter(has_text="...")` | Narrow matches by visible text. |
| `.count()` | Get the current number of matches; use `expect(...).to_have_count()` when waiting matters. |
| `.is_visible()`, `.is_enabled()`, `.is_checked()` | Read the current state for a decision. Prefer an `expect()` assertion when checking a test outcome. |

**Tip:** a locator matching multiple elements is often a clue to make it more specific,
not a reason to click `.first` without checking what the elements represent.

## 5. Assertions and auto-waiting

Use Playwright's `expect` for page state. It retries the assertion until it passes or times
out, which is much less fragile than guessing how long the page needs.

```python
expect(page.get_by_test_id("page-title")).to_have_text("Books")
expect(page.get_by_test_id("empty-state")).to_be_visible()
expect(page.get_by_test_id("slow-spinner")).to_be_hidden()
expect(page.get_by_test_id("submit-book")).to_be_enabled()
expect(page.get_by_test_id("item")).to_have_count(2)
expect(page).to_have_url("http://127.0.0.1:5000/books")
```

Use ordinary Python `assert` for values that are already in memory:

```python
response = api_client.get("/api/books/1")
assert response.status_code == 200
assert response.json()["title"]
```

### Auto-waiting in plain language

Before actions such as `.click()` and `.fill()`, Playwright waits for the element to be
usable (for example, visible and enabled). Web-first assertions keep checking until the
expected state appears. This handles many timing differences without extra code.

Avoid fixed sleeps:

```python
time.sleep(2)  # Avoid: slow, and still may not be long enough
```

Instead, wait for the thing that proves the work finished:

```python
page.get_by_test_id("load-slow").click()
expect(page.get_by_test_id("slow-result")).to_contain_text("Loaded after")
```

The Playground's slow request takes about two seconds. A timeout is a maximum wait, not
a delay; set one only when a specific operation needs more time:

```python
expect(page.get_by_test_id("slow-result")).to_be_visible(timeout=5_000)
```

## 6. Common actions and forms

```python
page.get_by_test_id("search-input").fill("python")
page.get_by_test_id("category-filter").select_option(label="tech")
page.get_by_test_id("pg-terms").check()
page.get_by_test_id("plan-pro").check()
page.get_by_test_id("key-input").press("Enter")
page.get_by_test_id("hover-target").hover()
```

`fill()` replaces the input value. Use `press_sequentially()` only when you specifically
need to test per-key typing behavior, such as a live suggestion list.

Example: check that a required field is reported:

```python
page.goto("/books/new")
page.get_by_test_id("submit-book").click()
expect(page.get_by_test_id("error-title")).to_be_visible()
```

For dynamic controls, assert the state that matters:

```python
page.goto("/playground")
page.get_by_test_id("pg-name").fill("Riya")
page.get_by_test_id("pg-terms").check()
expect(page.get_by_test_id("pg-submit")).to_be_enabled()
page.get_by_test_id("pg-submit").click()
expect(page.get_by_test_id("inputs-result")).to_contain_text("Hi Riya")
```

## 7. Navigation, tables, and pages

```python
# Follow a link and verify the destination screen
page.goto("/books")
page.get_by_role("link", name="The Hobbit").click()
expect(page.get_by_test_id("detail-title")).to_contain_text("The Hobbit")

# Search and submit a filter form
page.goto("/books")
page.get_by_test_id("search-input").fill("python")
page.get_by_test_id("apply-filters").click()
expect(page.get_by_test_id("books-table")).to_contain_text("Python")
```

For a redirect or a URL that includes a query string, use a regular expression:

```python
import re
from playwright.sync_api import expect

expect(page).to_have_url(re.compile(r"/login\?next="))
```

Test meaningful user outcomes such as a destination heading, result row, or error
message—not just that a click did not raise an error.

## 8. Login and separate users

The app's browser login form can be exercised like any other form:

```python
page.goto("/login")
page.get_by_test_id("username-input").fill("user")
page.get_by_test_id("password-input").fill("user123")
page.get_by_test_id("login-submit").click()
expect(page.get_by_test_id("current-user")).to_contain_text("user")
```

There is also a `logged_in_page` fixture in `tests/conftest.py`; it signs in as the
default `user` and returns the page. Use it when login itself is not what the test is
trying to verify:

```python
def test_signed_in_user_sees_add_book_link(logged_in_page: Page):
    expect(logged_in_page.get_by_test_id("nav-add-book")).to_be_visible()
```

To test two users independently, create separate contexts. Each context gets its own
cookies and storage:

```python
admin_context = browser.new_context()
user_context = browser.new_context()
admin_page = admin_context.new_page()
user_page = user_context.new_page()

# Sign each page in with the appropriate account, then compare their permissions.

admin_context.close()
user_context.close()
```

For a reusable login between test runs, `context.storage_state(path="...")` saves
cookies and storage, and a new context can load that file with `storage_state="..."`.
Treat the file like a credential: keep it out of Git and do not use real account data.

## 9. Dynamic content and network

### Wait for a response caused by an action

Register the response expectation **before** the click that triggers it:

```python
with page.expect_response(
    lambda response: "/api/slow" in response.url
) as response_info:
    page.get_by_test_id("load-slow").click()

response = response_info.value
assert response.status == 200
expect(page.get_by_test_id("slow-result")).to_contain_text("Loaded after")
```

### Mock or block a request

Route handlers let a UI test control what the browser receives:

```python
page.route(
    "**/api/stats",
    lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"total": 42, "stock": 100}',
    ),
)
page.goto("/books")
```

Other useful route actions:

```python
# Continue the request as normal
page.route("**/api/books", lambda route: route.continue_())

# Simulate a failed request
page.route("**/api/books", lambda route: route.abort())
```

Use mocks to test a specific UI state or failure path. Keep at least some tests using the
real app and API so the integration is checked too.

## 10. Browser dialogs, popups, and iframes

### Alert, confirm, and prompt dialogs

Attach a handler before clicking. If you add a handler, your test must accept or dismiss
the dialog:

```python
page.goto("/playground")
page.once("dialog", lambda dialog: dialog.accept())
page.get_by_test_id("btn-alert").click()
expect(page.get_by_test_id("dialog-result")).to_have_text("alert shown")
```

Accept a prompt with text using `dialog.accept("Riya")`; use `dialog.dismiss()` to cancel.

### New tab / popup

```python
page.goto("/playground")
with page.expect_popup() as popup_info:
    page.get_by_test_id("open-new-tab").click()

popup = popup_info.value
expect(popup.get_by_test_id("frame-title")).to_have_text("Inside the frame")
```

### iframe

Use `frame_locator()` to find elements inside the frame:

```python
frame = page.frame_locator('[data-testid="demo-frame"]')
frame.get_by_test_id("frame-button").click()
expect(frame.get_by_test_id("frame-output")).to_have_text("Frame button clicked")
```

## 11. Uploads and downloads

```python
from pathlib import Path

page.goto("/playground")
page.get_by_test_id("file-input").set_input_files(Path("sample.txt"))
page.get_by_test_id("upload-submit").click()
expect(page.get_by_test_id("upload-result")).to_contain_text("sample.txt")
```

Capture a download before clicking the link. `tmp_path` is a pytest fixture for a
temporary test directory:

```python
def test_export_downloads_csv(page: Page, tmp_path: Path):
    page.goto("/playground")

    with page.expect_download() as download_info:
        page.get_by_test_id("download-csv").click()

    download = download_info.value
    saved_file = tmp_path / download.suggested_filename
    download.save_as(saved_file)
    assert saved_file.suffix == ".csv"
```

## 12. API testing: two useful choices

Many API tests in this project use the `api_client` fixture from `tests/conftest.py`.
It is a `requests.Session` with the app's base URL already set:

```python
import pytest


@pytest.mark.api
def test_health_endpoint(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

Use `requests` when you want a straightforward HTTP test without a browser. Use
Playwright's `context.request` when you want API calls to share the browser context's
cookies:

```python
@pytest.mark.e2e
def test_health_from_browser_context(context, base_url):
    response = context.request.get(f"{base_url}/api/health")
    assert response.status == 200
    assert response.json()["status"] == "ok"
```

The project also provides `auth_token` for API tests. Choose a role with indirect
parametrization:

```python
@pytest.mark.api
@pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
def test_admin_can_create_book(api_client, auth_token, book_factory):
    book = book_factory()
    book["price"] = 10
    response = api_client.post(
        "/api/books",
        headers={"Authorization": f"Bearer {auth_token}"},
        json=book,
    )
    assert response.status_code == 201
```

`book_factory` creates a valid book payload with a unique ISBN. The `user` account
cannot delete books; the `admin` account can.

## 13. Reuse with fixtures, parameters, and page objects

### Keep repeated setup in fixtures

Fixtures make setup reusable and let pytest handle cleanup. The project already has
`page`, `context`, `base_url`, `api_client`, `auth_token`, `logged_in_page`, and
`book_factory`.

### Test several values with parametrization

```python
@pytest.mark.parametrize(
    ("query", "expected"),
    [("Python", "Python"), ("Pride", "Pride")],
)
def test_search_finds_matching_book(page: Page, query: str, expected: str):
    page.goto("/books")
    page.get_by_test_id("search-input").fill(query)
    page.get_by_test_id("apply-filters").click()
    expect(page.get_by_test_id("books-table")).to_contain_text(expected)
```

### A small Page Object

When several tests use the same screen, a page object can keep its locators and actions
in one place:

```python
from playwright.sync_api import Page


class BooksPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = page.get_by_test_id("search-input")
        self.apply_filters = page.get_by_test_id("apply-filters")
        self.table = page.get_by_test_id("books-table")

    def open(self):
        self.page.goto("/books")

    def search_for(self, text: str):
        self.search.fill(text)
        self.apply_filters.click()
```

Keep page objects small; assertions usually belong in the test so it stays clear what
behavior is being checked.

## 14. Debugging failing tests

Run one test at a time, show the browser, or slow down actions:

```bash
pytest tests/ui/test_smoke.py -q
pytest -m ui --headed
pytest -m ui --headed --slowmo 400
PWDEBUG=1 pytest -k books
```

The project config keeps traces and screenshots on failure. Open a trace with:

```bash
playwright show-trace test-results/<test-folder>/trace.zip
```

In the Trace Viewer, inspect the action timeline, DOM snapshots, screenshots, and
network requests. You can also capture a screenshot explicitly:

```python
page.screenshot(path="reports/books.png", full_page=True)
```

For JavaScript errors and browser console messages:

```python
page.on("pageerror", lambda error: print(f"Page error: {error}"))
page.on("console", lambda message: print(f"Console {message.type}: {message.text}"))
```

Before adding a wait or changing a locator, check the trace and failure message. They
often show whether the element was missing, hidden, covered, or simply not the element
you intended.

## 15. Run the tests you need

```bash
pytest                                  # all tests
pytest -m ui                            # browser tests
pytest -m "not ui"                      # tests not marked ui
pytest -m api                           # API tests
pytest -k login                         # tests with "login" in their names
pytest --browser chromium               # select Chromium
pytest --browser firefox --browser webkit
pytest -m ui -n 2                       # run UI tests with two workers
```

`pytest --browser` supports `chromium`, `firefox`, and `webkit`. Install other browsers
with `playwright install firefox` or `playwright install webkit`. CI runs the UI suite
across a browser matrix; see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## 16. Good habits and common traps

- **Prefer user-facing locators** (`get_by_role`, `get_by_label`) or stable
  `data-testid` hooks over brittle CSS paths.
- **Assert outcomes**, not just actions. After clicking Submit, check the message,
  destination, or updated data.
- **Avoid `time.sleep()`**. Wait for a locator, URL, or response that signals completion.
- **Keep tests independent.** This project resets seed data before each test; avoid
  relying on another test to create something first.
- **Use unique test data.** `book_factory` avoids ISBN collisions.
- **Keep browser and API assertions distinct.** A browser test checks user-visible
  behavior; an API test checks HTTP status, headers, and response data.
- **Don't hide failures with broad `try/except` blocks.** Let pytest report the failure
  or add a precise assertion with context.
- **Don't use real credentials or commit saved browser state.** Storage state can contain
  active cookies.
- **Use a fresh context for another user.** Separate pages in the same context share
  cookies and storage.

## 17. Try these mini-exercises

Each task maps to a feature in this app:

1. **Find a book:** on `/books`, search for a word and assert the matching row appears.
2. **Check a form error:** submit `/books/new` empty and check the title error.
3. **Check permissions:** sign in as `user`, send a `POST` to `/books/1/delete` with
   `page.request`, and assert a 403 response; compare with `admin`.
4. **Watch a request:** click **Load slow data** on `/playground`, capture `/api/slow`,
   and assert its status.
5. **Practise a dialog:** accept the alert or dismiss the confirm dialog.
6. **Download a report:** save the CSV to `tmp_path` and check its filename or contents.
7. **Try three browsers:** run the same UI test on Chromium, Firefox, and WebKit.

For more app-specific examples and feature locations, see the
[project README](README.md), [`tests/ui/`](tests/ui/), and
[`app/templates/playground.html`](app/templates/playground.html).
