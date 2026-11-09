# End-to-End Test Plan — QA Automation Practice Hub

**Application:** QA Automation Practice Hub (Flask bookshelf app)  
**Primary test types:** API (HTTP/JSON), UI (Playwright), hybrid E2E  
**Target browsers:** Chromium, Firefox, WebKit  
**Markers used:** `smoke`, `api`, `ui`, `e2e` (see `pytest.ini`)

---

## 1. Objective and scope

This plan defines a **level-by-level** strategy for verifying every reachable feature of the application through both the **REST API** (`/api/*`) and the **HTML UI**. Each level is a gate: tests from the next level are added only when the previous level is green and stable.

### In scope

- All API endpoints and documented status codes
- All UI pages, forms, navigation, filters, pagination
- Authentication, authorization, session handling
- Validation of every field and query parameter
- Playground interactions (wait, dialogs, inputs, hover, keyboard, drag/drop, upload/download, iframe, new tab, dynamic list)
- Export CSV, reset-for-tests, error pages (404/403/405/500)
- Cross-cutting concerns: network mocking, console/page errors, cross-browser, security basics, CI quality gates

### Out of scope (unless extended)

- Database durability (app is in-memory by design)
- Production deployment hardening beyond documented app behaviour
- Visual pixel-diff unless later requested
- Performance/load beyond endpoint response-time smoke

---

## 2. Application and endpoint inventory

### 2.1 API endpoints

| Method | Endpoint          | Auth                           | Purpose                          |
| ------ | ----------------- | ------------------------------ | -------------------------------- |
| GET    | `/api/health`     | none                           | liveness/health badge            |
| GET    | `/api/stats`      | none                           | aggregate book stats             |
| GET    | `/api/slow?ms=`   | none                           | delayed response (max 5000ms)    |
| POST   | `/api/auth/login` | none                           | issue Bearer token               |
| GET    | `/api/auth/me`    | Bearer                         | current API user                 |
| GET    | `/api/books`      | none                           | list/search/filter/sort/paginate |
| POST   | `/api/books`      | Bearer (any logged-in user)    | create book                      |
| GET    | `/api/books/{id}` | none                           | read one book                    |
| PUT    | `/api/books/{id}` | Bearer                         | full replace                     |
| PATCH  | `/api/books/{id}` | Bearer                         | partial update                   |
| DELETE | `/api/books/{id}` | Bearer admin only              | delete                           |
| POST   | `/api/test/reset` | only if `ENABLE_TEST_ROUTES=1` | reseed data (204)                |

### 2.2 UI routes

| Route                         | Auth      | Purpose                              |
| ----------------------------- | --------- | ------------------------------------ |
| `/`                           | none      | redirect to `/books`                 |
| `/login` (GET/POST)           | none      | login form                           |
| `/logout` (POST)              | session   | end session                          |
| `/books` (GET)                | none      | list/filter table, stats, pagination |
| `/books/new` (GET/POST)       | logged-in | create book form                     |
| `/books/{id}` (GET)           | none      | book detail                          |
| `/books/{id}/edit` (GET/POST) | logged-in | edit book form                       |
| `/books/{id}/delete` (POST)   | admin     | delete + confirm dialog              |
| `/books/export.csv` (GET)     | none      | download CSV                         |
| `/playground` (GET)           | none      | interaction demos                    |
| `/playground/upload` (POST)   | none      | file upload echo                     |
| `/playground/frame` (GET)     | none      | iframe/new-tab target                |

### 2.3 Seed data

- 7 books (IDs 1–7): tech=3, fiction=2, science=1, history=1
- default page size = 5 → page 1 has 5, page 2 has 2
- total stock = 89
- users: `admin/admin123` (admin), `user/user123` (non-admin)

---

## 3. Test strategy

### 3.1 Levels (execution order)

| Level | Name                        | Marker(s)    | Goal                                                 | Added when          |
| ----- | --------------------------- | ------------ | ---------------------------------------------------- | ------------------- |
| 0     | Environment readiness       | smoke        | install/run/server health/reset                      | repository cloned   |
| 1     | API smoke                   | api, smoke   | one happy-path per endpoint, core shapes             | Level 0 green       |
| 2     | API functional + validation | api          | exhaustive status codes, fields, filters, auth roles | Level 1 green       |
| 3     | UI smoke                    | ui, smoke    | pages load, navigation, health badge                 | Level 1 green       |
| 4     | UI functional               | ui           | forms, filters, pagination, playground interactions  | Levels 2–3 green    |
| 5     | Hybrid E2E                  | e2e (api+ui) | cross-layer flows, roles, network mock               | Level 4 green       |
| 6     | Non-functional              | api/ui       | security basics, robustness, cross-browser checks    | Level 5 green       |
| 7     | CI/CD quality gates         | all          | marker split, matrix, artifacts, flakiness control   | Levels 0–6 complete |

### 3.2 Environment and fixtures

- Reuse `tests/conftest.py` (`live_server`, `base_url`, autouse `_reset_state`) so every test starts from seed data.
- API tests use direct HTTP (`requests` or Playwright `APIRequestContext`).
- UI tests use Playwright `page`.
- Hybrid tests combine both in one test where needed.
- Test isolation: `_reset_state` guarantees same starting data; token map is intentionally preserved by reset. Tests must not depend on tokens from previous tests.

### 3.3 Test data strategy

Create these fixtures/helpers early:

1. `api_client(base_url)` → `requests.Session` with base URL.
2. `admin_token`, `user_token` → login once and return tokens.
3. `book_factory(isbn=None)` → valid payload with 13-digit unique ISBN.
4. `logged_in_page(page, username, password)` or storage-state fixture per role.
5. Page Objects for Books, Login, BookForm, Playground.
6. Unique ISBN generator using a 13-digit counter / timestamp.

### 3.4 Success criteria conventions

A test is considered successful only when it asserts:

- HTTP status code (or UI response status where observable)
- response body shape and key fields
- state change reflected in follow-up read/export/stats
- no unexpected console/page errors
- no flakiness over 3 repeated local runs

---

## 4. Level 0 — Environment readiness

**Add when:** repository is cloned.  
**Marker:** `smoke`

| Test ID   | What to verify                                     | Success criteria                                        |
| --------- | -------------------------------------------------- | ------------------------------------------------------- |
| L0-ENV-01 | Create venv and install `requirements-dev.txt`     | no install errors                                       |
| L0-ENV-02 | Install Playwright Chromium                        | browser available                                       |
| L0-ENV-03 | Start app with `ENABLE_TEST_ROUTES=1`              | `/api/health` returns 200 within 20s                    |
| L0-ENV-04 | Run `pytest` with empty `tests/` (except conftest) | exit code 0 or 5, no collection errors                  |
| L0-ENV-05 | Reset endpoint availability                        | `POST /api/test/reset` → 204 and `/api/books` total = 7 |

**Exit criteria:** local `pytest` completes, server starts/stops cleanly, report files generated.

---

## 5. Level 1 — API smoke (P0)

**Add when:** Level 0 green.  
**Marker:** `api, smoke`  
**Goal:** one fast test per critical endpoint and core shape.

| Test ID    | Endpoint / action                    | Expected                                                |
| ---------- | ------------------------------------ | ------------------------------------------------------- |
| API-SMK-01 | `GET /api/health`                    | 200, `status="ok"`, `version="1.0.0"`                   |
| API-SMK-02 | `GET /api/stats`                     | 200, total_books=7, total_stock=89, by_category present |
| API-SMK-03 | `POST /api/auth/login` admin         | 200, non-empty token, token_type Bearer, role admin     |
| API-SMK-04 | `GET /api/auth/me` with token        | 200, username/role match                                |
| API-SMK-05 | `GET /api/auth/me` no token          | 401, error `unauthorized`                               |
| API-SMK-06 | `GET /api/books` default             | 200, 5 items, total=7, page=1, pages=2                  |
| API-SMK-07 | `GET /api/books/1`                   | 200, title/name fields present                          |
| API-SMK-08 | `GET /api/books/9999`                | 404, error `not_found`                                  |
| API-SMK-09 | `POST /api/books` valid (user token) | 201, Location header, created body                      |
| API-SMK-10 | `PATCH /api/books/1` one field       | 200, updated field only changed                         |
| API-SMK-11 | `DELETE /api/books/{id}` as admin    | 204 and subsequent GET 404                              |
| API-SMK-12 | `GET /api/slow?ms=0`                 | 200, waited_ms=0                                        |
| API-SMK-13 | `POST /api/test/reset`               | 204 then total_books=7                                  |

**Exit criteria:** all Level 1 pass in under 10 seconds per worker.

---

## 6. Level 2 — API functional and validation (detailed)

**Add when:** Level 1 green.  
**Marker:** `api`

### 6.1 Health and stats

| Test ID    | Validation                         | Expected                                                     |
| ---------- | ---------------------------------- | ------------------------------------------------------------ |
| API-HLT-01 | content-type and exact keys/values | `application/json`, body `{"status":"ok","version":"1.0.0"}` |
| API-HLT-02 | repeated calls                     | stable 200 response                                          |
| API-ST-01  | stats math for seed                | total_books=7, stock=84                                      |
| API-ST-02  | category counts                    | tech=3, fiction=2, science=1, history=1                      |
| API-ST-03  | stats after create                 | total_books and relevant category count +1                   |
| API-ST-04  | stats after delete                 | total_books and category count -1                            |
| API-ST-05  | total_stock after stock update     | exact arithmetic                                             |

### 6.2 Slow endpoint

| Test ID     | Scenario             | Expected                           |
| ----------- | -------------------- | ---------------------------------- |
| API-SLOW-01 | `ms` omitted         | 200, waited_ms=1000, elapsed ≥0.9s |
| API-SLOW-02 | `ms=0`               | 200, waited_ms=0, fast             |
| API-SLOW-03 | `ms=2000`            | 200, waited_ms=2000, elapsed ≥1.9s |
| API-SLOW-04 | `ms=5000`            | 200, waited_ms=5000                |
| API-SLOW-05 | `ms=5001`            | capped to 5000                     |
| API-SLOW-06 | `ms=-5`              | treated as 0                       |
| API-SLOW-07 | `ms=abc`             | 400, error `bad_request`           |
| API-SLOW-08 | `ms=1.5`             | 400                                |
| API-SLOW-09 | `ms=true`            | 400                                |
| API-SLOW-10 | body present ignored | 200                                |

### 6.3 Authentication: login

| Test ID           | Scenario                                 | Expected                                                                                                                                                                                                                   |
| ----------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API-AUTH-LOGIN-01 | admin valid                              | 200, token non-empty, token_type Bearer, role admin                                                                                                                                                                        |
| API-AUTH-LOGIN-02 | user valid                               | 200, role user                                                                                                                                                                                                             |
| API-AUTH-LOGIN-03 | wrong password                           | 401, error unauthorized, no token                                                                                                                                                                                          |
| API-AUTH-LOGIN-04 | unknown user                             | 401, same message as wrong password (no enumeration)                                                                                                                                                                       |
| API-AUTH-LOGIN-05 | missing username                         | 422, details.username = "is required"                                                                                                                                                                                      |
| API-AUTH-LOGIN-06 | missing password                         | 422, details.password = "is required"                                                                                                                                                                                      |
| API-AUTH-LOGIN-07 | both missing                             | 422, both details                                                                                                                                                                                                          |
| API-AUTH-LOGIN-08 | empty username `""`                      | 422                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-09 | empty password `""`                      | 422                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-10 | username number                          | 422                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-11 | password number                          | 422                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-12 | body `null`                              | 400, invalid_json (because parsed None)                                                                                                                                                                                    |
| API-AUTH-LOGIN-13 | body JSON array                          | 400                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-14 | missing Content-Type but valid JSON raw  | 400 (get_json returns None)                                                                                                                                                                                                |
| API-AUTH-LOGIN-15 | malformed JSON `{`                       | 400                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-16 | `GET /api/auth/login`                    | 405 method_not_allowed                                                                                                                                                                                                     |
| API-AUTH-LOGIN-17 | login response token authenticates `/me` | 200                                                                                                                                                                                                                        |
| API-AUTH-LOGIN-18 | whitespace username `" admin "`          | 422 or invalid? App does not strip API username; ensure assertion matches actual: only empty check, so `" admin "` passes if password matches? Password compare exact; username lookup fails → 401. Document expected 401. |
| API-AUTH-LOGIN-19 | leading/trailing password spaces         | exact password required; wrong → 401                                                                                                                                                                                       |

### 6.4 Authentication: me / tokens

| Test ID        | Scenario                                                                     | Expected                                   |
| -------------- | ---------------------------------------------------------------------------- | ------------------------------------------ |
| API-AUTH-ME-01 | admin token                                                                  | 200, `{"username":"admin","role":"admin"}` |
| API-AUTH-ME-02 | user token                                                                   | 200, role user                             |
| API-AUTH-ME-03 | no Authorization header                                                      | 401 + `WWW-Authenticate: Bearer`           |
| API-AUTH-ME-04 | invalid token                                                                | 401 + WWW-Authenticate                     |
| API-AUTH-ME-05 | empty Bearer                                                                 | 401                                        |
| API-AUTH-ME-06 | `Authorization: Token x` (wrong scheme)                                      | 401                                        |
| API-AUTH-ME-07 | Bearer with extra spaces                                                     | trim supported, 200 if valid               |
| API-AUTH-ME-08 | token in query string                                                        | ignored → 401                              |
| API-AUTH-ME-09 | method POST to `/me`                                                         | 405                                        |
| API-AUTH-ME-10 | expired/revoked token behavior | Tokens never expire in the app; document as a limitation/non-goal |

