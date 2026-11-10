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


@pytest.mark.api
@pytest.mark.parametrize(
    ("role", "auth_token"),
    [("user", "user"), ("admin", "admin")],
    indirect=["auth_token"],
    ids=["user", "admin"],
)
def test_auth_login_returns_token_for_each_role(api_client, role, auth_token):
    response = api_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    check.equal(response.status_code, 200, msg="invalid bearer token received")
    check.equal(response.json()["role"], role, msg="role mismatch")



@pytest.mark.api
def test_auth_login_rejects_invalid_credentials(api_client):
    response = api_client.post('api/auth/login',
                               json = {'username':'test','password':'test123'})

    response_json = response.json()
    check.equal(response.status_code,401,msg='status code mismatch')
    check.equal(response_json['error'],'unauthorized',msg='error mismatch')
    check.equal(response_json['message'],'Invalid username or password',msg='message mismatch')


@pytest.mark.api
def test_auth_login_validates_request_body(api_client):
    response1 = api_client.post('api/auth/login',
                               json={'username':'','password':'user123'})

    check.equal(response1.status_code,422,msg='status mismatch missing username')

    response2 = api_client.post('api/auth/login',
                               json={'username':'user','password':''})

    check.equal(response2.status_code,422,msg='status mismatch missing password')

    response3 = api_client.post('api/auth/login',
                                   json={'username':'','password':''})
    
    check.equal(response3.status_code,422,msg='status mismatch missing both')

    response4 = api_client.post('api/auth/login',
                                   json={'username':'user'})
    
    check.equal(response4.status_code,422,msg='status mismatch unprovided pwd')

    malformed_payload = '{"username": "user", "password": "user123"'
    response5 = api_client.post('api/auth/login',
                                   json = malformed_payload)
                                        
    check.equal(response5.status_code,422,msg='status mismatch malformed payload1')

    malformed_payload2 = "{'username': 'user', 'password': 'user123'}"
    response6 = api_client.post('api/auth/login',
                                    json = malformed_payload2)
                                        
    check.equal(response6.status_code,422,msg='status mismatch malformed payload1')


@pytest.mark.api
def test_auth_me_rejects_invalid_bearer_token(api_client):
    resp1 = api_client.get('api/auth/me',
                           headers={'Authorization':f'Bearer 123test12333'})

    
    check.equal(resp1.status_code,401,msg='status mismatch invalid bearer token')

    resp2 = api_client.get('api/auth/me',
                           headers={'Authorization':'Bearer '})

    check.equal(resp2.status_code,401,msg='status mismatch for missing bearer token')