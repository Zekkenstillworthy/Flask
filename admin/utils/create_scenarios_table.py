"""
Script to create the scenarios table in the database.
"""
from admin import db
from admin.models.scenario import Scenario
from admin.app import AdminApp
import os

def create_scenarios_table():
    """Create the scenarios table if it doesn't exist"""
    try:
        # Create the scenarios table
        print("Creating scenarios table...")
        Scenario.__table__.create(db.engine, checkfirst=True)
        print("Scenarios table created successfully!")
    except Exception as e:
        print(f"Error creating scenarios table: {e}")
        
if __name__ == "__main__":
    # Create the Flask application instance
    admin_app = AdminApp()
    app = admin_app.app
    
    # Set the correct database URI pointing to the instance folder
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "test.db")}'
    
    # Initialize the app
    admin_app.init_db()
    
    # Create application context
    with app.app_context():
        # Create the scenarios table
        create_scenarios_table()