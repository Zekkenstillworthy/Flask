from pytz import timezone
import os

# Application configuration settings
# Use absolute path to ensure the correct database is used
INSTANCE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_PATH, "test.db")}'
SECRET_KEY = 'your_secret_key'
PH_TZ = timezone('Asia/Manila')
UPLOAD_FOLDER = os.path.join('static', 'img')