### 6.5 Books: list, search, filter, sort, paginate

API status baseline: valid requests 200; invalid query 400.

| Test ID           | Scenario                                                       | Expected                                                  |
| ----------------- | -------------------------------------------------------------- | --------------------------------------------------------- |
| API-BOOKS-LIST-01 | default request                                                | 5 items, page=1, per_page=5, total=7, pages=2             |
| API-BOOKS-LIST-02 | item schema                                                    | keys id,title,author,isbn,price,stock,category,created_at |
| API-BOOKS-LIST-03 | ids seed 1..5 on page 1                                        | exact (or sorted by id)                                   |
| API-BOOKS-LIST-04 | `page=2`                                                       | 2 items, page=2                                           |
| API-BOOKS-LIST-05 | `page=3`                                                       | 0 items, total=7, pages=2                                 |
| API-BOOKS-LIST-06 | `per_page=1`                                                   | total=7 pages=7                                           |
| API-BOOKS-LIST-07 | `per_page=50`                                                  | all 7 in one page                                         |
| API-BOOKS-LIST-08 | `per_page=0`                                                   | 400                                                       |
| API-BOOKS-LIST-09 | `per_page=51`                                                  | 400                                                       |
| API-BOOKS-LIST-10 | `page=0`                                                       | 400                                                       |
| API-BOOKS-LIST-11 | `page=-1`                                                      | 400                                                       |
| API-BOOKS-LIST-12 | `page=1.0`                                                     | 400                                                       |
| API-BOOKS-LIST-13 | `q=clean` title search                                         | only Clean Code                                           |
| API-BOOKS-LIST-14 | `q=robert` author search                                       | Clean Code                                                |
| API-BOOKS-LIST-15 | `q=CLEAN` case-insensitive                                     | Clean Code                                                |
| API-BOOKS-LIST-16 | `q=zzzzz`                                                      | items empty, total=0, pages=1                             |
| API-BOOKS-LIST-17 | `q` whitespace-only                                            | treated as None, full list                                |
| API-BOOKS-LIST-18 | `category=tech`                                                | 3 items                                                   |
| API-BOOKS-LIST-19 | `category=fiction`                                             | 2 items                                                   |
| API-BOOKS-LIST-20 | invalid category                                               | 400, details.category                                     |
| API-BOOKS-LIST-21 | empty category param                                           | ignored                                                   |
| API-BOOKS-LIST-22 | `min_price=30`                                                 | prices ≥30                                                |
| API-BOOKS-LIST-23 | `max_price=15`                                                 | prices ≤15                                                |
| API-BOOKS-LIST-24 | min+max range                                                  | only books in range                                       |
| API-BOOKS-LIST-25 | `min_price=9.99&max_price=9.99`                                | Dune only                                                 |
| API-BOOKS-LIST-26 | min_price=max_price (none) -> all? edge                        | not in range? test exact                                  |
| API-BOOKS-LIST-27 | negative price                                                 | 400                                                       |
| API-BOOKS-LIST-28 | non-numeric min_price                                          | 400                                                       |
| API-BOOKS-LIST-29 | NaN/Infinity string? `Infinity` float parse -> nonfinite check | 400                                                       |
| API-BOOKS-LIST-30 | `min_price=10&max_price=5`                                     | 400 min_price detail "must not be greater than max_price" |
| API-BOOKS-LIST-31 | `sort=title&order=asc`                                         | alphabetical                                              |
| API-BOOKS-LIST-32 | `sort=title&order=desc`                                        | reverse alphabetical                                      |
| API-BOOKS-LIST-33 | `sort=price&order=asc`                                         | cheapest first                                            |
| API-BOOKS-LIST-34 | `sort=id` default                                              | ascending IDs                                             |
| API-BOOKS-LIST-35 | invalid sort                                                   | 400 details.sort                                          |
| API-BOOKS-LIST-36 | invalid order                                                  | 400 details.order                                         |
| API-BOOKS-LIST-37 | combined q+category+price+sort+page                            | exact filtered subset and pagination                      |
| API-BOOKS-LIST-38 | filters do not mutate source data                              | list twice same result                                    |
| API-BOOKS-LIST-39 | `q` matches partial author/title                               | substring behaviour                                       |
| API-BOOKS-LIST-40 | multiple invalid params                                        | details contains all invalid fields                       |

### 6.6 Books: read one

| Test ID          | Scenario                                                | Expected                                                                              |
| ---------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| API-BOOKS-GET-01 | existing id 1                                           | 200 body equals created book                                                          |
| API-BOOKS-GET-02 | seed book fields exact                                  | title etc                                                                             |
| API-BOOKS-GET-03 | id 0                                                    | 404                                                                                   |
| API-BOOKS-GET-04 | negative id `-1`                                        | 404 (route converter int allows negative? Flask `<int>` accepts negative; store none) |
| API-BOOKS-GET-05 | id 9999                                                 | 404 not_found                                                                         |
| API-BOOKS-GET-06 | non-numeric path `/api/books/abc`                       | 404 (no route) or HTML? API prefix starts /api, error handler returns JSON 404        |
| API-BOOKS-GET-07 | created id location retrieval                           | body matches create response                                                          |
| API-BOOKS-GET-08 | after delete                                            | 404                                                                                   |
| API-BOOKS-GET-09 | method DELETE? handled separate; POST to `/api/books/1` | 405                                                                                   |

### 6.7 Books: create

