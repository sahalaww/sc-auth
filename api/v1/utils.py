"""Various helpers for auth

Heavily inspired by
https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/blocklist_database.py
"""
from datetime import datetime
from flask import jsonify, make_response
from flask_jwt_extended import decode_token, get_jwt_identity,verify_jwt_in_request

from sqlalchemy.orm.exc import NoResultFound

from main import db
from models.tokens import Token
from models.users import User
from functools import wraps

def add_token_to_database(encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_identity = decoded_token[identity_claim]
    expires = datetime.fromtimestamp(decoded_token["exp"])
    revoked = False

    db_token = Token(
        jti=jti,
        token_type=token_type,
        user_uuid=user_identity,
        expires=expires,
        revoked=revoked,
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(jwt_payload):
    jti = jwt_payload["jti"]
    try:
        token = Token.query.filter_by(jti=jti).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(token_jti, user):
    try:
        token = Token.query.filter_by(jti=token_jti, user_uuid=user).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise Exception("Could not find the token {}".format(token_jti))

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_identity = get_jwt_identity()
            role_name = User.query.filter_by(uuid=user_identity).first().roles.name
            if role_name == "Admin" :
                return fn(*args, **kwargs)
            else:
                response = {
                    'status': 'fail',
                    'code': 403,
                    'data': {
                        'error': 'not admin'
                    }
                }
                return make_response(jsonify(response), 403)
        return decorator
    return wrapper
