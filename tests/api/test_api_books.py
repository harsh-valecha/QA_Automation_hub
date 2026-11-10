import pytest
from pytest_check import check


@pytest.mark.api
def test_api_books_total_and_stock(api_client):
    pages = []
    for page_number in (1, 2):
        response = api_client.get("/api/books", params={"page": page_number})
        assert response.status_code == 200
        pages.append(response.json())

    check.equal(pages[0]["total"], 7, msg="Total books mismatch")
    all_items = [item for page_data in pages for item in page_data["items"]]
    check.equal(sum(item["stock"] for item in all_items), 89, msg="stock total mismatch")


@pytest.mark.api
def test_api_books_pagination(api_client):
    page_size = 3
    first_response = api_client.get(
        "/api/books", params={"page": 1, "per_page": page_size}
    )
    assert first_response.status_code == 200
    pages = [first_response.json()]
    total = pages[0]["total"]
    page_count = (total + page_size - 1) // page_size

    for page_number in range(2, page_count + 1):
        response = api_client.get(
            "/api/books",
            params={"page": page_number, "per_page": page_size},
        )
        assert response.status_code == 200
        pages.append(response.json())

    for page_number, page_data in enumerate(pages, 1):
        check.equal(page_data["total"], total, msg="total books changed between pages")
        expected_size = min(page_size, total - (page_number - 1) * page_size)
        check.equal(
            len(page_data["items"]),
            expected_size,
            msg=f"page {page_number} size mismatch",
        )

    all_items = [item for page_data in pages for item in page_data["items"]]
    check.equal(len(all_items), total, msg="pagination did not return every book")
    book_ids = [item["id"] for item in all_items]
    check.equal(len(set(book_ids)), total, msg="pagination returned duplicate books")


@pytest.mark.api
def test_api_category_counts(api_client):
    category_counts = {"tech": 0, "fiction": 0, "science": 0, "history": 0}

    for page_number in (1, 2):
        response = api_client.get("/api/books", params={"page": page_number})
        assert response.status_code == 200

        for item in response.json()["items"]:
            category_counts[item["category"]] += 1

    check.equal(category_counts["tech"], 3, msg="tech count mismatch")
    check.equal(category_counts["fiction"], 2, msg="fiction count mismatch")
    check.equal(category_counts["science"], 1, msg="science count mismatch")
    check.equal(category_counts["history"], 1, msg="history count mismatch")


@pytest.mark.api
@pytest.mark.smoke
def test_api_books(api_client):
    response = api_client.get("/api/books")
    response_json = response.json()

    check.equal(response.status_code, 200, msg="status code mismatch")
    check.equal(response_json["total"], 7, msg="total books count mismatch")
    check.equal(len(response_json["items"]), 5, msg="items count mismatch")
    check.equal(response_json["page"], 1, msg="page number mismatch")
    check.equal(response_json["pages"], 2, msg="total pages count mismatch")


@pytest.mark.api
@pytest.mark.smoke
def test_api_first_book(api_client):
    response = api_client.get("/api/books/1")
    response_json = response.json()

    check.equal(response.status_code, 200, msg="status code mismatch")
    check.is_true("title" in response_json, msg="title not present in response")


@pytest.mark.api
def test_api_books_out_of_bound(api_client):
    response = api_client.get("/api/books/9999")
    response_json = response.json()

    check.equal(response.status_code, 404, msg="status code mismatch")
    check.equal(response_json["error"], "not_found", msg="Book with mentioned index not found")


@pytest.mark.api
@pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
def test_api_books_valid_token(api_client, auth_token):
    response = api_client.post(
        "/api/books",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "title": "The ghost town",
            "author": "kamlesh jagpat",
            "isbn": "1111111111111",
            "price": 200,
            "stock": 10,
            "category": "history",
        },
    )

    response_json = response.json()
    check.equal(response.status_code, 201, msg="status code mismatch")
    check.is_true("Location" in response.headers, msg="location not found in response headers")
    check.is_true("created_at" in response_json, msg="created_at not present in response json")


@pytest.mark.api
@pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
def test_api_books_patch(api_client, auth_token):
    response = api_client.patch(
        "/api/books/1",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"title": "Totally true"},
    )
    response_json = response.json()

    check.equal(response.status_code, 200, msg="Status code mismatch")
    check.equal(response_json["title"], "Totally true", msg="patch not updated correctly")


@pytest.mark.api
@pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
def test_api_books_delete_multiple(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response_first = api_client.delete("/api/books/1", headers=headers)
    response_second = api_client.delete("/api/books/1", headers=headers)

    check.equal(response_first.status_code, 204, msg="Error in deletion")
    check.equal(response_second.status_code, 404, msg="Mismatch in second response deletion")