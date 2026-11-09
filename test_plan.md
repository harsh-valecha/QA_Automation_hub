# End-to-End Test Plan — QA Automation Practice Hub

**Application:** Flask bookshelf app
**Test types:** API (`requests`), UI (Playwright), hybrid E2E
**Browsers:** Chromium first; Firefox and WebKit for smoke coverage
**Pytest markers:** `smoke`, `api`, `ui`, `e2e`

## 1. Goal and scope

Build a compact, progressive suite that exercises the app's distinct behavior and teaches the main automation techniques without repeating the same checks at every level.

In scope: REST endpoints, authentication and roles, book CRUD and validation, UI forms and navigation, CSV, playground interactions, test isolation, basic network/security/accessibility checks, and CI.

Out of scope: persistent-database behavior, production load testing, visual pixel-diff, and security behavior the app does not implement (for example rate limiting or CSRF).

## 2. Application reference

### API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health`, `/api/stats`, `/api/slow` | Health, aggregates, delayed response |
| POST | `/api/auth/login` | Issue bearer token |
| GET | `/api/auth/me` | Identify token owner |
| GET | `/api/books` | List, search, filter, sort, paginate |
| POST | `/api/books` | Create a book |
| GET | `/api/books/{id}` | Read a book |
| PUT/PATCH/DELETE | `/api/books/{id}` | Replace, partially update, delete |
| POST | `/api/test/reset` | Restore seed data when test routes are enabled |

### UI

`/`, `/login`, `/logout`, `/books`, `/books/new`, `/books/{id}`, `/books/{id}/edit`, `/books/{id}/delete`, `/books/export.csv`, `/playground`, `/playground/upload`, and `/playground/frame`.

### Seed data

- Seven books; default page size is five (pages contain five and two books).
- Category counts: tech 3, fiction 2, science 1, history 1.
- Seed stock total: **89**.
- Demo users: `admin/admin123` (admin) and `user/user123` (user).

## 3. How to keep the suite small

- Each scenario below is listed once. `smoke` is a marker on selected API/UI tests, not a second copy of them.
- Parameterize related inputs (for example invalid book fields, query values, or dialog choices) rather than writing one nearly identical test per value.
- Reuse fixtures for the server, reset, API client, logged-in users, and unique valid book data.
- For CRUD, assert the result through a follow-up read or aggregate when that proves a distinct outcome; do not repeat the same field assertions in every layer.
- Start with Chromium and add other browsers only after the UI suite is stable.

### Suggested fixtures

1. `base_url` / `live_server` and an autouse reset before each test.
2. `api_client` and `admin_token` / `user_token`.
3. `valid_book()` with a unique 13-digit ISBN.
4. `logged_in_page(role)` for UI tests.

## 4. Level 0 — Environment readiness

**Checklist (not separate automated test cases):**

- Install development dependencies and the Chromium browser.
- Start the app with `ENABLE_TEST_ROUTES=1`; confirm `/api/health` responds.
- Run pytest and confirm collection and server startup/shutdown work.
- Confirm the reset fixture restores seven seed books.

**Ready when:** the test environment starts reliably and at least one test can run.

## 5. API tests — implement across Levels 1–2

**Markers:** `api`; add `smoke` to the fast core cases below. These are the API cases to implement once; later levels should extend them, not recreate them.

### 5.1 Health and stats

| ID | Scenario | Essential assertions |
|---|---|---|
| API-01 `smoke` | Health response | 200, JSON content type, exact `status` and `version` fields |
| API-02 `smoke` | Seed stats | 200, 7 books, stock 89, exact category counts |
| API-03 | Stats after a book lifecycle | Create, change stock, and delete a book; assert the aggregate changes correctly at each meaningful step |

### 5.2 Authentication

