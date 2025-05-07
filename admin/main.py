import os
import sys
from admin.app import AdminApp

def main():
    """Main entry point for the admin application."""
    # Add the parent directory to sys.path to ensure imports work correctly
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    admin_app = AdminApp()
    app = admin_app.setup()
    admin_app.run()

if __name__ == "__main__":
    main()
