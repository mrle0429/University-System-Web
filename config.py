import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 从环境变量获取配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    def __init__(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("No DATABASE_URL set in environment variables")