| ID | Scenario | Essential assertions |
|---|---|---|
| API-04 `smoke` | Login as admin and user, then call `/me` | Non-empty bearer token; returned username and role match each account |
| API-05 | Invalid login and invalid/missing bearer token | Login failures do not issue a token; protected endpoint returns 401 |
| API-06 | Login request validation | Parameterize missing/empty fields and malformed/non-object JSON; assert the documented 4xx response and error shape |

### 5.3 Books API

| ID | Scenario | Essential assertions |
|---|---|---|
| API-07 `smoke` | Default list and one seeded book | 200, pagination metadata and item schema; detail response matches the selected book |
| API-08 | Search/filter/sort combination | Use a known query with category and price bounds; assert matching items and ordering. Include a no-match query |
| API-09 | Pagination and invalid query values | Check page 2 and an out-of-range page; parameterize representative invalid page, page-size, category, sort, and price values and assert 400 |
| API-10 `smoke` | Create a valid book | 201, response fields, `Location` resolves to the same book, list/stats reflect creation |
| API-11 | Create validation and duplicate ISBN | Parameterize required/type/range/ISBN/category errors; separately assert duplicate ISBN returns conflict and does not add a book |
| API-12 `smoke` | PUT and PATCH semantics | PUT replaces the submitted resource; PATCH changes only the supplied field; verify with GET |
| API-13 `smoke` | Delete and role permissions | Admin delete returns 204 then GET returns 404; user cannot delete and the book remains |
| API-14 | Missing resource and unsupported method | Unknown book is JSON 404; unsupported API method returns 405 |

### 5.4 Slow endpoint, reset, and errors

| ID | Scenario | Essential assertions |
|---|---|---|
| API-15 | Slow endpoint boundaries | Parameterize zero, default, and over-limit delay; check `waited_ms` and use a tolerant elapsed-time bound |
| API-16 | Invalid slow endpoint input | Non-numeric input returns the documented 400 error |
| API-17 | Reset behavior | Reset returns 204 and restores seed totals; verify it is unavailable when test routes are disabled |

**Level 1 exit:** the marked smoke tests pass quickly and independently. The remaining API cases can be added as Level 2 without duplicating these.

## 6. Level 2 — API coverage complete

Section 5 is the complete, deduplicated API test inventory. Implement its `smoke` cases in Level 1, then add the remaining cases in this level. Use parameterization for validation inputs; add a separate case only when the behavior or assertion is genuinely different.

**Completion check:** every API route/method is exercised, including success, relevant error status, authentication/role behavior, and response shape. Do not separately test token expiration: tokens do not expire in this app.

## 7. Level 3 — UI smoke

**Markers:** `ui`, `smoke`

| ID | Scenario | Essential assertions |
|---|---|---|
| UI-01 `smoke` | Core page load (parameterize books, login, playground, and frame) | Page heading/main content appears; no uncaught page error |
| UI-02 `smoke` | Root, unknown route, and anonymous navigation | Root reaches books; unknown page shows 404; anonymous navigation shows the expected links |
| UI-03 `smoke` | Books page API indicators | Health badge reaches ready state and stats display the seed totals |
| UI-04 `smoke` | CSV route | Download starts with the expected filename and CSV content type |

**Level 3 exit:** the UI smoke marker passes in Chromium.

## 8. Level 4 — UI functional

**Marker:** `ui`

| ID | Scenario | Essential assertions / technique |
|---|---|---|
| UI-05 | Login, logout, and role-based navigation | Both roles can add books, only admin can delete; logout clears the session; anonymous access to a protected form redirects to login |
| UI-06 | Failed login and safe `next` redirect | Error is visible, password is not retained, and external redirect targets are rejected |
| UI-07 | Books list interaction | Search/category/sort and pagination update results and preserve query state; reset filters restores defaults |
| UI-08 | Create book form | Valid submit reaches detail; parameterize representative invalid fields and assert field errors/retained input |
| UI-09 | Edit book form | Values are prefilled; a valid edit is saved; invalid ISBN/field input is rejected |
| UI-10 | Book detail and delete confirmation | Detail shows the book; confirm deletes it, dismiss leaves it; verify the result in the list |
| UI-11 | CSV download and upload | Use Playwright download handling and parse a row; upload a valid file and verify the echoed name/size |
| UI-12 | Playground wait and dialogs | Wait for a delayed result; handle alert/confirm/prompt (parameterize accept/dismiss outcomes) |
| UI-13 | Playground inputs and keyboard | Fill/check/select controls and verify enabled state/result; verify Enter and Escape behavior |
| UI-14 | Playground hover and drag/drop | Tooltip appears on hover; drag a card and assert its destination |
| UI-15 | Iframe, new tab, and dynamic list | Use frame locator and new-page handling; add/remove list items and assert count/content |

