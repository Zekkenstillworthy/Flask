# This file is a proxy for importing models from the proper location
# All model definitions have been moved to the user/models/ directory or are imported from admin

# Re-export models from the models package
from user.models.user import User
from user.models.score import Score

# Import models from admin package to avoid duplication
from admin.models.question import Question
from admin.models.essay_response import EssayResponse
from user.models.association_tables import class_students

# Import the Class model for proper referencing
from admin.models.class_model import Class

# Re-export the db instance for convenience
from __init__ import db