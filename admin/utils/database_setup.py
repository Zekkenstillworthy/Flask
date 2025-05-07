from admin import db
from admin.models.question import Question
from werkzeug.security import generate_password_hash
from admin.models.user import Admin
from admin.models.scenario import Scenario  # Make sure the Scenario model is imported
from admin.utils.questions_data import get_networking_questions
import sqlite3

def setup_database():
    """Set up the database with initial tables and data."""
    from admin import db
    from admin.models.user import User, Admin
    from admin.models.question import Question
    from admin.models.score import Score
    from admin.models.class_model import Class
    from admin.models.question_group import QuestionGroup
    from admin.models.essay_response import EssayResponse
    from admin.models.activity_log import ActivityLog
    from admin.models.scenario import Scenario
    from admin.models.topology import Topology
    from werkzeug.security import generate_password_hash
    
    print("Creating database tables...")
    
    # Create all database tables
    db.create_all()
    
    # Check for admin account and create if not exists
    admin_exists = Admin.query.filter_by(username="admin").first()
    if not admin_exists:
        print("Creating admin account...")
        admin = Admin(
            username="admin", 
            password_hash=generate_password_hash("admin"),  # Direct password hash instead of using set_password
            email="admin@riddlenet.com"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully!")
    
    print("Database setup complete!")

def ensure_scenarios_table_exists():
    """Ensure that the scenarios table exists with all required columns."""
    try:
        # Access the database connection directly
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        # Check if the scenarios table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating scenarios table directly with SQL...")
            # Create the scenarios table directly with SQL if it doesn't exist
            cursor.execute('''
            CREATE TABLE scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            connection.commit()
            print("Scenarios table created successfully")
        else:
            # Check if the table has all required columns
            cursor.execute("PRAGMA table_info(scenarios)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'title' not in column_names or 'description' not in column_names:
                print("Scenarios table exists but is missing required columns. Recreating...")
                cursor.execute("DROP TABLE scenarios")
                cursor.execute('''
                CREATE TABLE scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                connection.commit()
                print("Scenarios table recreated with all required columns")
            else:
                print("Scenarios table exists and has all required columns")
                
        connection.close()
    except Exception as e:
        print(f"Error ensuring scenarios table exists: {e}")

def import_default_questions():
    """Import default questions if the database is empty."""
    if Question.query.count() == 0:
        try:
            # Get default questions from questions_data.py
            default_questions = get_networking_questions()
            
            for q_data in default_questions:
                question = Question(
                    numb=q_data["numb"],
                    question=q_data["question"],
                    answer=q_data["answer"],
                    options=q_data["options"],
                    explanation=q_data.get("explanation", ""),
                    category="riddle"
                )
                db.session.add(question)
                
            db.session.commit()
            print("Imported default questions from questions_data.py")
        except Exception as e:
            db.session.rollback()
            print(f"Error importing default questions: {e}")

def create_default_admin():
    """Create a default admin user if no admin exists."""
    if Admin.query.count() == 0:
        default_admin = Admin(
            username="admin",
            password_hash=generate_password_hash("admin"),
            email="admin@example.com",
            role="admin"
        )
        try:
            db.session.add(default_admin)
            db.session.commit()
            print("Created default admin user. Username: 'admin', Password: 'admin'")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating default admin: {e}")
