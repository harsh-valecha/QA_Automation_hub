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