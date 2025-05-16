from __init__ import create_app, db
import os
from user.quiz import QuizController
from admin.controllers.question_controller import QuestionController

# Create the Flask application
app = create_app()

# Create an application context for use outside of request handling
ctx = app.app_context()
ctx.push()

# Ensure the instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Initialize the QuizController with our Flask app to register all quiz routes
quiz_controller = QuizController(app)

# Now register the API blueprint AFTER the QuizController to avoid conflicts
# Any conflicts will result in the QuizController routes taking precedence
try:
    # Import directly from the file, not the package
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Direct import from the api.py file
    from user.api import api_blueprint as user_api_blueprint
    app.register_blueprint(user_api_blueprint, url_prefix='/api')
    print("API Blueprint registered successfully")
except Exception as e:
    print(f"Error registering API blueprint: {e}")
    # If we can't import from the package, try to import from the file directly
    try:
        import importlib.util
        api_path = os.path.join(os.path.dirname(__file__), 'user', 'api.py')
        spec = importlib.util.spec_from_file_location("api_module", api_path)
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        app.register_blueprint(api_module.api_blueprint, url_prefix='/api')
        print("API Blueprint registered successfully using direct file import")
    except Exception as e2:
        print(f"Second attempt also failed: {e2}")

# Print all registered routes for debugging
print("\n=== Registered Routes ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    methods = ', '.join(sorted(rule.methods)) if rule.methods else ''
    print(f"{rule.endpoint:30} {methods:20} {rule.rule}")
print("=========================\n")

if __name__ == "__main__":
    # Run the app with debug mode enabled
    app.run(debug=True)

