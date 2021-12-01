import pytest
import json
import os
from main import app, db
from models.roles import Role

headers = {
    'Content-Type': 'application/json'
}

@pytest.fixture(scope='session')
def client():
    app.config["TESTING"] = True
    db.create_all()
    db.session.commit()
    
    Role.generate_default_roles()  # generate roles
    
    yield app.test_client()  # tests run here
    
    db.session.remove()
    db.drop_all()  # teardown


def login(client, payload):
    return client.post(
        '/api/v1/accounts/login',
        data=payload,
        headers=headers
    )

def register(client, payload):
    return client.post(
        '/api/v1/accounts/register',
        data=payload,
        headers=headers
    )
   
def logout(client, token):
    return client.delete(
        '/api/v1/accounts/logout',
        headers=token,
    )

def profile(client, token):
    return client.get(
        '/api/v1/accounts/me',
        headers=token,
    )

def refresh_token(client, token):
    return client.post(
        '/api/v1/accounts/refresh',
        headers=token,
    )

def test_env():
    assert os.environ.get('CONFIG_ENV') == 'config.TestConfig'


def test_index(client):
    response = client.get('/', headers=headers)
    assert response.status_code == 200

def test_register(client):
    payload = {
        'username': 'test_user',
        'password': 'pass1234',
        'email': 'test_user@email.com',
        'name': 'test_user'
    }
    rv = register(client, json.dumps(payload))
    assert b'ok' in rv.data
    assert rv.status_code == 201

def test_login_success(client):
    payload  = {
        'username':'test_user',
        'password': 'pass1234',
    }
    rv = login(client, json.dumps(payload))
    assert b"ok" in rv.data
    assert rv.status_code == 200    

def test_login_fails(client):
    payload  = {
        'username':'test_user',
        'password': 'pass12343',
    }
    rv = login(client, json.dumps(payload))
    assert b"fail" in rv.data
    assert rv.status_code == 422    

def test_register_duplicate(client):
    payload = {
        'username': 'test_user',
        'password': 'pass1234',
        'email': 'test_user@email.com',
        'name': 'test_user'
    }

    rv = register(client, json.dumps(payload))
    assert b"fail" in rv.data
    assert rv.status_code == 409    

def test_register_incompleted_data(client):
    payload = {
        'username': 'test_user',
        'password': 'pass1234',
        'email': 'test_user@email.com'
    }
    rv = register(client, json.dumps(payload))
    assert b'fail' in rv.data
    assert rv.status_code == 422

def test__login_use_token_logout(client):
    # login
    payload = {
        'username': 'test_user',
        'password': 'pass1234',
    }

    rv = login(client, json.dumps(payload))
    token = json.loads(rv.data)['data']['access_token']

    assert b'ok' in rv.data
    assert rv.status_code == 200

    # access profile
    access_token = 'Bearer ' + token    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token
    }

    rv = profile(client, headers)
    assert b'user_identity' in rv.data

    # logout
    rv = logout(client, headers)
    assert b'ok' in rv.data

    # visit again after logout
    rv = profile(client, headers)
    assert b'revoked' in rv.data
    assert rv.status_code == 401

def test_login_user_not_found(client):
    payload = {
        'username': 'test_user0',
        'password': 'pass1234',
    }
    rv = login(client, json.dumps(payload))
    assert b'user not' in rv.data
    assert rv.status_code == 422

def test_refresh_token(client):
    # login
    payload = {
        'username': 'test_user',
        'password': 'pass1234',
    }

    rv = login(client, json.dumps(payload))
    ref_token = json.loads(rv.data)['data']['refresh_token']

    assert b'ok' in rv.data
    assert rv.status_code == 200
    # create refresh_token from prev login
    ref_token = 'Bearer ' + ref_token    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ref_token
    }
    
    rv = refresh_token(client, headers)
    assert b'token' in rv.data
    assert rv.status_code == 200
