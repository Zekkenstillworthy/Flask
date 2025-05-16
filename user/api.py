from flask import Blueprint, jsonify, request, session
from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from admin.controllers.question_controller import QuestionController
from admin.controllers.question_group_controller import QuestionGroupController
from admin.models.topology import Topology
from admin.models.score import AdminScore  # Updated to use the renamed model directly
from admin.models.class_model import Class
from user.models import db, User as UserModel  # Rename to avoid conflicts
from user.models import Score as UserScore  # Use a clear name for the user's Score model
from user.models.association_tables import class_students
import json
from datetime import datetime

api_blueprint = Blueprint('api', __name__)
question_controller = QuestionController()
question_group_controller = QuestionGroupController()

@api_blueprint.route('/save_essay', methods=['POST'])
def save_essay():
    """Save an essay response for the current user"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "User not logged in."}), 403
    
    data = request.get_json()
    question_text = data.get('question')
    question_id = data.get('questionId')
    response_text = data.get('answer')
    category = data.get('category', 'riddle')
    
    if not response_text or not question_text:
        return jsonify({"status": "error", "message": "Missing question or response"}), 400
    
    try:
        from admin.models.essay_response import EssayResponse
        
        new_response = EssayResponse(
            user_id=session['user_id'],
            question_id=question_id,
            question_text=question_text,
            response_text=response_text,
            category=category
        )
        db.session.add(new_response)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Essay submitted for review"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error saving essay: {str(e)}")
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

@api_blueprint.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions, with optional category filter"""
    try:
        category = request.args.get('category')
        if category:
            questions = question_controller.get_questions_by_category(category)
        else:   
            questions = question_controller.get_all_questions()
        
        # Convert to JSON-serializable format
        result = []
        for question in questions:
            question_data = {
                'id': question.id,
                'numb': question.numb,
                'question': question.question,
                'answer': question.answer,
                'options': question.options,
                'explanation': question.explanation,
                'category': question.category
            }
            result.append(question_data)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error in get_questions: {str(e)}")
        traceback.print_exc()
        return jsonify([]), 500