import json
from __init__ import db

class Question(db.Model):
    __tablename__ = 'question'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    numb = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    explanation = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), default="riddle")
    _options = db.Column(db.String(1000), nullable=False)
    question_type = db.Column(db.String(50), default="multiple_choice")
    
    @property
    def options(self):
        try:
            return json.loads(self._options)
        except:
            return []
        
    @options.setter
    def options(self, options_list):
        self._options = json.dumps(options_list)
        
    def __repr__(self):
        return f'<Question {self.id}: {self.question[:30]}...>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'numb': self.numb,
            'question': self.question,
            'answer': self.answer,
            'options': self.options,
            'explanation': self.explanation,
            'category': self.category,
            'question_type': self.question_type
        }


# This additional model handles the "questions" table (with plural name)
# that contains standard questions with options as a JSON array
class StandardQuestion(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    numb = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(250), nullable=False)
    explanation = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), default="riddle")
    _options = db.Column(db.String(1000), nullable=False)
    
    @property
    def options(self):
        try:
            return json.loads(self._options)
        except:
            return []
        
    @options.setter
    def options(self, options_list):
        self._options = json.dumps(options_list)
        
    def __repr__(self):
        return f'<StandardQuestion {self.id}: {self.question[:30]}...>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'numb': self.numb,
            'question': self.question,
            'answer': self.answer,
            'options': self.options,
            'explanation': self.explanation,
            'category': self.category
        }
