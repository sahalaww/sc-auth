import pytest
import json
import os

from werkzeug.security import generate_password_hash
from main import app, db
from models.roles import Role
from models.users import User
import uuid 

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
    assert b'ok' in rv.data

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

def test_create_admin():
    role_admin_id = Role.query.filter_by(name='Admin').first().id
    username ='adminok'
    password = generate_password_hash('admin33')

    create_admin = User(
        uuid=uuid.uuid4().hex,
        username=username,
        password=password,
        email='admin@email.com',
        name='admin',
        role_id=role_admin_id
    )
    db.session.add(create_admin)
    db.session.commit()

    assert create_admin.username == username

def test_only_admin(client):
    # admin login
    payload = {
        'username': 'adminok',
        'password': 'admin33'
    }

    rv = login(client, json.dumps(payload))

    access_token = json.loads(rv.data)['data']['access_token']

    assert b'ok' in rv.data
    assert rv.status_code == 200

    # admin access
    access_token = 'Bearer ' + access_token    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token
    }
    
    rv = client.get(
        '/api/v1/users',
        headers=headers
    )
    assert b'ok' in rv.data

    # non admin login
    payload = {
        'username': 'test_user',
        'password': 'pass1234'
    }

    rv = login(client, json.dumps(payload))

    access_token = json.loads(rv.data)['data']['access_token']

    assert b'ok' in rv.data
    assert rv.status_code == 200
    
    # non admin access
    access_token = 'Bearer ' + access_token    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': access_token
    }
    
    rv = client.get(
        '/api/v1/users',
        headers=headers
    )
    assert b'fail' in rv.data