| Test ID             | Scenario                                                     | Expected                                                         |
| ------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------- |
| API-BOOKS-CREATE-01 | minimal valid book (stock omitted)                           | 201, stock=0, all returned                                       |
| API-BOOKS-CREATE-02 | full valid book with stock                                   | 201                                                              |
| API-BOOKS-CREATE-03 | Location header points to GET URL                            | GET location returns same book                                   |
| API-BOOKS-CREATE-04 | status and body                                              | 201 JSON                                                         |
| API-BOOKS-CREATE-05 | price rounded to 2 decimals                                  | e.g. 10.125 → 10.12 or 10.13 per Python round; document observed |
| API-BOOKS-CREATE-06 | ISBN exact 13 digits required                                | invalid → 422                                                    |
| API-BOOKS-CREATE-07 | missing title                                                | 422 details.title                                                |
| API-BOOKS-CREATE-08 | missing author                                               | 422                                                              |
| API-BOOKS-CREATE-09 | missing isbn                                                 | 422                                                              |
| API-BOOKS-CREATE-10 | missing price                                                | 422                                                              |
| API-BOOKS-CREATE-11 | missing category                                             | 422                                                              |
| API-BOOKS-CREATE-12 | stock optional                                               | no stock error                                                   |
| API-BOOKS-CREATE-13 | title too long (>100)                                        | 422                                                              |
| API-BOOKS-CREATE-14 | author too long (>60)                                        | 422                                                              |
| API-BOOKS-CREATE-15 | empty title after strip                                      | 422                                                              |
| API-BOOKS-CREATE-16 | blank/whitespace fields                                      | 422                                                              |
| API-BOOKS-CREATE-17 | title non-string number                                      | 422                                                              |
| API-BOOKS-CREATE-18 | ISBN wrong length / non-digits                               | 422                                                              |
| API-BOOKS-CREATE-19 | price zero                                                   | 422                                                              |
| API-BOOKS-CREATE-20 | price negative                                               | 422                                                              |
| API-BOOKS-CREATE-21 | price boolean                                                | 422 (not treated as number)                                      |
| API-BOOKS-CREATE-22 | price string numeric `"10"`                                  | 422 (strict)                                                     |
| API-BOOKS-CREATE-23 | stock negative                                               | 422                                                              |
| API-BOOKS-CREATE-24 | stock float                                                  | 422                                                              |
| API-BOOKS-CREATE-25 | stock boolean                                                | 422                                                              |
| API-BOOKS-CREATE-26 | category invalid                                             | 422                                                              |
| API-BOOKS-CREATE-27 | category numeric                                             | 422                                                              |
| API-BOOKS-CREATE-28 | unknown field `foo`                                          | 422, details.foo = "unknown field"                               |
| API-BOOKS-CREATE-29 | body not object (`[]`, string, number, null)                 | 400/422 (`_body` if dict? null → 400 invalid_json)               |
| API-BOOKS-CREATE-30 | malformed JSON                                               | 400                                                              |
| API-BOOKS-CREATE-31 | duplicate ISBN                                               | 409 conflict, details.isbn = "already exists"                    |
| API-BOOKS-CREATE-32 | duplicate after case? ISBN digits only; exact duplicate only | 409                                                              |
| API-BOOKS-CREATE-33 | auth: admin token                                            | 201                                                              |
| API-BOOKS-CREATE-34 | auth: user token                                             | 201 (create allowed for logged-in users)                         |
| API-BOOKS-CREATE-35 | auth: no token                                               | 401                                                              |
| API-BOOKS-CREATE-36 | auth: invalid token                                          | 401                                                              |
| API-BOOKS-CREATE-37 | created book appears in list                                 | total +1                                                         |
| API-BOOKS-CREATE-38 | duplicate on concurrent requests | Not needed; concurrent ISBN uniqueness is outside this test plan |
| API-BOOKS-CREATE-39 | created_at is ISO timestamp                                  | regex/parse                                                      |
| API-BOOKS-CREATE-40 | ID increments and no reuse within same run                   | new id = previous max +1                                         |

### 6.8 Books: update (PUT full replace / PATCH partial)

| Test ID          | Scenario                                                     | Expected                                                            |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------------- |
| API-BOOKS-UPD-01 | PUT valid full replacement                                   | 200, all fields overwritten                                         |
| API-BOOKS-UPD-02 | PUT missing required field                                   | 422                                                                 |
| API-BOOKS-UPD-03 | PUT with only title                                          | 422 (replace semantics require full payload)                        |
| API-BOOKS-UPD-04 | PUT unknown field                                            | 422                                                                 |
| API-BOOKS-UPD-05 | PUT immutable? id/created_at should not be client-controlled | if id provided unknown field? `id` is unknown field → 422 (protect) |
| API-BOOKS-UPD-06 | PATCH title only                                             | 200, only title changed, rest preserved                             |
| API-BOOKS-UPD-07 | PATCH price only                                             | 200                                                                 |
| API-BOOKS-UPD-08 | PATCH stock to 0                                             | 200                                                                 |
| API-BOOKS-UPD-09 | PATCH multiple fields                                        | all supplied update                                                 |
| API-BOOKS-UPD-10 | PATCH empty object `{}`                                      | 422 `_body` at least one field                                      |
| API-BOOKS-UPD-11 | PATCH with no allowed fields but unknown field               | still 422 unknown + \_body maybe                                    |
| API-BOOKS-UPD-12 | PATCH price zero                                             | 422                                                                 |
| API-BOOKS-UPD-13 | PATCH duplicate ISBN (another book)                          | 409                                                                 |
| API-BOOKS-UPD-14 | PATCH same ISBN as itself                                    | 200 (ignore_id works)                                               |
| API-BOOKS-UPD-15 | PATCH unknown book                                           | 404                                                                 |
| API-BOOKS-UPD-16 | PUT unknown book                                             | 404                                                                 |
| API-BOOKS-UPD-17 | PUT/PATCH malformed JSON                                     | 400                                                                 |
| API-BOOKS-UPD-18 | auth no token                                                | 401                                                                 |
| API-BOOKS-UPD-19 | auth invalid token                                           | 401                                                                 |
| API-BOOKS-UPD-20 | updates preserve created_at                                  | before/after equal                                                  |
| API-BOOKS-UPD-21 | updates do not change id                                     | id stable                                                           |
| API-BOOKS-UPD-22 | successful update reflected in list/search/detail            | GET/list confirms                                                   |
| API-BOOKS-UPD-23 | update stock negative                                        | 422                                                                 |
| API-BOOKS-UPD-24 | `PATCH` method to wrong ID type (`/api/books/abc`)           | 404                                                                 |
| API-BOOKS-UPD-25 | PUT/PATCH status error shape                                 | `error`, `message`, optional details                                |

### 6.9 Books: delete

| Test ID          | Scenario                                         | Expected                                          |
| ---------------- | ------------------------------------------------ | ------------------------------------------------- |
| API-BOOKS-DEL-01 | delete existing as admin                         | 204, empty body                                   |
| API-BOOKS-DEL-02 | subsequent GET                                   | 404                                               |
| API-BOOKS-DEL-03 | subsequent list total -1                         | verified                                          |
| API-BOOKS-DEL-04 | stats decrease                                   | total_books/stock/category counts                 |
| API-BOOKS-DEL-05 | delete same id twice                             | second 404                                        |
| API-BOOKS-DEL-06 | delete missing id                                | 404                                               |
| API-BOOKS-DEL-07 | delete as `user` token                           | 403 admin role required                           |
| API-BOOKS-DEL-08 | delete no token                                  | 401                                               |
| API-BOOKS-DEL-09 | delete invalid token                             | 401                                               |
| API-BOOKS-DEL-10 | DELETE as user to reduce? ensure no state change | book remains                                      |
| API-BOOKS-DEL-11 | method GET/POST to delete endpoint               | 405? (API endpoint DELETE only; POST returns 405) |
| API-BOOKS-DEL-12 | delete doesn't affect other books                | list minus one                                    |

