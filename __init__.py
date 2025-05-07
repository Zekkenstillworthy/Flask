from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config=None):
    # Set the instance path explicitly to ensure using the correct database location
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    app = Flask(__name__, instance_path=instance_path)

    # Configure the app
    # Use local config file instead of user.config
    app.config.from_pyfile('config.py', silent=True)
    if config:
        app.config.update(config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specify the login view endpoint

    # Register blueprints
    try:
        from user.views import user_bp
        app.register_blueprint(user_bp)
        
        # Register the API blueprint with explicit url_prefix
        from user.api import api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api')
        
        # Print registered rules for debugging
        print("Registered URL rules:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
    except ImportError as e:
        # If a blueprint can't be imported, continue without it
        print(f"Warning: Could not import blueprint: {e}")

    return app