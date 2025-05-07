from datetime import datetime
from admin import db

class Score(db.Model):
    __tablename__ = 'score'
    
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)  # Changed to float based on your data
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=True, default='riddle')

    user = db.relationship('User', backref='scores')
    
    def __repr__(self):
        return f'<Score {self.id}: {self.score}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'score': self.score,
            'date_attempted': self.date_attempted.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
            'category': self.category
        }