### 6.10 Error envelope and route errors

| Test ID    | Scenario                                                 | Expected                               |
| ---------- | -------------------------------------------------------- | -------------------------------------- |
| API-ERR-01 | unknown API path                                         | 404 JSON not_found                     |
| API-ERR-02 | method mismatch on `/api/books` (POST? handled; DELETE?) | 405 JSON shape                         |
| API-ERR-03 | `/api` unknown nested                                    | 404 JSON                               |
| API-ERR-04 | body error details only when provided                    | validate field presence based scenario |
| API-ERR-05 | `Content-Type` etc                                       | not required beyond cases              |
| API-ERR-06 | health always JSON                                       | no HTML                                |

### 6.11 Reset (test isolation)

| Test ID      | Scenario                                     | Expected                                                         |
| ------------ | -------------------------------------------- | ---------------------------------------------------------------- |
| API-RESET-01 | call reset                                   | 204 empty                                                        |
| API-RESET-02 | after reset books total 7                    | verified                                                         |
| API-RESET-03 | IDs reseed to 1..7                           | verified                                                         |
| API-RESET-04 | tokens survive reset                         | previously issued token still authenticates (document behaviour) |
| API-RESET-05 | reset restores deleted/updated books         | verified                                                         |
| API-RESET-06 | when `ENABLE_TEST_ROUTES=0`, endpoint absent | 404 (manual/deploy smoke; optional)                              |

**Level 2 exit criteria:** all API endpoint validations, auth roles, and error shapes pass; no test depends on execution order.

---

## 7. Level 3 — UI smoke

**Add when:** Levels 1–2 green.  
**Marker:** `ui, smoke`

| Test ID   | Page / action                   | Expected                                                      |
| --------- | ------------------------------- | ------------------------------------------------------------- |
| UI-SMK-01 | `GET /`                         | redirect to `/books`                                          |
| UI-SMK-02 | `/books`                        | title "Books", table visible, stats widget loading then ready |
| UI-SMK-03 | health badge                    | eventually text "API: ok", data-state="ok"                    |
| UI-SMK-04 | `/login`                        | title, form inputs, submit button                             |
| UI-SMK-05 | `/playground`                   | title, sections present                                       |
| UI-SMK-06 | `/books/export.csv`             | response downloadable; smoke only status                      |
| UI-SMK-07 | `/playground/frame`             | frame title/button                                            |
| UI-SMK-08 | unknown URL                     | error code 404, message "Page not found"                      |
| UI-SMK-09 | nav links visible for anonymous | Books, Playground, Log in                                     |
| UI-SMK-10 | no console errors on base pages | none                                                          |

**Exit criteria:** core pages and navigation pass on Chromium.

---

## 8. Level 4 — UI functional (detailed)

**Add when:** Levels 2–3 green.  
**Marker:** `ui`

### 8.1 Navigation and auth UI

| Test ID    | Scenario                                                             | Expected                                                                                                                                    |
| ---------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| UI-AUTH-01 | login valid admin                                                    | flash success "Welcome back, admin!", redirect /books, current-user shows admin (admin), nav Add book + Logout                              |
| UI-AUTH-02 | login valid user                                                     | current-user user (user), no Add book? Actually Add book visible to any logged-in user; delete button hidden                                |
| UI-AUTH-03 | invalid credentials                                                  | status 401, flash error "Invalid username or password", form remains, username retained, password blank                                     |
| UI-AUTH-04 | login empty submit                                                   | browser allows POST (novalidate), server validation? Form login doesn't call validate_book; Authenticate fails → flash error 401. Document. |
| UI-AUTH-05 | `?next=/books/new` valid                                             | redirect to /books/new                                                                                                                      |
| UI-AUTH-06 | unsafe next `//evil.com`                                             | safe redirect to /books                                                                                                                     |
| UI-AUTH-07 | unsafe next external URL                                             | /books                                                                                                                                      |
| UI-AUTH-08 | logout button                                                        | POST logout, redirect login, flash "You have been logged out.", session cleared, protected route redirects login with next                  |
| UI-AUTH-09 | anonymous visiting /books/new                                        | redirect login?next=/books/new                                                                                                              |
| UI-AUTH-10 | user visiting delete not applicable URL `/books/1/delete` via UI GET | 404? Route only POST; direct GET shows 404 error page. Note tests should use form/button.                                                   |
| UI-AUTH-11 | user clicks Delete? Button absent in DOM                             | `delete-book` count 0                                                                                                                       |
| UI-AUTH-12 | admin sees Delete button per row                                     | present                                                                                                                                     |
| UI-AUTH-13 | add book link visible only logged in                                 | count toggles                                                                                                                               |
| UI-AUTH-14 | login page demo accounts hint visible                                | text                                                                                                                                        |

### 8.2 Books list UI

| Test ID     | Scenario                                              | Expected                                                                     |
| ----------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| UI-BOOKS-01 | default load                                          | 5 rows; page info "Page 1 of 2"                                              |
| UI-BOOKS-02 | second page                                           | 2 rows; prev link, next disabled                                             |
| UI-BOOKS-03 | pagination retains query                              | URL includes filters + page; page2 title ordering preserved                  |
| UI-BOOKS-04 | result count text                                     | "7 books"                                                                    |
| UI-BOOKS-05 | empty filter result                                   | empty-state "No books found.", pagination pages=1                            |
| UI-BOOKS-06 | filter by search input                                | only matching rows                                                           |
| UI-BOOKS-07 | category filter selection persisted                   | selected attribute                                                           |
| UI-BOOKS-08 | sort/order selection persisted                        | selected attribute                                                           |
| UI-BOOKS-09 | reset filters link                                    | returns /books default                                                       |
| UI-BOOKS-10 | invalid filter handling                               | response 200, flash "Ignored invalid filters: ...", query reset values empty |
| UI-BOOKS-11 | stats widget updates from API                         | totals 7/89 after load                                                       |
| UI-BOOKS-12 | book links to detail                                  | click title -> detail page                                                   |
| UI-BOOKS-13 | price formatting                                      | `$9.99`                                                                      |
| UI-BOOKS-14 | row data-book-id matches API                          | compare                                                                      |
| UI-BOOKS-15 | admin row shows Edit and Delete; user shows Edit only | visibility                                                                   |
| UI-BOOKS-16 | anonymous no Edit/Delete                              | visibility                                                                   |

