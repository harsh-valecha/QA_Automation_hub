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
