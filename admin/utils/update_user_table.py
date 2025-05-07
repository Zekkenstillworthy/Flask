from admin import db
from admin.models.user import User
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

def migrate_user_table():
    """
    Update the User table to add missing fields:
    - email
    - status
    - created_at
    - last_active
    """
    print("Starting User table migration...")
    
    # Check if columns already exist to avoid errors
    connection = db.engine.connect()
    inspector = sa.inspect(db.engine)
    existing_columns = [column['name'] for column in inspector.get_columns('user')]
    
    # Add columns one by one if they don't exist
    if 'email' not in existing_columns:
        try:
            connection.execute(sa.text('ALTER TABLE user ADD COLUMN email VARCHAR(150)'))
            print(f"Added column 'email' to the User table")
        except OperationalError as e:
            print(f"Error adding column 'email': {e}")
    
    if 'status' not in existing_columns:
        try:
            connection.execute(sa.text('ALTER TABLE user ADD COLUMN status VARCHAR(20)'))
            print(f"Added column 'status' to the User table")
        except OperationalError as e:
            print(f"Error adding column 'status': {e}")
    
    if 'created_at' not in existing_columns:
        try:
            connection.execute(sa.text('ALTER TABLE user ADD COLUMN created_at TIMESTAMP'))
            print(f"Added column 'created_at' to the User table")
        except OperationalError as e:
            print(f"Error adding column 'created_at': {e}")
    
    if 'last_active' not in existing_columns:
        try:
            connection.execute(sa.text('ALTER TABLE user ADD COLUMN last_active TIMESTAMP'))
            print(f"Added column 'last_active' to the User table")
        except OperationalError as e:
            print(f"Error adding column 'last_active': {e}")
    
    # Update existing rows with default values
    try:
        # Set default status for users that don't have one yet
        connection.execute(sa.text("UPDATE user SET status = 'active' WHERE status IS NULL"))
        print("Updated users with default 'active' status")
        
        # Set default created_at for users that don't have one yet
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        connection.execute(sa.text(f"UPDATE user SET created_at = '{now}' WHERE created_at IS NULL"))
        print("Updated users with default creation date")
        
        db.session.commit()
        print("Updated existing users with default values")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating existing users: {e}")
    
    print("User table migration completed.")


if __name__ == "__main__":
    migrate_user_table()