### 8.3 Book create form

| Test ID      | Scenario                                       | Expected                                                 |
| ------------ | ---------------------------------------------- | -------------------------------------------------------- |
| UI-CREATE-01 | load form anonymous? route login_required      | redirect login                                           |
| UI-CREATE-02 | logged-in load form                            | empty values, mode create, Create button                 |
| UI-CREATE-03 | required field validation per field            | error-{field} shown, status 422, values retained         |
| UI-CREATE-04 | create valid book                              | success flash, redirect detail with fields               |
| UI-CREATE-05 | duplicate ISBN                                 | error-isbn "already exists", status 422, values retained |
| UI-CREATE-06 | stock blank                                    | created with stock 0                                     |
| UI-CREATE-07 | price validation message                       | "must be a number"/">0"                                  |
| UI-CREATE-08 | ISBN validation message                        | "must be exactly 13 digits"                              |
| UI-CREATE-09 | title max length message                       | shown                                                    |
| UI-CREATE-10 | cancel link returns /books                     | no changes                                               |
| UI-CREATE-11 | category select options all categories         | options count 4                                          |
| UI-CREATE-12 | invalid price string remains input value       | retained raw                                             |
| UI-CREATE-13 | created stock default reflected in list/detail | 0                                                        |

### 8.4 Book edit form

| Test ID    | Scenario                                       | Expected                                                   |
| ---------- | ---------------------------------------------- | ---------------------------------------------------------- |
| UI-EDIT-01 | load edit form logged in                       | prefilled values from book                                 |
| UI-EDIT-02 | anonymous edit                                 | redirect login next                                        |
| UI-EDIT-03 | edit non-existing ID                           | 404 error page                                             |
| UI-EDIT-04 | valid full update                              | success flash "Book ... updated.", redirect detail updated |
| UI-EDIT-05 | partial-ish form? edit always sends all fields | if stock blank, stock becomes 0 (important behavior)       |
| UI-EDIT-06 | duplicate ISBN on edit                         | error-isbn already exists, values retained                 |
| UI-EDIT-07 | validation errors per field                    | 422 + errors                                               |
| UI-EDIT-08 | cancel returns? cancel link to /books          | no save                                                    |
| UI-EDIT-09 | cannot edit non-existing                       | 404                                                        |
| UI-EDIT-10 | edits by regular user allowed                  | success (login_required no admin)                          |

### 8.5 Book detail and delete

| Test ID      | Scenario                                       | Expected                                                                                       |
| ------------ | ---------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| UI-DETAIL-01 | existing book                                  | title, all fields visible via testids; price `$...`                                            |
| UI-DETAIL-02 | non-existing book                              | 404 error code/message                                                                         |
| UI-DETAIL-03 | back link                                      | returns /books                                                                                 |
| UI-DELETE-01 | admin confirm accept                           | dialog text contains book title; delete succeeds; flash success; list no longer contains title |
| UI-DELETE-02 | admin confirm cancel                           | dialog then cancel; no delete; book remains                                                    |
| UI-DELETE-03 | direct navigation /books/{id}/delete as GET    | 404 (method not allowed maybe rendered)                                                        |
| UI-DELETE-04 | non-admin no button                            | already; direct POST yields 403 page                                                           |
| UI-DELETE-05 | deleted detail subsequently                    | 404                                                                                            |
| UI-DELETE-06 | admin deletion of last? no special empty pages | okay                                                                                           |

### 8.6 CSV export and upload (playground files)

| Test ID    | Scenario                              | Expected                                             |
| ---------- | ------------------------------------- | ---------------------------------------------------- |
| UI-FILE-01 | download CSV link                     | filename books.csv, MIME text/csv                    |
| UI-FILE-02 | download content                      | header row + 7 seed rows (if reset)                  |
| UI-FILE-03 | download via expect_download          | save and parse, data matches UI list                 |
| UI-FILE-04 | upload valid file                     | upload-result shows `Uploaded {name} ({size} bytes)` |
| UI-FILE-05 | upload empty file (0 bytes)           | upload-result with size 0                            |
| UI-FILE-06 | submit no file                        | no upload-result shown (result None)                 |
| UI-FILE-07 | upload binary/large file              | size correct, no failure (within app limits)         |
| UI-FILE-08 | upload result not shown on first load | count 0                                              |

### 8.7 Playground interactions

| Test ID     | Feature                           | Scenario                                                       | Expected                                                        |
| ----------- | --------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| P-WAIT-01   | auto-wait                         | click load slow                                                | spinner visible, result hidden during load                      |
| P-WAIT-02   | auto-wait                         | wait for completion                                            | spinner hidden, result visible text "Loaded after 2000ms"       |
| P-WAIT-03   | web-first expect                  | use `expect` auto retries                                      | stable                                                          |
| P-DIALOG-01 | alert                             | click alert                                                    | dialog message "Hello from alert"; accept; result `alert shown` |
| P-DIALOG-02 | confirm accept                    | click confirm, accept                                          | result `confirm: true`                                          |
| P-DIALOG-03 | confirm dismiss                   | click confirm, dismiss                                         | result `confirm: false`                                         |
| P-DIALOG-04 | prompt accept default             | click prompt, accept default                                   | result `prompt: anon`                                           |
| P-DIALOG-05 | prompt accept custom              | enter "qa"                                                     | result `prompt: qa`                                             |
| P-DIALOG-06 | prompt dismiss                    | dismiss                                                        | result `prompt: null`                                           |
| P-INPUT-01  | submit disabled until name+terms  | button disabled initially                                      |
| P-INPUT-02  | type name only                    | still disabled                                                 |
| P-INPUT-03  | check terms only                  | disabled                                                       |
| P-INPUT-04  | both name and terms               | enabled                                                        |
| P-INPUT-05  | uncheck terms after enable        | disabled again                                                 |
| P-INPUT-06  | radio default free                | `plan-free` checked                                            |
| P-INPUT-07  | select pro                        | `plan-pro` checked                                             |
| P-INPUT-08  | country selection                 | change to Germany/Brazil                                       |
| P-INPUT-09  | submit                            | result text exact `Hi {name} \| plan={plan} \| country={country}` |
| P-INPUT-10  | whitespace name                   | disabled (trim) but if spaces? button disabled due trim        |
| P-HOVER-01  | tooltip hidden by CSS until hover | not visible initially                                          |
| P-HOVER-02  | hover target                      | tooltip visible                                                |
| P-KEY-01    | Enter key with value              | result `Enter pressed with "value"`                            |
| P-KEY-02    | Escape key                        | input cleared, result "Cleared"                                |
| P-KEY-03    | no result on other keys           | result unchanged                                               |
| P-DRAG-01   | drag card from A to B             | card's parent becomes zone-b                                   |
| P-DRAG-02   | drag B to A                       | parent zone-a                                                  |
| P-FRAME-01  | iframe button                     | use frame_locator, click button, output "Frame button clicked" |
| P-FRAME-02  | new tab                           | expect new page, same frame content and button works           |
| P-DYN-01    | add item                          | first item appears, remove button                              |
| P-DYN-02    | add 3 items                       | item count 3                                                   |
| P-DYN-03    | remove item                       | count decreases, specific item disappears                      |
| P-DYN-04    | empty list initially              | count 0                                                        |

