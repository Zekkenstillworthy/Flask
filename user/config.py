from pytz import timezone
import os

class Config:
    """Application configuration settings"""
    # Use absolute path to the root instance database
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(ROOT_DIR, "instance", "test.db")}'
    SECRET_KEY = 'your_secret_key'
    PH_TZ = timezone('Asia/Manila')
    UPLOAD_FOLDER = os.path.join('static', 'img')
