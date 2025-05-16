# Import and expose the API blueprint from the parent module
import sys
import os

# Add parent directory to path if needed
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the blueprint from the direct module
try:
    from user.api import api_blueprint
except ImportError:
    # Try direct import if package import fails
    try:
        import importlib.util
        api_path = os.path.join(parent_dir, 'api.py')
        spec = importlib.util.spec_from_file_location("api_module", api_path)
        api_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_module)
        api_blueprint = api_module.api_blueprint
    except Exception as e:
        print(f"Failed to import API blueprint: {e}")
        # Create a dummy blueprint to avoid errors
        from flask import Blueprint
        api_blueprint = Blueprint('api', __name__)