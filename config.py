from datetime import timedelta
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    DEVELOPMENT = True
    JSON_SORT_KEYS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
class TestConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT= True
    TESTING = True
    # DB_HOST = os.environ.get('DB_HOST') 
    # DB_USER = os.environ.get('DB_USER') 
    # DB_PASS = os.environ.get('DB_PASS')
    # DB_NAME = os.environ.get('DB_NAME_TEST')
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(DB_USER,DB_PASS,DB_HOST,DB_NAME) 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(BaseConfig):
    DEBUG =  False
    DEVELOPMENT= False
    DB_HOST = os.environ.get('DB_HOST') 
    DB_USER = os.environ.get('DB_USER') 
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(DB_USER,DB_PASS,DB_HOST,DB_NAME) 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
