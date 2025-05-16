"""
Association tables for many-to-many relationships in the user model
This module defines association tables that can be imported anywhere
without causing import cycles
"""
from . import db
from datetime import datetime

# We're importing the existing definition from admin.models.class_model
# to avoid duplicate definitions of the association table
"""
# This table is now defined in admin.models.class_model
class_students = db.Table(
    'class_students',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('joined_date', db.DateTime, default=datetime.utcnow),
    db.Column('status', db.String(20), default='active'),  # active, inactive, pending
    extend_existing=True
)
"""
# Instead, reference the existing table
from admin.models.class_model import class_students
