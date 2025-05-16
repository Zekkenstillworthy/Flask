from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class AdminUser(db.Model, UserMixin):
    """
    Admin User model
    """
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}  # Allow table to be redefined
    
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    totp_key = Column(String(32), nullable=True)
    profile_img = Column(String(150), nullable=True)
    is_admin = Column(Boolean, default=False)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    
    # Define the scores relationship from the User side
    # Use a method to query scores to avoid circular imports
    def get_scores(self):
        """Get scores for this user"""
        from admin.models.score import AdminScore
        return AdminScore.query.filter_by(user_id=self.id).all()
    
    # Note: The enrolled_classes relationship is defined in the Class model via backref
    # We don't need to define it explicitly here
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'status': self.status,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else None
        }

# Define the Admin model to match your 'admin' table
class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }
