from . import db
from datetime import datetime

class Score(db.Model):
    """
    Score model for tracking user quiz scores
    """
    __tablename__ = 'score'
    __table_args__ = {'extend_existing': True}  # Allow table to be redefined
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    # Removed topic_id column as it doesn't exist in the actual database
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Score {self.score} by User {self.user_id} in {self.category}>'
