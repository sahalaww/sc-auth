from flask import Flask, jsonify, make_response
from config import DevConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
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

version = "0.1"

@app.route('/')
def index():
    response = {
        'status': 'ok',
        'status_code': 200,
        'data':{
            'version': version
        }
    }

    return make_response(jsonify(response), 200)

@app.cli.command()
def run_test():
    """test """
    pytest.main(["-s", "tests"])