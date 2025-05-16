# Import the db instance from the main application
from __init__ import db

# Import models to make them available when importing from the package
from .user import User
# Import admin models to avoid duplication
from admin.models.question import Question
from admin.models.essay_response import EssayResponse
from .score import Score

# Import association tables last to avoid circular imports
from .association_tables import class_students