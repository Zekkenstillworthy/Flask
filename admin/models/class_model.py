from __init__ import db
from datetime import datetime

# Association table for many-to-many relationship between classes and question groups
class_question_groups = db.Table('class_question_groups',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_group_id', db.Integer, db.ForeignKey('question_groups.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

# Association table for many-to-many relationship between classes and students (users)
class_students = db.Table('class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('joined_date', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='active'),  # active, inactive, pending
    extend_existing=True
)

class Class(db.Model):
    """Class model for managing student classes"""
    __tablename__ = 'classes'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50))
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_students = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question_groups = db.relationship('QuestionGroup', 
                                      secondary=class_question_groups, 
                                      lazy='subquery',
                                      backref=db.backref('classes', lazy=True))
    
    # Use a property to get students instead of a relationship
    @property
    def students(self):
        """Get students enrolled in this class using a direct query"""
        from sqlalchemy import text
        from user.models.user import User
        
        # Direct SQL query using the association table
        result = db.session.query(User).join(
            text('class_students ON user.id = class_students.user_id')
        ).filter(
            text('class_students.class_id = :class_id')
        ).params(class_id=self.id)
        
        return result
    
    def __repr__(self):
        return f"<Class {self.name} ({self.code})>"
    
    def to_dict(self):
        """Convert class object to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'code': self.code,
            'description': self.description,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'maxStudents': self.max_students,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'questionGroups': [qg.id for qg in self.question_groups] if self.question_groups else [],
            'studentCount': len(self.students) if self.students else 0
        }
        
    def to_dict_with_question_groups(self):
        """Convert class object to dictionary with detailed question groups data"""
        data = self.to_dict()
        
        # Add detailed question group data
        question_groups_data = []
        for qg in self.question_groups:
            question_types = set()
            question_count = 0
            
            # Extract question types if the relationship exists
            if hasattr(qg, 'questions'):
                question_count = len(qg.questions)
                for q in qg.questions:
                    if hasattr(q, 'type'):
                        question_types.add(q.type)
                    elif hasattr(q, 'category'):
                        question_types.add(q.category)
            
            question_groups_data.append({
                'id': qg.id,
                'name': qg.name,
                'description': qg.description if hasattr(qg, 'description') else '',
                'questionCount': question_count,
                'questionTypes': list(question_types)
            })
        
        data['questionGroups'] = question_groups_data
        return data