from flask import Flask
from .models import db
from .config import Config
from .quiz import QuizController
# Import the Blueprint instead of ViewController
from .views import user_bp
from .api import api_blueprint  # Import the API blueprint
from .utils import DataUtility
import os
from datetime import timedelta
from admin.models.topology import Topology  # Import the Topology model

class Application:
    def __init__(self):
        # Get the root directory path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        instance_path = os.path.join(root_dir, 'instance')
        
        # Create the instance directory if it doesn't exist
        os.makedirs(instance_path, exist_ok=True)
        
        # Initialize Flask with explicit instance path
        self.app = Flask(__name__, 
                        template_folder='../templates', 
                        static_folder='../static',
                        instance_path=instance_path)
        
        # Configure the app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
        self.app.config['SECRET_KEY'] = Config.SECRET_KEY
        self.app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
        
        # Configure session settings
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = True
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
        self.app.config['SESSION_USE_SIGNER'] = True
        self.app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        # Initialize database
        db.init_app(self.app)
        
        # Register controllers and blueprints
        with self.app.app_context():
            self._init_database()
            self._register_controllers()
    
    def _init_database(self):
        """Initialize the database and import default data"""
        # Only create tables if database doesn't exist
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'instance', 'test.db')
        
        if not os.path.exists(db_path):
            print(f"Creating database at {db_path}")
            db.create_all()
            DataUtility.import_default_questions()
        else:
            print(f"Using existing database at {db_path}")
    
    def _register_controllers(self):
        """Register all controllers with the application"""
        self.quiz_controller = QuizController(self.app)
        # Register the user_bp blueprint instead of initializing ViewController
        self.app.register_blueprint(user_bp)
        # Register the API blueprint
        self.app.register_blueprint(api_blueprint, url_prefix='/api')
    
    def run(self, debug=True):
        """Run the Flask application"""
        self.app.run(debug=debug)

# For direct execution of this file
if __name__ == "__main__":
    app = Application()
    app.run(debug=True)