---

## 9. Level 5 — Hybrid E2E

**Add when:** Levels 2–4 green.  
**Marker:** `e2e` (often combines `ui`+`api`)

| Test ID | Scenario                                 | Steps / Expected                                                                           |
| ------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| E2E-01  | API create then UI detail                | POST /api/books; open UI detail by id; fields match; stats increments                      |
| E2E-02  | UI create then API verification          | submit UI form; call GET location/id; fields match API; total count increments             |
| E2E-03  | UI create then list total/count          | result-count reflects +1                                                                   |
| E2E-04  | API update then UI detail                | PATCH title; UI detail and list reflect                                                    |
| E2E-05  | UI edit then API verification            | edit in UI; GET API confirms values and unchanged id/created_at                            |
| E2E-06  | UI delete by admin then API 404          | after confirm, GET /api/books/id =404; total -1; stats updated                             |
| E2E-07  | API delete then UI list no row           | delete via API; refresh UI; row count decreases                                            |
| E2E-08  | admin role end-to-end delete allowed     | login admin UI, delete; API get 404                                                        |
| E2E-09  | user role end-to-end delete forbidden    | login user, no button; direct API POST/DELETE → 403/401 depending channel; no state change |
| E2E-10  | CSV export after UI create               | export contains newly created book                                                         |
| E2E-11  | search/filter parity                     | apply same q/category/min/max/sort via UI and API; row count matches API total             |
| E2E-12  | pagination parity                        | UI row count equals API page size                                                          |
| E2E-13  | auth storage state reuse                 | save admin storage_state; reuse context; can create without repeating login                |
| E2E-14  | two browser contexts                     | admin and user simultaneously; independent sessions and role visibility                    |
| E2E-15  | direct HTTP from browser session         | `context.request.post(delete)` as user → 403                                               |
| E2E-16  | health badge network mocked across pages | badge down when /api/health aborted; app usable                                            |
| E2E-17  | stats network mocked                     | `stats` error state "Stats unavailable" (not crash)                                        |
| E2E-18  | reset between tests                      | create book in one test does not leak to next (isolation)                                  |

---

## 10. Level 6 — Non-functional and cross-cutting

**Add when:** Level 5 green.  
**Marker:** `api` / `ui` depending.

### 10.1 Concurrency and robustness

| Test ID     | Scenario                                     | Expected                                            |
| ----------- | -------------------------------------------- | --------------------------------------------------- |
| NF-CONC-01  | parallel GET /api/books requests (20)        | all 200 same default result                         |
| NF-CONC-02  | create two books with same ISBN concurrently | one 201 and one 409 (at least no duplicate success) |
| NF-CONC-03  | reset during reads (manual)                  | no 500; best-effort                                 |
| NF-IDEMP-01 | GET repeated                                 | stable                                              |
| NF-IDEMP-02 | DELETE repeated                              | first 204, second 404                               |

### 10.2 Network and browser robustness (Playwright)

| Test ID   | Scenario                                        | Expected                                                            |
| --------- | ----------------------------------------------- | ------------------------------------------------------------------- |
| NF-NET-01 | abort `/api/health` on books page               | badge text "API: down", data-state="down", page still renders table |
| NF-NET-02 | abort `/api/stats`                              | stats widget error state, no uncaught exception                     |
| NF-NET-03 | slow stats response                             | page remains usable, no crash                                       |
| NF-NET-04 | assert network response for health on page load | `expect_response` captured                                          |
| NF-ERR-01 | capture console errors across pages             | none unexpected                                                     |
| NF-ERR-02 | capture page errors across pages                | none                                                                |

### 10.3 Security basics

| Test ID   | Scenario                                           | Expected                                         |
| --------- | -------------------------------------------------- | ------------------------------------------------ |
| NF-SEC-01 | XSS in title                                       | detail renders literal text; no dialog triggered |
| NF-SEC-02 | XSS in search q                                    | no script execution                              |
| NF-SEC-03 | open redirect protection on login next             | external next ignored                            |
| NF-SEC-04 | token not accepted in query string                 | 401                                              |
| NF-SEC-05 | malformed bearer remains 401                       | no 500                                           |
| NF-SEC-06 | user cannot delete via API                         | 403 and no state change                          |
| NF-SEC-07 | anonymous cannot create via API                    | 401                                              |
| NF-SEC-08 | error responses do not leak secrets                | no password/token                                |
| NF-SEC-09 | reset endpoint disabled outside test mode (manual) | 404                                              |

### 10.4 Accessibility and UX (basic)

| Test ID    | Scenario                                    | Expected                                   |
| ---------- | ------------------------------------------- | ------------------------------------------ |
| NF-A11Y-01 | each page has page-title testid and heading | present                                    |
| NF-A11Y-02 | form inputs have labels                     | label count matches inputs (manual review) |
| NF-A11Y-03 | keyboard can submit login form with Enter   | redirect success                           |
| NF-A11Y-04 | keyboard can operate playground inputs      | result updates                             |
| NF-A11Y-05 | error text associated with fields           | error testids adjacent                     |

### 10.5 Cross-browser

| Test ID  | Scope                                     | Expected                                                                   |
| -------- | ----------------------------------------- | -------------------------------------------------------------------------- |
| NF-CB-01 | run UI smoke on Firefox                   | pass                                                                       |
| NF-CB-02 | run UI smoke on WebKit                    | pass                                                                       |
| NF-CB-03 | run full UI on Chromium before merge      | pass                                                                       |
| NF-CB-04 | playground dialogs/drag in Firefox/WebKit | basic interactions pass (drag may be browser-dependent; document if flaky) |

### 10.6 Performance (lightweight)

