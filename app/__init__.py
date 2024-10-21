from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Load configurations
    db.init_app(app)  # Initialize the database
    login_manager.init_app(app)  # Initialize login manager

    # Import and register blueprints (deferred import to avoid circular import issues)
    from .routes import main_routes
    app.register_blueprint(main_routes)

    with app.app_context():
        db.create_all()  # Create database tables

    return app
