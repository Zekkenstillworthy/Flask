"""
THIS FILE IS DEPRECATED AND SHOULD NOT BE USED

The Question model is now imported from admin.models.question to avoid
duplicate table definitions. This file is kept for reference only.

To use the Question model, import it from admin.models.question:
    from admin.models.question import Question
"""

# Original code is commented out to prevent it from being loaded
"""
from .import db
import json

class Question(db.Model):
    __tablename__ = 'question'
    __table_args__ = {'extend_existing': True} 
    
    id = db.Column(db.Integer, primary_key=True)
    numb = db.Column(db.Integer, nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    explanation = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), default="riddle")
    question_type = db.Column(db.String(50), default="multiple_choice")
    
    _options = db.Column(db.String(1000), nullable=False)
    
    @property
    def options(self):
        try:
            return json.loads(self._options)
        except:
            return []
    
    @options.setter
    def options(self, value):
        self._options = json.dumps(value)
"""

# Re-export the Question model from admin to maintain backward compatibility
from admin.models.question import Question
def options(self):
        try:
            return json.loads(self._options)
        except:
            return []
        
@options.setter
def options(self, options_list):
        self._options = json.dumps(options_list)
        
def get_question_type(self):
        """Determine the question type based on the explanation field"""
        if self.explanation:
            if '[TYPE:fill_blank]' in self.explanation:
                return 'fill_blank'
            elif '[TYPE:short_answer]' in self.explanation:
                return 'short_answer'
            elif '[TYPE:matching]' in self.explanation:
                return 'matching'
        return 'multiple_choice'
