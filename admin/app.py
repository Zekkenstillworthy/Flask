from flask import Flask, redirect, url_for
import os
from admin import db, login_manager

class AdminApp:
    def __init__(self):
        # Specify the template folder as an absolute path pointing to the project's templates directory
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        
        self.configure_app()
        self.init_db()
        self.init_login_manager()
        self.register_template_filters()

    def configure_app(self):
        """Configure the Flask application."""
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['SECRET_KEY'] = 'your_secret_key'
        self.app.config['ADMIN_PORT'] = 5001

        # Debug template path
        template_dir = self.app.template_folder
        print(f"Looking for templates in: {template_dir}")

    def init_db(self):
        """Initialize the database with the app."""
        db.init_app(self.app)
        
    def init_login_manager(self):
        """Initialize the Flask-Login manager with the app."""
        login_manager.init_app(self.app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message_category = 'info'
        
        @login_manager.user_loader
        def load_user(user_id):
            # Try to load from Admin model first (since admin login is being used)
            from admin.models.user import Admin, User
            
            # Check if the ID starts with 'admin-' which would indicate it's an admin
            if isinstance(user_id, str) and user_id.startswith('admin-'):
                admin_id = int(user_id.replace('admin-', ''))
                return Admin.query.get(admin_id)
            
            # Try Admin table first
            admin = Admin.query.get(int(user_id))
            if admin:
                return admin
                
            # If not found in Admin, try User table
            user = User.query.get(int(user_id))
            return user

    def register_template_filters(self):
        """Register custom template filters."""
        @self.app.template_filter('from_json')
        def from_json_filter(value):
            import json
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return []

    def register_blueprints(self):
        """Register all blueprints with the application."""
        # Use absolute imports instead of relative imports
        from admin.controllers.auth_controller import auth_bp
        from admin.controllers.user_controller import user_bp
        from admin.controllers.question_controller import question_bp
        from admin.controllers.score_controller import score_bp
        from admin.controllers.essay_controller import essay_bp
        from admin.controllers.dashboard_controller import dashboard_bp
        from admin.controllers.question_group_controller import question_group_bp
        from admin.controllers.class_controller import class_controller
        from admin.controllers.scenario_controller import scenario_bp
        from admin.routes.topology_routes import topology_bp
        
        # Register only available blueprints
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(user_bp)
        self.app.register_blueprint(question_bp)
        self.app.register_blueprint(score_bp)
        self.app.register_blueprint(essay_bp)
        self.app.register_blueprint(dashboard_bp)
        self.app.register_blueprint(question_group_bp)
        self.app.register_blueprint(class_controller)
        self.app.register_blueprint(scenario_bp)
        self.app.register_blueprint(topology_bp, url_prefix='/admin/topology')
        
        # Add root route to redirect to admin dashboard
        @self.app.route('/')
        def index():
            return redirect(url_for('dashboard.index'))

    def setup(self):
        """Setup the application by registering blueprints and initializing database."""
        self.register_blueprints()
        
        with self.app.app_context():
            # Use absolute import for database_setup
            from admin.utils.database_setup import setup_database
            setup_database()
        
        return self.app

    def run(self):
        """Run the Flask application."""
        port = self.app.config['ADMIN_PORT']
        print(f"Admin app running on port {port}")
        self.app.run(debug=True, port=port)
