from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from admin.models.class_model import Class
from admin.models.question_group import QuestionGroup
from admin import db
from datetime import datetime
import json
import random
import string

# Create a blueprint for class related routes
class_controller = Blueprint('class_controller', __name__)

@class_controller.route('/classes')
@login_required
def index():
    """Display the class management page"""
    # Add debug print to verify authentication status
    print(f"User authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    
    return render_template('admin/class.html', active_page='classes')

@class_controller.route('/api/question-groups', methods=['GET'])
@login_required
def get_question_groups():
    """API endpoint to retrieve all question groups"""
    try:
        # Get all question groups from database
        groups = QuestionGroup.query.all()
        return jsonify([{
            'id': group.id,
            'name': group.name,
            'questionCount': len(group.questions)
        } for group in groups])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """API endpoint to retrieve all classes"""
    try:
        # Get all classes from database
        classes = Class.query.all()
        
        # Convert classes to dictionary format for JSON response
        result = []
        for cls in classes:
            # Count students (to be implemented with actual student relationship)
            student_count = 0  # Replace with actual query when student model is available
            
            result.append({
                'id': cls.id,
                'name': cls.name,
                'section': cls.section,
                'code': cls.code,
                'students': student_count,
                'maxStudents': cls.max_students,
                'startDate': cls.start_date.isoformat() if cls.start_date else None,
                'endDate': cls.end_date.isoformat() if cls.end_date else None,
                'status': cls.status
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes', methods=['POST'])
@login_required
def create_class():
    """API endpoint to create a new class"""
    try:
        data = request.json
        
        # Check if code already exists
        existing_class = Class.query.filter_by(code=data.get('code')).first()
        if existing_class:
            return jsonify({
                "error": f"Class code '{data.get('code')}' already exists. Please use a different code."
            }), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(data.get('startDate')) if data.get('startDate') else None
        end_date = datetime.fromisoformat(data.get('endDate')) if data.get('endDate') else None
        
        # Create new class
        new_class = Class(
            name=data.get('name'),
            section=data.get('section'),
            code=data.get('code'),
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            max_students=data.get('maxStudents'),
            status=data.get('status', 'active')
        )
        
        # Add question groups if provided
        if 'questionGroups' in data and data['questionGroups']:
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            new_class.question_groups = question_groups
        
        # Save to database
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Class created successfully!",
            "classId": new_class.id
        }), 201
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        if "UNIQUE constraint failed: classes.code" in error_msg:
            error_msg = f"Class code '{data.get('code')}' already exists. Please use a different code."
        return jsonify({"error": error_msg}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['GET'])
@login_required
def get_class(class_id):
    """API endpoint to retrieve a specific class details"""
    try:
        cls = Class.query.get_or_404(class_id)
        return jsonify(cls.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['PUT'])
@login_required
def update_class(class_id):
    """API endpoint to update a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        data = request.json
        
        # Check if code is being changed and verify it's unique
        if 'code' in data and data['code'] != cls.code:
            existing_class = Class.query.filter_by(code=data['code']).first()
            if existing_class and existing_class.id != class_id:
                return jsonify({
                    "error": f"Class code '{data['code']}' already exists. Please use a different code."
                }), 400
        
        # Update fields if provided
        if 'name' in data:
            cls.name = data['name']
        if 'section' in data:
            cls.section = data['section']
        if 'code' in data:
            cls.code = data['code']
        if 'description' in data:
            cls.description = data['description']
        if 'startDate' in data:
            cls.start_date = datetime.fromisoformat(data['startDate'])
        if 'endDate' in data:
            cls.end_date = datetime.fromisoformat(data['endDate'])
        if 'maxStudents' in data:
            cls.max_students = data['maxStudents']
        if 'status' in data:
            cls.status = data['status']
            
        # Update question groups if provided
        if 'questionGroups' in data:
            question_groups = QuestionGroup.query.filter(
                QuestionGroup.id.in_(data['questionGroups'])
            ).all()
            cls.question_groups = question_groups
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Class updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/classes/<int:class_id>', methods=['DELETE'])
@login_required
def delete_class(class_id):
    """API endpoint to delete a class"""
    try:
        cls = Class.query.get_or_404(class_id)
        db.session.delete(cls)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Class deleted successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@class_controller.route('/api/generate-class-code', methods=['GET'])
@login_required
def generate_class_code():
    """API endpoint to generate a unique class code"""
    try:
        # Generate a random 6-character code (letters and numbers)
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Removed confusing characters like 0, O, 1, I
        
        # Keep generating until we find a unique code
        while True:
            code = ''.join(random.choice(chars) for _ in range(6))
            
            # Check if code already exists in database
            existing = Class.query.filter_by(code=code).first()
            if not existing:
                break
                
        return jsonify({"code": code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500