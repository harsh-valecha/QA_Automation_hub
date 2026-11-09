import pytest
import json
from pytest_check import check

# validating api health endpoint
def test_api_health(api_client):
    response = api_client.get("/api/health")
    response_text = json.loads(response.text)
    
    # check for response.ok
    check.is_true(response.ok,msg = "API is not working properly")

    # check for response.status_code
    check.equal(response.status_code,200,msg="Status code not 200")

    # check for version 
    check.equal(response_text['version'],'1.0.0',msg = "Version not 1.0.0")

    # check for status in response text
    check.equal(response_text['status'],'ok',msg='Status not ok')

# validating api stats
def test_api_stats(api_client):
    '''
    b'{"by_category":{"fiction":2,"history":1,"science":1,"tech":3},"total_books":7,"total_stock":89}'
    '''
    response = api_client.get('/api/stats')
    response_text = json.loads(response.content)

    # validate the status code
    check.equal(response.status_code,200,msg="status code not 200")

    # validate the number of books 
    check.equal(response_text['total_books'],7,msg = "books count mismatch")

    # validate the total stock 
    check.equal(response_text['total_stock'],89,msg="total stock mismatch")

    # validate books present by categories
    check.is_true("by_category" in response_text,msg="by_category not present")


# auth login admin 
def test_auth_login(api_client):
    '''
    Dummy api response text - 
    '{"role":"admin","token":"token_number","token_type":"Bearer"}\n'
    '''
    response = api_client.post('api/auth/login',
                               json={'username':'admin','password':'admin123'}
                               )
    response_text = json.loads(response.text)

    # validate successful login
    check.equal(response.status_code,200,msg='Admin login unsuccessful')

    # validate non empty token recieved
    check.is_not_none(response_text['token'],msg='Empty token received')

    # validate token type is bearer
    check.equal(response_text['token_type'],"Bearer",msg="Token type is not bearer")

    # validate role is admin
    check.equal(response_text['role'],'admin',msg='Role is not admin')


# validate api/auth/me
@pytest.mark.parametrize("auth_token",["admin"],indirect=True)
def test_auth_me(api_client, auth_token):
    response = api_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # validate the response status code
    check.equal(response.status_code,200,msg='no valid bearer token present ')

    # validate the username 
    check.equal(response.json()['username'],'admin',msg='username mismatch')

    # validate the role
    check.equal(response.json()['role'],'admin',msg='role mismatch')