## 9. Level 5 — Hybrid E2E

**Marker:** `e2e`. These cover cross-layer outcomes only; single-layer behavior is already covered above.

| ID | Scenario | Essential assertions |
|---|---|---|
| E2E-01 | UI creates a book, API verifies it | UI submission succeeds; API GET and stats show the created book |
| E2E-02 | API changes/deletes a book, UI verifies it | UI reflects the changed data, then no longer shows the deleted book |
| E2E-03 | User/admin authorization across UI and API | User cannot delete (including direct request); admin can; verify final state |

## 10. Level 6 — Cross-cutting checks

Add these after the functional suite is stable. They are intentionally representative, not a second full pass over every page/endpoint.

| ID | Focus | Scenario and assertion |
|---|---|---|
| NF-01 | Network resilience | Abort health/stats requests; page remains usable and shows the appropriate unavailable state |
| NF-02 | Security basics | User input is rendered as text (no script execution); external login redirect is rejected; errors reveal no credentials/tokens |
| NF-03 | Accessibility | Form inputs have labels and errors are associated with fields; keyboard can submit login and operate a playground control |
| NF-04 | Robustness | Parallel read requests all succeed; repeated delete gives 204 then 404 |
| NF-05 | Cross-browser | Run UI smoke on Firefox and WebKit; keep Chromium as the main UI run |
| NF-06 | Timing | Check one normal endpoint has a generous local response-time ceiling; verify slow endpoint cap in API-15 |

## 11. Level 7 — CI quality gates

- Run API and UI suites by marker; keep smoke tests fast.
- Run Chromium on each change; run Firefox/WebKit smoke in a browser matrix.
- Publish JUnit/HTML reports and capture traces/screenshots on failure.
- Fail on lint, collection errors, or test failures; remove any temporary allowance for an empty suite.
- Track runtime and repeat failures to identify flakiness rather than adding arbitrary retries.

## 12. Exit criteria and coverage

- All levels pass in CI; tests are isolated by reset and do not rely on execution order.
- Every listed API route/method and UI feature has at least one meaningful assertion.
- Book validation is data-driven across required fields, types, boundaries, and duplicate ISBN.
- Auth success/failure and admin/user permissions are covered at API and UI boundaries.
- API/UI errors, list filters/pagination, CSV, playground controls, and core cross-layer flows are covered.
- No unexpected page errors; cross-browser smoke is green.

## 13. Implementation order

1. `tests/api/test_health_stats_slow.py` — API-01–03, API-15–16
2. `tests/api/test_auth.py` — API-04–06
3. `tests/api/test_books.py` — API-07–14
4. `tests/api/test_reset.py` — API-17
5. `tests/ui/test_smoke.py` — UI-01–04
6. `tests/ui/test_books.py` — UI-05–10
7. `tests/ui/test_files_playground.py` — UI-11–15
8. `tests/e2e/test_flows.py` — E2E-01–03
9. Add NF checks and CI gates after the above are stable.

## 14. Notes

- Reset restores books but tokens survive; each test should obtain its own token.
- UI edit submits all fields; a blank stock value becomes zero.
- UI invalid filters are reset and reported in the UI rather than returning the API's 400.
- Use returned IDs for created books; IDs restart after reset.
- Drag/drop and dialog behavior can vary by browser; only add evidence-based skips.
