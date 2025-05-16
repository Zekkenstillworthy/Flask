from datetime import datetime
from __init__ import db
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

class AdminScore(db.Model):
    """
    Score model for the admin section
    """
    __tablename__ = 'score'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)  # Changed to float based on your data
    date_attempted = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category = Column(String(50), nullable=True, default='riddle')
    
    # Define user relationship explicitly with a string
    # We'll use a query-time join instead of a persistent relationship
    def get_user(self):
        """Get the user associated with this score"""
        from admin.models.user import AdminUser
        return AdminUser.query.get(self.user_id)
    
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
