from datetime import datetime
import json
from __init__ import db

class Topology(db.Model):
    """
    Model for network topology challenges
    """
    __tablename__ = 'topologies'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='medium')  # 'easy', 'medium', 'hard'
    topology_type = db.Column(db.String(50), default='point-to-point')  # 'point-to-point', 'mesh', 'star', etc.
    _initial_config = db.Column('initial_config', db.Text, nullable=True)  # JSON string
    _expected_config = db.Column('expected_config', db.Text, nullable=False)  # JSON string
    base_score = db.Column(db.Integer, default=10)  # Base points for completing
    time_bonus = db.Column(db.Integer, default=0)  # Additional points for completing quickly
    perfect_match_bonus = db.Column(db.Integer, default=5)  # Bonus for exact match with expected solution
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def initial_config(self):
        """Get the initial configuration as a Python object"""
        if not self._initial_config:
            return {"devices": [], "connections": []}
        return json.loads(self._initial_config)
        
    @initial_config.setter
    def initial_config(self, config):
        """Set the initial configuration from a Python object"""
        if isinstance(config, dict):
            self._initial_config = json.dumps(config)
        else:
            self._initial_config = config
            
    @property
    def expected_config(self):
        """Get the expected configuration as a Python object"""
        return json.loads(self._expected_config)
        
    @expected_config.setter
    def expected_config(self, config):
        """Set the expected configuration from a Python object"""
        if isinstance(config, dict):
            self._expected_config = json.dumps(config)
        else:
            self._expected_config = config
            
    def get_initial_config(self):
        """Get the initial configuration as a Python object"""
        return self.initial_config
        
    def get_expected_config(self):
        """Get the expected configuration as a Python object"""
        return self.expected_config
        
    def to_dict(self):
        """Convert the model to a dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'topology_type': self.topology_type,
            'initial_config': self.initial_config,
            'expected_config': self.expected_config,
            'base_score': self.base_score,
            'time_bonus': self.time_bonus,
            'perfect_match_bonus': self.perfect_match_bonus,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }