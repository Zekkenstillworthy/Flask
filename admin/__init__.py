from flask import Flask
from flask_login import LoginManager
import os
import sys

# Add parent directory to path so we can import from main app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import db from main app to use a single SQLAlchemy instance
from __init__ import db, login_manager

# Import controllers after creating db to avoid circular imports
def create_app(config=None):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure app
    if config:
        app.config.from_object(config)
    else:
        # Default configuration
        app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
        # Use the test.db in instance folder
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(ROOT_DIR, "instance", "test.db")}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from admin.models.user import AdminUser
        return AdminUser.query.get(int(user_id))
    
    # Register blueprints
    with app.app_context():
        from admin.controllers.auth_controller import auth_bp
        from admin.controllers.dashboard_controller import dashboard_bp
        from admin.controllers.user_controller import user_bp
        from admin.controllers.question_controller import question_bp
        from admin.controllers.score_controller import score_bp
        from admin.controllers.essay_controller import essay_bp
        from admin.controllers.scenario_controller import scenario_bp
        from admin.routes.scenario_routes import scenario_routes
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(question_bp)
        app.register_blueprint(score_bp)
        app.register_blueprint(essay_bp)
        app.register_blueprint(scenario_bp)
        app.register_blueprint(scenario_routes)
        
        # Create database tables
        db.create_all()
        
    return app

