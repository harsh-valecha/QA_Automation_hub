import json
import pytest
from pytest_check import check


@pytest.mark.api
@pytest.mark.smoke
def test_api_health(api_client):
    response = api_client.get("/api/health")
    response_text = json.loads(response.text)

    check.is_true(response.ok,msg = "API is not working properly")
    check.equal(response.status_code,200,msg="Status code not 200")
    check.equal(response.headers["content-type"], "application/json", msg="content type mismatch")
    check.equal(response_text['version'],'1.0.0',msg = "Version not 1.0.0")
    check.equal(response_text['status'],'ok',msg='Status not ok')


@pytest.mark.api
def test_api_repeated(api_client):
    for call_number in range(20):
        response = api_client.get("/api/health")
        print(f"Called {call_number} time")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.smoke
def test_api_seed_stats_smoke(api_client):
    response = api_client.get("/api/stats")
    response_json = response.json()

    check.equal(response.status_code, 200, msg="status code not 200")
    check.equal(response_json["total_books"], 7, msg="books count mismatch")
    check.equal(response_json["total_stock"], 89, msg="total stock mismatch")
    check.equal(
        response_json["by_category"],
        {"fiction": 2, "history": 1, "science": 1, "tech": 3},
        msg="category counts mismatch",
    )


@pytest.mark.api
def test_api_slow_wait(api_client):
    response = api_client.get("/api/slow?ms=0")
    response_json = response.json()

    check.equal(response.status_code, 200, msg="status code mismatch")
    check.equal(response_json["waited_ms"], 0, msg="wait time mismatch")


@pytest.mark.api
def test_api_slow_delay_limits(api_client):
    response1 = api_client.get("/api/slow")
    response2 = api_client.get("/api/slow?ms=10000")

    check.equal(response1.status_code,200,msg="status code mismatch")
    check.equal(response2.status_code,200,msg="status code mismatch")



@pytest.mark.api
def test_api_slow_rejects_non_integer_delay(api_client):
    response = api_client.get("api/slow?ms=helo")

    check.equal(response.status_code,400,msg="status code mismatch for non integer ms in api/slow")


@pytest.mark.api
@pytest.mark.parametrize("auth_token",['admin'],indirect=True)
def test_api_stats_follow_book_lifecycle(api_client,auth_token):
    initial_stats = api_client.get("api/stats")
    initial_resp = initial_stats.json()

    '''
    {'by_category': {'fiction': 2, 'history': 1, 'science': 1, 'tech': 3}, 'total_books': 7, 'total_stock': 89}
    '''
    # create a book
    create_resp = api_client.post('api/books',
                                  headers={"Authorization":f'Bearer {auth_token}'},
                                  json={
                                        "title": "The idle man",
                                        "author": "Nikamma kaluta",
                                        "isbn": "1111111111111",
                                        "price": 230,
                                        "stock": 12,
                                        "category": "science",
                                        },)
    id = create_resp.json()['id']
    check.equal(create_resp.status_code,201,msg="status mismatch for book creation")

    # update a book
    update_resp = api_client.put(f'api/books/{id}',
                                 headers={"Authorization":f"Bearer {auth_token}"},
                                 json={
                                        "title": "The idle man",
                                        "author": "Kamlesh Karapathy",
                                        "isbn": "1111111111111",
                                        "price": 230,
                                        "stock": 12,
                                        "category": "science",
                                        },)

    check.equal(update_resp.status_code,200,msg = "status mismatch for book updation")

    # delete a book
    delete_resp = api_client.delete(f'api/books/{id}',
                                    headers={"Authorization":f"Bearer {auth_token}"})

    check.equal(delete_resp.status_code,204,msg="status code mismatch for book deletion")

    # final stats
    final_stats = api_client.get("api/stats")
    final_resp = final_stats.json()

    check.equal(initial_resp,final_resp,msg="Data mismatch ")