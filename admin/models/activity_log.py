from datetime import datetime
from admin import db

class ActivityLog(db.Model):
    """
    Model for tracking admin activities in the system
    """
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Changed from 'users.id' to 'user.id'
    action_type = db.Column(db.String(50), nullable=False)  # e.g., 'review', 'delete', 'grade'
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    related_entity_type = db.Column(db.String(50), nullable=True)  # e.g., 'essay', 'question'
    related_entity_id = db.Column(db.Integer, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('activity_logs', lazy=True))
    
    @classmethod
    def log_activity(cls, user_id, action_type, message, related_entity_type=None, related_entity_id=None):
        """
        Create and save a new activity log entry
        
        Args:
            user_id: The ID of the user performing the action
            action_type: Type of action (review, delete, etc.)
            message: Description of the activity
            related_entity_type: Type of entity being acted upon (essay, question, etc.)
            related_entity_id: ID of the entity being acted upon
        """
        log = cls(
            user_id=user_id,
            action_type=action_type,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        db.session.add(log)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging activity: {e}")
    
    def __repr__(self):
        return f"<ActivityLog {self.id}: {self.action_type} by User {self.user_id}>"