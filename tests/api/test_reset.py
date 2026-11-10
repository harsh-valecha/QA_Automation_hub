import pytest
from pytest_check import check


@pytest.mark.api
def test_api_reset(api_client):
    response = api_client.post("/api/test/reset")

    check.equal(response.status_code, 204, msg="status code mismatch")