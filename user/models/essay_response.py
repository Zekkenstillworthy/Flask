"""
THIS FILE IS DEPRECATED AND SHOULD NOT BE USED

The EssayResponse model is now imported from admin.models.essay_response to avoid
duplicate table definitions. This file is kept for reference only.

To use the EssayResponse model, import it from admin.models.essay_response:
    from admin.models.essay_response import EssayResponse
"""

# Original code is commented out to prevent it from being loaded
"""
from . import db
from datetime import datetime
from .user import User  # Import from the same package

class EssayResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    graded_score = db.Column(db.Integer, nullable=True)
    is_graded = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, default=lambda: datetime.now())
    category = db.Column(db.String(50), default='riddle')

    user = db.relationship(
        User,
        backref=db.backref('essay_responses', lazy=True),
        foreign_keys=[user_id],
        primaryjoin="EssayResponse.user_id == User.id"
    )
"""

# Re-export the EssayResponse model from admin to maintain backward compatibility
from admin.models.essay_response import EssayResponse
    
