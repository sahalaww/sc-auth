from flask import Flask, jsonify, make_response
from config import DevConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
import os
import pytest

load_dotenv('.env')
app = Flask(__name__)

sconfig = os.environ.get('CONFIG_ENV')
JWT_KEY = os.environ.get('SECRET_KEY')
app.config.from_object(sconfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config["JWT_SECRET_KEY"] = JWT_KEY
jwt = JWTManager(app)

from models.users import User
from models.roles import Role
from models.tokens import Token

from api.v1.accounts import *

version = "0.2.1"

@app.route('/')
def index():
    response = {
        'status': 'ok',
        'code': 200,
        'data':{
            'version': version
        }
    }
    return make_response(jsonify(response), 200)

@app.errorhandler(Exception)
def internal_error(err):
    """
    Global Route to handle All Error Status Codes
    """
    if isinstance(err, HTTPException):
        if type(err).__name__ == 'NotFound':
            err.description = "Not found"
        message = err.description
        code = err.code
    else:
        message = err
        code = 500

    response = {
        'status': 'fail',
        'code': int(code),
        'data': {
            'error': message
        },
    }
    return make_response(jsonify(response), code)

@app.errorhandler(400)
def handle_404(exception):
    """
    handles 400 errros, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    
    response = {
        'status': 'fail',
        'code': int(code),
        'data': {
            'error': description
        },
    }
    return make_response(jsonify(response), code)

@app.errorhandler(404)
def handle_404(exception):
    """
    handles 404 errors, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    response = {
        'status': 'fail',
        'code': int(code),
        'data': {
            'error': description
        },
    }
    return make_response(jsonify(response), code)

@app.cli.command()
def run_test():
    """test """
    pytest.main(["-s", "tests"])

@app.cli.command()
def seed_role():
   """Seed user roles """
   Role.generate_default_roles()
