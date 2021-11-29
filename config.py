import os
import pymysql

basedir = os.path.abspath(os.path.dirname(__file__))

class DevConfig(object):
    DEBUG = True
    DEVELOPMENT= True
    JSON_SORT_KEYS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(object):
    DEBUG =  False
    DEVELOPMENT= False
    JSON_SORT_KEYS = False
    DB_HOST = os.environ.get('DB_HOST') 
    DB_USER = os.environ.get('DB_USER') 
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(DB_USER,DB_PASS,DB_HOST,DB_NAME) 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
