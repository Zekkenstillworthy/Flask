from __init__ import db
from sqlalchemy.orm import relationship
from datetime import datetime

# Association table for the many-to-many relationship between groups and questions
question_group_items = db.Table('question_group_items',
    db.Column('group_id', db.Integer, db.ForeignKey('question_groups.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class QuestionGroup(db.Model):
    __table_args__ = {'extend_existing': True}
    """Model for question groups which organize questions into categories"""
    __tablename__ = 'question_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship with questions
    questions = relationship("Question", secondary=question_group_items, backref="groups")
    
    # NOTE: The relationship with classes is defined in the Class model via backref
    # classes = relationship("Class", secondary="class_question_groups", back_populates="question_groups")
    
    def __repr__(self):
        return f'<QuestionGroup {self.id}: {self.name}>'
        
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'question_count': len(self.questions),
            'class_count': len(self.classes) if hasattr(self, 'classes') else 0
        }
