import pytest
from pytest_check import check

# health and stats tests

def test_api_health(api_client):
    response = api_client.get('api/health')
    response_json = response.json()
    
    #status validation
    check.equal(response.status_code,200,msg='status code mismatch')

    # content validation
    check.equal(response.headers['content-type'] , 'application/json',msg='content type mismatch')

    # status and version
    check.equal(response_json['status'],'ok',msg='status mismatch')

    check.equal(response_json['version'],'1.0.0',msg='version mismatch')


# repeated calls
def test_api_repeated(api_client):
    for i in range(20):
        response = api_client.get('api/health')
        print(f'Called {i} time')
        assert response.status_code == 200

# basic stats
def test_api_stats(api_client):
    response = api_client.get('api/books')
    response_json = response.json()

    
    # check total books
    check.equal(response_json['total'],7,msg='Total books mismatch')

    # collect stock and assert
    items = response_json['items']
    stock=0
    for item in items:
        stock +=item['stock']

    # verify stock total
    check.equal(stock,84,msg='stock total mismatch')


# category counts 
def test_api_category_counts(api_client):
    response = api_client.get('api/books')
    response_json = response.json()

    # verify the category counts
    tech = 0
    fiction=0
    science = 0
    history = 0

    for item in response_json['items']:
        category = item['category']
        if category=='tech':
            tech+=1
        elif category=='fiction':
            fiction+=1
        elif category=='science':
            science+=1
        else:
            history+=1
    # verifying the counts
    check.equal(tech,2,msg='tech count mismatch')
    check.equal(fiction,1,msg='fiction count mismatch')
    check.equal(science,1,msg='science count mismatch')
    check.equal(history,1,msg='history count mismatch')

 