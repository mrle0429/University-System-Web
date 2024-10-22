import os


class Config:
    SECRET_KEY = 'secretary'
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Update this line to use MySQL with remote credentials
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:OOD20241022@39.105.0.202/webapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

