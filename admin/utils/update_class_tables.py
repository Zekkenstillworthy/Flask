from admin import db
from admin.models.class_model import Class, class_question_groups, class_students
from sqlalchemy.engine import reflection
from sqlalchemy import Table, MetaData, inspect, text

def update_database_schema():
    """Update database schema to include class tables"""
    try:
        # Get a list of existing tables
        insp = reflection.Inspector.from_engine(db.engine)
        existing_tables = insp.get_table_names()
        
        # Create tables if they don't exist
        if 'classes' not in existing_tables:
            print("Creating 'classes' table...")
            Class.__table__.create(db.engine)
        
        # Check if association tables exist
        metadata = MetaData()
        metadata.reflect(bind=db.engine)
        
        if 'class_question_groups' not in existing_tables:
            print("Creating 'class_question_groups' association table...")
            Table('class_question_groups', metadata,
                  autoload_with=db.engine,
                  extend_existing=True).create(db.engine)
        
        if 'class_students' not in existing_tables:
            print("Creating 'class_students' association table...")
            Table('class_students', metadata,
                  autoload_with=db.engine,
                  extend_existing=True).create(db.engine)
        
        print("Database schema successfully updated for class management!")
        return True
    except Exception as e:
        print(f"Error updating database schema: {e}")
        return False

def update_classes_table():
    """
    Script to update the classes table with the required columns
    """
    try:
        # Get the inspector for the current database
        inspector = inspect(db.engine)
        
        # Check if the classes table exists
        if 'classes' not in inspector.get_table_names():
            print("Table 'classes' does not exist. Creating the table...")
            # Create the table from the model
            db.create_all()
            print("Table 'classes' created successfully.")
            return "Table created successfully"
        
        # Get the columns in the classes table
        columns = [column['name'] for column in inspector.get_columns('classes')]
        
        # Check if required columns are missing
        required_columns = {
            'code': 'VARCHAR(20) UNIQUE NOT NULL',
            'name': 'VARCHAR(100) NOT NULL',
            'section': 'VARCHAR(50)',
            'description': 'TEXT',
            'start_date': 'DATE NOT NULL',
            'end_date': 'DATE NOT NULL',
            'max_students': 'INTEGER',
            'status': 'VARCHAR(20)',
            'created_at': 'DATETIME'
        }
        
        with db.engine.connect() as conn:
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    print(f"Column '{col_name}' is missing. Adding it now...")
                    conn.execute(text(f"ALTER TABLE classes ADD COLUMN {col_name} {col_type}"))
                    print(f"Column '{col_name}' added successfully.")
        
        print("Classes table updated successfully!")
        return "Classes table updated successfully!"
    except Exception as e:
        print(f"Error updating classes table: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # This allows running this script directly
    from admin.app import AdminApp
    app = AdminApp().setup()
    with app.app_context():
        update_database_schema()
        update_classes_table()