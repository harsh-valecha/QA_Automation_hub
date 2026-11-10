import pytest
from pytest_check import check


@pytest.mark.api
@pytest.mark.smoke
def test_auth_login(api_client):
    response = api_client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    response_json = response.json()

    check.equal(response.status_code, 200, msg="Admin login unsuccessful")
    check.is_not_none(response_json["token"], msg="Empty token received")
    check.equal(response_json["token_type"], "Bearer", msg="Token type is not bearer")
    check.equal(response_json["role"], "admin", msg="Role is not admin")


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.parametrize("auth_token", ["admin"], indirect=True)
def test_auth_me(api_client, auth_token):
    response = api_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    check.equal(response.status_code, 200, msg="no valid bearer token present")
    check.equal(response.json()["username"], "admin", msg="username mismatch")
    check.equal(response.json()["role"], "admin", msg="role mismatch")


@pytest.mark.api
def test_auth_me_no_token(api_client):
    response = api_client.get("/api/auth/me")

    check.equal(response.status_code, 401, msg="status code mismatch")