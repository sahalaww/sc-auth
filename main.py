from flask import Flask, jsonify, make_response
from config import DevConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv('.env')
app = Flask(__name__)

app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models.users import User
from models.roles import Role

from api.v1 import *

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
