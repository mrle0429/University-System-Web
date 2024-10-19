import os

class Config:
    SECRET_KEY = 'secretary'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance/app.db')
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
