from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from admin.models.topology import Topology
import json

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    User model for the quiz application
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_img = db.Column(db.String(128))
    totp_key = db.Column(db.String(32))
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)
    totp_secret = db.Column(db.String(32))
    totp_enabled = db.Column(db.Boolean, default=False)
    
    # Define relationship with scores
    scores = db.relationship('Score', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Score(db.Model):
    """
    Score model for tracking user quiz scores
    """
    __tablename__ = 'score'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    # Removed topic_id column as it doesn't exist in the actual database
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Score {self.score} by User {self.user_id} in {self.category}>'

class Question(db.Model):
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
        return json.loads(self._options)
        
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
        
        # Default types based on options
        if len(self.options) == 2 and ('True' in self.options[0] or 'False' in self.options[0]):
            return 'true_false'
        
        return 'multiple_choice'

class EssayResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    graded_score = db.Column(db.Integer, nullable=True)
    is_graded = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, default=lambda: datetime.now())
    category = db.Column(db.String(50), default='riddle')

    user = db.relationship('User', backref=db.backref('essay_responses', lazy=True))
