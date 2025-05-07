from flask import Blueprint, jsonify, request, session
from admin.models.question import Question
from admin.models.question_group import QuestionGroup
from admin.controllers.question_controller import QuestionController
from admin.controllers.question_group_controller import QuestionGroupController
from admin.models.topology import Topology
from admin.models.score import Score
from admin.models.user import User
from user.models import db
import json
from datetime import datetime

api_blueprint = Blueprint('api', __name__)
question_controller = QuestionController()
question_group_controller = QuestionGroupController()

@api_blueprint.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions, with optional category filter"""
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
            'content': question.content,
            'category': question.category,
            'group_id': question.group_id if question.group_id else None
        }
        result.append(question_data)
    
    return jsonify(result)

@api_blueprint.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """Get a single question by ID"""
    question = question_controller.get_question_by_id(question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    question_data = {
        'id': question.id,
        'content': question.content,
        'category': question.category,
        'group_id': question.group_id if question.group_id else None
    }
    
    return jsonify(question_data)

@api_blueprint.route('/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """Update a question's content and/or group"""
    data = request.json
    
    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    question = question_controller.get_question_by_id(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Update fields
    if 'content' in data:
        question.content = data['content']
    
    if 'group' in data:
        # Remove from current group if any
        if question.group_id:
            question_controller.remove_from_group(question_id)
        
        # Add to new group if specified (not None or empty string)
        if data['group']:
            question_controller.add_to_group(question_id, data['group'])
    
    # Save changes
    question_controller.update_question(question)
    
    return jsonify({'status': 'success', 'message': 'Question updated successfully'})

@api_blueprint.route('/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Delete a question"""
    question = question_controller.get_question_by_id(question_id)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Delete the question
    question_controller.delete_question(question_id)
    
    return jsonify({'status': 'success', 'message': 'Question deleted successfully'})

@api_blueprint.route('/groups', methods=['GET'])
def get_groups():
    """Get all question groups"""
    groups = question_group_controller.get_all_groups()
    
    result = []
    for group in groups:
        group_data = {
            'id': group.id,
            'name': group.name,
            'description': group.description
        }
        result.append(group_data)
    
    return jsonify(result)

@api_blueprint.route('/groups', methods=['POST'])
def create_group():
    """Create a new question group"""
    data = request.json
    
    # Validate input
    if not data or 'name' not in data:
        return jsonify({'error': 'Group name is required'}), 400
    
    # Create new group
    new_group = question_group_controller.create_group(data['name'], data.get('description', ''))
    
    if not new_group:
        return jsonify({'error': 'Failed to create group'}), 500
    
    return jsonify({
        'status': 'success',
        'message': 'Group created successfully',
        'group': {
            'id': new_group.id,
            'name': new_group.name,
            'description': new_group.description
        }
    })

@api_blueprint.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """Get a single group by ID"""
    group = question_group_controller.get_group_by_id(group_id)
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Get questions in this group
    questions = question_controller.get_questions_by_group_id(group_id)
    
    group_data = {
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'questions': [
            {
                'id': question.id,
                'content': question.content,
                'category': question.category
            } for question in questions
        ]
    }
    
    return jsonify(group_data)

@api_blueprint.route('/groups/<int:group_id>/stats', methods=['GET'])
def get_group_stats(group_id):
    """Get statistics for a group"""
    group = question_group_controller.get_group_by_id(group_id)
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Get questions in this group
    questions = question_controller.get_questions_by_group_id(group_id)
    
    # Calculate statistics
    question_count = len(questions)
    
    # Count unique question types
    question_types = set()
    for question in questions:
        explanation = getattr(question, 'explanation', '')
        if explanation:
            if '[TYPE:fill_blank]' in explanation:
                question_types.add('Fill in the Blank')
            elif '[TYPE:short_answer]' in explanation:
                question_types.add('Short Answer')
            elif '[TYPE:matching]' in explanation:
                question_types.add('Matching')
            elif '[TYPE:essay]' in explanation:
                question_types.add('Essay')
            else:
                question_types.add('Multiple Choice')
        else:
            question_types.add('Multiple Choice')
    
    # Format created date if available
    created_date = 'N/A'
    if hasattr(group, 'created_at') and group.created_at:
        created_date = group.created_at.strftime('%Y-%m-%d')
    
    stats = {
        'questionCount': question_count,
        'typeCount': len(question_types),
        'types': list(question_types),
        'createdDate': created_date
    }
    
    return jsonify(stats)

@api_blueprint.route('/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Update a group's name and/or description"""
    data = request.json
    
    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    group = question_group_controller.get_group_by_id(group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Update fields
    if 'name' in data:
        group.name = data['name']
    
    if 'description' in data:
        group.description = data['description']
    
    # Save changes
    question_group_controller.update_group(group)
    
    return jsonify({'status': 'success', 'message': 'Group updated successfully'})

@api_blueprint.route('/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Delete a group"""
    group = question_group_controller.get_group_by_id(group_id)
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Delete the group and get the count of deleted questions
    success, deleted_count = question_group_controller.delete_group(group_id)
    
    if not success:
        return jsonify({'error': 'Failed to delete group'}), 500
    
    return jsonify({
        'status': 'success', 
        'message': 'Group deleted successfully',
        'deletedQuestions': deleted_count
    })

# Topology API endpoints
@api_blueprint.route('/topology/challenges', methods=['GET'])
def get_topology_challenges():
    """Get all active topology challenges"""
    try:
        topologies = Topology.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': topology.id,
            'title': topology.title,
            'description': topology.description,
            'difficulty': topology.difficulty,
            'topology_type': topology.topology_type,
            'base_score': topology.base_score,
            'time_bonus': topology.time_bonus,
            'perfect_match_bonus': topology.perfect_match_bonus,
        } for topology in topologies])
    except Exception as e:
        print(f"Error in get_topology_challenges: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/topology/challenge/<int:topology_id>', methods=['GET'])
def get_topology_challenge(topology_id):
    """Get a specific topology challenge by ID"""
    try:
        topology = Topology.query.get(topology_id)
        
        if not topology:
            return jsonify({'error': 'Topology not found'}), 404
        
        # Parse the initial configuration JSON
        try:
            initial_config = json.loads(topology.initial_config) if topology.initial_config else None
        except:
            initial_config = None
        
        return jsonify({
            'id': topology.id,
            'title': topology.title,
            'description': topology.description,
            'difficulty': topology.difficulty,
            'topology_type': topology.topology_type,
            'initial_config': initial_config,
            'base_score': topology.base_score,
            'time_bonus': topology.time_bonus,
            'perfect_match_bonus': topology.perfect_match_bonus,
        })
    except Exception as e:
        print(f"Error in get_topology_challenge: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/topology/completed', methods=['GET'])
def get_completed_topologies():
    """Get all completed topology challenges for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get all scores for this user that are related to topology challenges
        scores = Score.query.filter_by(user_id=user_id, category='topology').all()
        
        # Extract the topology IDs
        completed_ids = [score.challenge_id for score in scores if score.challenge_id is not None]
        
        return jsonify({'completed': completed_ids})
    except Exception as e:
        print(f"Error in get_completed_topologies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/save_topology_score', methods=['POST'])
def save_topology_score():
    """Save a score for a completed topology challenge"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in', 'status': 'error'}), 401
    
    try:
        data = request.json
        if not data or 'score' not in data or 'topology_id' not in data:
            return jsonify({'error': 'Invalid data', 'status': 'error'}), 400
        
        user_id = session['user_id']
        score_value = data['score']
        topology_id = data['topology_id']
        category = data.get('category', 'topology')
        
        # Create a new score entry
        new_score = Score(
            user_id=user_id,
            score=score_value,
            category=category,
            challenge_id=topology_id,
            date_achieved=datetime.utcnow()
        )
        
        db.session.add(new_score)
        db.session.commit()
        
        # Update the user's last active timestamp
        user = User.query.get(user_id)
        if user:
            user.last_active = datetime.utcnow()
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Score saved successfully'})
    except Exception as e:
        db.session.rollback()
        print(f"Error in save_topology_score: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500