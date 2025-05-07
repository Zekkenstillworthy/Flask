from admin import db
from datetime import datetime

# Association table for many-to-many relationship between classes and question groups
class_question_groups = db.Table('class_question_groups',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('question_group_id', db.Integer, db.ForeignKey('question_groups.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for many-to-many relationship between classes and students (users)
class_students = db.Table('class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
)

class Class(db.Model):
    """Class model for managing student classes"""
    __tablename__ = 'classes'
    
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
    
    # Relationship with students (users)
    students = db.relationship('User',
                               secondary=class_students,
                               lazy='subquery',
                               backref=db.backref('enrolled_classes', lazy=True))
    
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