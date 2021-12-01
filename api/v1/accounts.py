from flask.helpers import make_response
from main import app, db, jwt
from models.users import User
from models.roles import Role
from flask import request, jsonify
from schemas.user import (
    UserRegisterSchema,
    UserLoginSchema,
    UsersResponse,
    UserRegisterAdminSchema
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound     
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import (
    add_token_to_database, 
    revoke_token, 
    is_token_revoked,
    admin_required
)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError
import uuid

def insert_user_data(data,role_name):
    try:
        role = Role.query.filter_by(name=role_name).first()
        new_user = User(username = data['username'],
            uuid = uuid.uuid4().hex,
            email = data['email'],
            name = data['name'],
            role_id = role.id,
            password = generate_password_hash(data['password']),
        )
        db.session.add(new_user)
        db.session.commit()
        response = {
            'status': 'ok',
            'code': 201
        }
    
    except AssertionError as err_assertion:
        db.session.rollback()
        response = {
            'status': 'fail',
            'code': 400,
            'data': {
                'error': err_assertion 
            }
        }

    except IntegrityError as err_integrity:
        db.session.rollback()
        error_info = err_integrity.orig.args
        response = {
            'status': 'fail',
            'code': 409,
            'data': {
                'error': error_info[0]
            }
        }

    except Exception as err_exception:
        db.session.rollback()
        response = {
            'status': 'fail',
            'code': 500,
            'data': {
                'error': 'server error/invalid data'
            }
        }
    return response

@app.route('/api/v1/accounts/register', methods=['POST'])
def register():
    data = request.json
    try:
        UserRegisterSchema().load(data)
        response = insert_user_data(data, 'User')

        return make_response(jsonify(response), response['code'])
    
    except ValidationError as err_validation:
        response = {
            'status': 'fail',
            'code': 422,
            'data': {
                'error': err_validation.messages
            }
        }
    return make_response(jsonify(response), response['code'])


@app.route('/api/v1/accounts/login', methods=['POST'])
def login():
    try:
        UserLoginSchema().load(request.json)
        username = request.json['username']
        password = request.json['password']
        user_login = User.query.filter_by(username=username).first()

        if not user_login:
            response = {
                'status': 'fail',
                'code': 422,
                'data': {
                    'error': 'user not found'
                }
            }
            return make_response(jsonify(response), 422)
        
        check = check_password_hash(user_login.password, password)
        if check:
            access_token = create_access_token(identity=user_login.uuid)
            refresh_token = create_refresh_token(identity=user_login.uuid)
            add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
            add_token_to_database(refresh_token, app.config["JWT_IDENTITY_CLAIM"])
            response = {
                'status': 'ok',
                'code': 200,
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            }
            return make_response(jsonify(response), 200)
        else:
            response = {
                'status': 'fail',
                'code': 422,
                'data': {
                    'error': 'bad username/password'
                }
            }
            return make_response(jsonify(response), 422)
        
    except ValidationError as er:
        response = {
            'status': 'fail',
            'code': 422,
            'data': {
                'error': er.messages
            }
        }
        return make_response(jsonify(response), 422)        

@app.route('/api/v1/accounts/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    response = {
        'status': 'ok',
        'code': 200,
        'data': 'The token has been revoked'
    }
    return make_response(jsonify(response), 200) 

@app.route('/api/v1/accounts/me', methods=['GET'])
@jwt_required()
def me():
    user_identity = get_jwt_identity()
    user_data = User.query.filter_by(uuid=user_identity).first()
    response = {
        'status': 'ok',
        'code': 200,
        'data': UsersResponse().dump(user_data)
    }
    return make_response(jsonify(response), 200) 

@app.route('/api/v1/accounts/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = {
        'status': 'ok',
        'code': 200,
        'data': {
            'access_token': access_token
        }
    }
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    return make_response(jsonify(response), 200)
 
@app.route('/api/v1/users', methods=['GET', 'POST', 'DELETE'])
@admin_required()
def users():
    if request.method == 'GET':
        users = User.query.all()
        users_json = UsersResponse(many=True).dump(users)
        response = {
            'status': 'ok',
            'code': 200,
            'data': users_json
        }
        return make_response(jsonify(response), 200)
    
    elif request.method == 'POST':
        data = request.json
        try:
            UserRegisterAdminSchema().load(data)
            response = insert_user_data(data, data['role_name'])
            return make_response(jsonify(response), response['code'])
        
        except ValidationError as er:
            response = {
                'status': 'fail',
                'code': 422,
                'data': {
                    'error': er.messages
                }
            }
        return make_response(jsonify(response), response['code'])

@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    identity = jwt_payload["sub"]
    return User.query.filter_by(uuid=identity).one()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_headers, jwt_payload):
    return is_token_revoked(jwt_payload)

@jwt.revoked_token_loader
def expired_token_callback(jwt_headers, jwt_payload):
    return make_response(jsonify({
        'status': 'fail',
        'code': 401,
        'data': {
            'error': 'The token has revoked'
        }
    }), 401)

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return make_response(jsonify({
        'status': 'fail',
        'code': 401,
        'data': {
            'error': 'The token has expired'
        }
    }), 401)