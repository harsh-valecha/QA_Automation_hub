# Test Plan — QA Automation Practice Hub

**Application:** Flask bookshelf app
**Stack:** pytest, requests, Playwright
**Markers:** `api`, `ui`, `e2e`, `smoke`

## Status key

| Status         | Meaning                                                               |
| -------------- | --------------------------------------------------------------------- |
| ✅ Complete    | Implemented and covered by the current test.                          |
| 🟡 Partial     | A test exists, but it does not yet cover the full scenario described. |
| ⬜ Not started | Test still needs to be written.                                       |

This inventory is the checklist for remaining test work. Each scenario belongs
to the file shown; update its status when the test is implemented and verified.
Do not duplicate API-only or UI-only checks in the E2E suite.

## API tests

### [`tests/api/test_health_stats_slow.py`](./tests/api/test_health_stats_slow.py)

| Test                                      | Description                                                                                                | Status      |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ----------- |
| `test_api_health`                         | Check `GET /api/health` returns success, JSON content type, status `ok`, and version `1.0.0`.              | ✅ Complete |
| `test_api_repeated`                       | Call the health endpoint 20 times and check every response succeeds.                                       | ✅ Complete |
| `test_api_seed_stats_smoke`               | Check seeded book count, stock total, and complete category counts from `GET /api/stats`.                  | ✅ Complete |
| `test_api_slow_wait`                      | Check `GET /api/slow?ms=0` succeeds and reports zero wait time.                                            | ✅ Complete |
| `test_api_slow_delay_limits`              | Check zero, default, and capped slow delays report the expected wait and take a reasonable amount of time. | ✅ Complete |
| `test_api_slow_rejects_non_integer_delay` | Check a non-integer `ms` value returns 400 with `bad_request`.                                             | ✅ Complete |
| `test_api_stats_follow_book_lifecycle`    | Create, update, and delete a book; verify stats change and return to the seeded values.                    | ✅ Complete |

### [`tests/api/test_auth.py`](./tests/api/test_auth.py)

| Test                                          | Description                                                                                                  | Status      |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------- |
| `test_auth_login`                             | Check admin login returns a non-empty bearer token and the admin role.                                       | ✅ Complete |
| `test_auth_me`                                | Check an admin bearer token returns the correct username and role from `/api/auth/me`.                       | ✅ Complete |
| `test_auth_me_no_token`                       | Check `/api/auth/me` rejects a request without a token.                                                      | ✅ Complete |
| `test_auth_login_returns_token_for_each_role` | Check both admin and user login responses and use each token to verify `/api/auth/me`.                       | ✅ Complete |
| `test_auth_login_rejects_invalid_credentials` | Check wrong passwords and unknown users return 401 without issuing a token.                                  | ✅ Complete |
| `test_auth_login_validates_request_body`      | Check missing/empty fields, non-object JSON, malformed JSON, and non-JSON bodies return the expected errors. | ✅ Complete |
| `test_auth_me_rejects_invalid_bearer_token`   | Check malformed authorization schemes and unknown tokens return 401 with a Bearer challenge.                 | ✅ Complete |

### [`tests/api/test_api_books.py`](./tests/api/test_api_books.py)