| Test ID    | Scenario                              | Expected                                        |
| ---------- | ------------------------------------- | ----------------------------------------------- |
| NF-PERF-01 | `GET /api/health` p95 < 100ms (local) | pass                                            |
| NF-PERF-02 | `GET /api/books` p95 < 100ms          | pass                                            |
| NF-PERF-03 | slow endpoint max enforced ≤5s        | elapsed ≤5.2s even if ms=999999 requested (cap) |

---

## 11. Level 7 — CI/CD quality gates

**Add when:** Levels 0–6 complete.  
**Marker:** all

| Gate ID | Requirement                                              | Success criteria                              |
| ------- | -------------------------------------------------------- | --------------------------------------------- |
| CI-01   | `lint` job passes (`ruff`)                               | no lint errors                                |
| CI-02   | `api` job runs `pytest -m "not ui"` parallel (`-n auto`) | green                                         |
| CI-03   | `ui` job matrix Chromium/Firefox/WebKit                  | green                                         |
| CI-04   | reports upload (`report.html`, `junit.xml`)              | artifact exists                               |
| CI-05   | traces/screenshots on failure                            | artifact exists if failed                     |
| CI-06   | remove exit-code-5 allowance once tests exist            | workflow updated                              |
| CI-07   | nightly run                                              | green for 7 consecutive nights                |
| CI-08   | flakiness control                                        | no test fails >1% over 20 runs                |
| CI-09   | required status checks on PR                             | configured in branch protection               |
| CI-10   | test runtime budget                                      | API suite <2 min, UI smoke <5 min per browser |

---

## 12. Entry and exit criteria

### Level entry criteria (summary)

- Previous level exit criteria met.
- No unresolved blocking bugs from prior level.
- Required fixtures/helpers implemented.

### Final exit criteria (release of test plan implementation)

- Levels 0–6 all green on CI for all targeted browsers.
- 100% endpoint coverage (every route/method in inventory has at least one test).
- Validation matrix complete (required/invalid/edge cases for login, query params, book fields).
- Error envelope validated for all major error paths.
- Role-based access validated for both API and UI.
- Reports committed/available as artifacts.
- Flakiness observed as zero across 3 consecutive local runs and nightly run.

---

## 13. Coverage and success criteria (high-level)

| Area                                                                       | Coverage target           | Success criteria                                           |
| -------------------------------------------------------------------------- | ------------------------- | ---------------------------------------------------------- |
| API routes (13 endpoints, all methods)                                     | 100%                      | At least one + negative test per route                     |
| UI routes (12+)                                                            | 100%                      | All pages load and main actions tested                     |
| Book validation fields (6 fields + unknown + body errors)                  | 100%                      | All validation branches asserted                           |
| Query parameters (q, category, min/max price, sort, order, page, per_page) | 100%                      | Valid, invalid, boundary covered                           |
| Auth flows                                                                 | 100%                      | Valid, invalid, expired/invalid token, role denial         |
| Status codes documented                                                    | 100%                      | 200, 201, 204, 400, 401, 403, 404, 405, 409, 422 exercised |
| Playground features                                                        | 100%                      | Each README concept has at least one test                  |
| Cross-browser smoke                                                        | Chromium, Firefox, WebKit | Green on CI matrix                                         |

---

## 14. Traceability matrix (feature → tests)

| Feature                 | API tests           | UI tests               | E2E tests       |
| ----------------------- | ------------------- | ---------------------- | --------------- |
| Health                  | API-HLT-\*          | health badge tests     | NF-NET-01       |
| Stats                   | API-ST-\*           | UI-BOOKS-11            | E2E-01/02       |
| Slow                    | API-SLOW-\*         | P-WAIT-\*              | —               |
| Login                   | API-AUTH-LOGIN-\*   | UI-AUTH-01..07         | —               |
| Me / roles              | API-AUTH-ME-\*      | UI header current-user | E2E-08/09       |
| List/filter/sort/page   | API-BOOKS-LIST-\*   | UI-BOOKS-01..10, 14    | E2E-11/12       |
| Read one                | API-BOOKS-GET-\*    | UI-DETAIL-01/02        | E2E-01          |
| Create                  | API-BOOKS-CREATE-\* | UI-CREATE-\*           | E2E-02/03       |
| Replace/patch           | API-BOOKS-UPD-\*    | UI-EDIT-\*             | E2E-04/05       |
| Delete                  | API-BOOKS-DEL-\*    | UI-DELETE-\*           | E2E-06/07/08/09 |
| CSV export              | n/a                 | UI-FILE-01..03         | E2E-10          |
| Upload                  | n/a                 | UI-FILE-04..08         | —               |
| Playground interactions | n/a                 | P-\*                   | —               |
| Reset                   | API-RESET-\*        | n/a                    | E2E-18          |

---

## 15. Risks and assumptions

1. **Statefulness:** app is in-memory; reset endpoint required for isolation. Parallel workers each start separate servers; do not share base URL across workers.
2. **Tokens survive reset** by design, so tests should issue their own tokens and not assume reset logs out API sessions.
3. **UI edit form always submits all fields** (`_form_to_data`), which means blank stock becomes 0; tests must assert this behavior, not treat it as a bug.
4. **UI invalid filters are silently reset**, not surfaced as hard 400; tests assert flash + reset values.
5. **Drag-and-drop and dialog behavior differ slightly across browsers**; mark browser-specific skips only with evidence.
6. **No persistent DB/external services**, so network and load tests are limited to local server behaviour.
7. **Created IDs restart after reset**, so assertions should use returned IDs rather than hard-coded new IDs.
8. **No rate limiting/CORS/CSRF in app**; documented; security tests stay within app's intended behaviour.

---

## Appendix A — Recommended implementation order of test files

1. `tests/api/test_health_stats_slow.py`
2. `tests/api/test_auth.py`
3. `tests/api/test_books_list.py`
4. `tests/api/test_books_crud.py`
5. `tests/api/test_errors_reset.py`
6. `tests/ui/test_smoke.py`
7. `tests/ui/test_auth_ui.py`
8. `tests/ui/test_books_list_ui.py`
9. `tests/ui/test_book_forms.py`
10. `tests/ui/test_delete_export_upload.py`
11. `tests/ui/test_playground.py`
12. `tests/ui/test_network_errors.py`
13. `tests/e2e/test_hybrid_flows.py`
14. Non-functional + CI changes

---

## Appendix B — Suggested fixtures/factories

```python
import itertools
import requests

def api(base_url):
    return requests.Session()  # prepend base_url in helper

def unique_isbn():
    return str(next(itertools.count(10**12)))[:13].rjust(13, "0")

def valid_book(isbn=None):
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": isbn or unique_isbn(),
        "price": 12.5,
        "stock": 3,
        "category": "tech",
    }
```

Run tests level by level, and do not begin Level 3 until Level 2 exit criteria are met.
