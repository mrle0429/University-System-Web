from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 初始化数据库
    db.init_app(app)

    # 延迟导入路由和模型，避免循环导入
    from .routes import main_routes
    from .models import User

    # 注册蓝图
    app.register_blueprint(main_routes)

    return app