| Test                                                    | Description                                                                                              | Status      |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ----------- |
| `test_api_books`                                        | Check the default book-list total, first-page size, current page, and page count.                        | ✅ Complete |
| `test_api_first_book`                                   | Check seeded book ID 1 can be retrieved and includes a title.                                            | ✅ Complete |
| `test_api_books_out_of_bound`                           | Check an unknown book ID returns 404 / `not_found`, and unsupported methods return JSON 405.             | ✅ Complete |
| `test_api_books_valid_token`                            | Check an admin can create a book, verify its submitted fields, and retrieve it using `Location`.         | ✅ Complete |
| `test_api_books_patch`                                  | Check an admin can PATCH a book, unsupplied values are preserved, and PUT replaces the full book.        | ✅ Complete |
| `test_api_books_delete_multiple`                        | Check deleting a book succeeds once and returns 404 on a repeated delete.                                | ✅ Complete |
| `test_api_books_pagination`                             | Check pagination returns all books without missing or duplicate IDs, using `per_page`.                   | ✅ Complete |
| `test_api_category_counts`                              | Check category counts across all pages of the books list.                                                | ✅ Complete |
| `test_api_books_total_and_stock`                        | Check the paginated books list contains all 7 seeded books and their total stock is 89.                  | ✅ Complete |
| `test_list_books_defaults_and_schema_smoke`             | Check default list metadata and required fields on every returned book.                                  | ✅ Complete |
| `test_get_seeded_book_smoke`                            | Check ID 1 matches the known seed: Clean Code, ISBN `9780132350884`, category `tech`.                    | ✅ Complete |
| `test_list_books_search_filter_and_sort`                | Check search, category, price bounds, sorting, and no-match results.                                     | ✅ Complete |
| `test_list_books_invalid_query`                         | Check invalid pagination, filters, sorting, ordering, and price bounds return 400 / `bad_request`.       | ✅ Complete |
| `test_create_book_rejects_invalid_payloads`             | Check required fields, field limits, ISBN, price, stock, category, unknown fields, and malformed bodies. | ✅ Complete |
| `test_create_book_rejects_duplicate_isbn`               | Check duplicate ISBN returns 409 and does not change the book count.                                     | ✅ Complete |
| `test_update_book_validates_payload_and_duplicate_isbn` | Check incomplete/invalid updates and duplicate ISBN errors.                                              | ✅ Complete |
| `test_book_mutations_require_authentication`            | Check POST, PUT, and PATCH reject missing or invalid tokens without changing data.                       | ✅ Complete |
| `test_delete_book_requires_admin`                       | Check admin delete succeeds, user delete is forbidden, and anonymous delete is unauthorized.             | ✅ Complete |
| `test_parallel_book_reads_succeed`                      | Check concurrent health, stats, list, and book-detail reads return valid responses.                      | ✅ Complete |

### [`tests/api/test_reset.py`](./tests/api/test_reset.py)

| Test                                      | Description                                                                   | Status         |
| ----------------------------------------- | ----------------------------------------------------------------------------- | -------------- |
| `test_api_reset`                          | Check the test reset endpoint responds with 204.                              | 🟡 Partial     |
| `test_reset_restores_seed_data`           | Change book data, reset it, and verify seed stats and book ID 1 are restored. | ⬜ Not started |
| `test_reset_route_is_disabled_by_default` | Check a separate app with test routes disabled returns 404 for reset.         | ⬜ Not started |

## UI tests

### [`tests/ui/test_smoke.py`](./tests/ui/test_smoke.py)

| Test                                                | Description                                                                         | Status         |
| --------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------- |
| `test_books_page_loads`                             | Open `/books` and check the page title is Books.                                    | ✅ Complete    |
| `test_core_pages_render_smoke`                      | Check login, playground, and playground-frame pages render without uncaught errors. | ✅ Complete    |
| `test_root_redirects_and_unknown_route_renders_404` | Check the root redirect and unknown-route 404 page.                                 | ✅ Complete    |
| `test_books_csv_download_smoke`                     | Check CSV download filename, content type, header columns, and seven data rows.     | ✅ Complete    |
| `test_health_failure_keeps_books_page_usable`       | Fail the health request and check the page remains usable with a down badge.        | ⬜ Not started |
| `test_stats_failure_shows_unavailable_state`        | Fail the stats request and check the page remains usable with unavailable stats.    | ⬜ Not started |

### [`tests/ui/test_ui_books.py`](./tests/ui/test_ui_books.py)

| Test                                                            | Description                                                                              | Status         |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------- |
| `test_login_logout_and_role_navigation`                         | Check admin/user navigation, role-specific delete controls, and logout.                  | ⬜ Not started |
| `test_failed_login_and_unsafe_next_redirect`                    | Check failed-login feedback and that unsafe `next` URLs cannot redirect off-site.        | ⬜ Not started |
| `test_anonymous_access_to_protected_book_forms`                 | Check anonymous visits to create/edit pages redirect to login.                           | ⬜ Not started |
| `test_books_search_filters_sort_and_pagination`                 | Check visible results, pagination, retained filters, reset, and invalid-filter feedback. | ⬜ Not started |
| `test_create_book_form_success_and_validation`                  | Check successful creation plus validation errors and retained form values.               | ⬜ Not started |
| `test_edit_book_form_prefills_saves_and_rejects_invalid_values` | Check edit form values, successful edits, validation, and retained input.                | ⬜ Not started |
| `test_book_detail_and_delete_confirmation`                      | Check book details, delete confirmation, and user delete restrictions.                   | ⬜ Not started |
| `test_book_title_is_rendered_as_text`                           | Check user-supplied HTML-like titles render as text and do not execute.                  | ⬜ Not started |
| `test_login_and_book_form_controls_have_labels`                 | Check login and book form controls have usable labels and login works by keyboard.       | ⬜ Not started |

### [`tests/ui/test_files_playground.py`](./tests/ui/test_files_playground.py)

| Test                                                   | Description                                                                      | Status         |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- | -------------- |
| `test_playground_upload_echoes_filename_and_size`      | Check uploading an in-memory file displays its filename and byte size.           | ⬜ Not started |
| `test_playground_slow_result_waits_for_response`       | Check the slow-action spinner and the completed result.                          | ⬜ Not started |
| `test_playground_alert_confirm_and_prompt`             | Check alert, confirm, and prompt dialogs for accept, dismiss, and input cases.   | ⬜ Not started |
| `test_playground_inputs_enable_submit_and_show_values` | Check input, checkbox, select, and submit behavior.                              | ⬜ Not started |
| `test_playground_keyboard_enter_and_escape`            | Check Enter reports text and Escape clears the input.                            | ⬜ Not started |
| `test_playground_hover_tooltip_and_drag_drop`          | Check hover tooltip and drag/drop destination.                                   | ⬜ Not started |
| `test_playground_iframe_new_tab_and_dynamic_list`      | Check iframe interaction, new-tab content, and dynamic-list add/remove behavior. | ⬜ Not started |

## End-to-end tests

### [`tests/e2e/test_flows.py`](./tests/e2e/test_flows.py)

| Test                                                             | Description                                                              | Status         |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------- |
| `test_ui_created_book_is_visible_through_api`                    | Create a book in the UI and verify its data and stats through the API.   | ⬜ Not started |
| `test_api_updated_and_deleted_book_is_reflected_in_ui`           | Update/delete through the API and verify the corresponding UI state.     | ⬜ Not started |
| `test_user_and_admin_delete_permissions_match_across_ui_and_api` | Verify user/admin delete permissions and final state across both layers. | ⬜ Not started |

## Shared expectations

- Seed data: 7 books, total stock 89; categories: 3 tech, 2 fiction,
  1 science, and 1 history.
- API book fields use `category` (not `genre`). The default list page size is 5.
- Demo accounts are `admin/admin123` and `user/user123`; only admins may delete.
- The autouse fixture resets data before each test. Use returned IDs for created
  books and obtain tokens within each test.
- Use `book_factory` for valid unique payloads; its category field is `category`.
- The reset route is enabled by the test server. Do not change shared server
  configuration to test the route-disabled case.
- Use `data-testid` selectors for UI tests. UI error spans currently lack an
  `aria-describedby` association; do not assert that association.

## Running and completion

```bash
pytest
pytest -m "not ui"
pytest -m ui --browser chromium
```

Run the browser-matrix smoke tests on Firefox and WebKit as configured in CI.
The inventory is complete when all intended scenarios above are implemented,
their status is updated, and the relevant marked suites pass.
