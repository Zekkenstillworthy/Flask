from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from datetime import datetime
from sqlalchemy import func, desc
from flask_login import login_required, current_user

# Import models
from admin import db
from admin.models.scenario import Scenario

# Create scenario blueprint
scenario_bp = Blueprint('scenario', __name__, url_prefix='/scenarios')

@scenario_bp.route('/')
@login_required
def index():
    """
    Display all scenarios
    """
    scenarios = Scenario.query.all()
    
    return render_template('admin/scenario.html', 
                          active_page='scenarios',
                          scenarios=scenarios)

# API Routes to match frontend expectations
@scenario_bp.route('/api/list', methods=['GET'])
@login_required
def api_list_scenarios():
    """
    API endpoint to get all scenarios
    """
    scenario_controller = ScenarioController()
    scenarios = scenario_controller.get_all_scenarios()
    return jsonify(scenarios)

@scenario_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_scenario():
    """
    API endpoint to create a new scenario
    """
    scenario_controller = ScenarioController()
    data = request.json
    result = scenario_controller.create_scenario(data)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@scenario_bp.route('/api/update/<int:scenario_id>', methods=['PUT'])
@login_required
def api_update_scenario(scenario_id):
    """
    API endpoint to update a scenario
    """
    scenario_controller = ScenarioController()
    data = request.json
    result = scenario_controller.update_scenario(scenario_id, data)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@scenario_bp.route('/api/delete/<int:scenario_id>', methods=['DELETE'])
@login_required
def api_delete_scenario(scenario_id):
    """
    API endpoint to delete a scenario
    """
    scenario_controller = ScenarioController()
    result = scenario_controller.delete_scenario(scenario_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@scenario_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new scenario
    """
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        
        new_scenario = Scenario(
            title=title,
            description=description,
            difficulty=difficulty
        )
        
        db.session.add(new_scenario)
        db.session.commit()
        flash('Scenario created successfully!', 'success')
        return redirect(url_for('scenario.index'))
    
    return render_template('admin/scenario.html', active_page='scenarios')

@scenario_bp.route('/edit/<int:scenario_id>', methods=['GET', 'POST'])
@login_required
def edit(scenario_id):
    """
    Edit an existing scenario
    """
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if request.method == 'POST':
        scenario.title = request.form.get('title')
        scenario.description = request.form.get('description')
        scenario.difficulty = request.form.get('difficulty')
        db.session.commit()
        flash('Scenario updated successfully!', 'success')
        return redirect(url_for('scenario.index'))
    
    return render_template('admin/scenario_edit.html', 
                          active_page='scenarios',
                          scenario=scenario)

@scenario_bp.route('/delete/<int:scenario_id>', methods=['POST'])
@login_required
def delete(scenario_id):
    """
    Delete a scenario
    """
    scenario = Scenario.query.get_or_404(scenario_id)
    db.session.delete(scenario)
    db.session.commit()
    flash('Scenario deleted successfully!', 'success')
    
    return redirect(url_for('scenario.index'))

from datetime import datetime
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from admin.models.scenario import Scenario
from admin import db

class ScenarioController:
    def get_all_scenarios(self):
        """Get all scenarios from the database"""
        try:
            scenarios = Scenario.query.all()
            result = []
            for scenario in scenarios:
                result.append({
                    'id': scenario.id,
                    'title': scenario.title,
                    'description': scenario.description,
                    'difficulty': scenario.difficulty,
                    'created_at': scenario.created_at.strftime('%Y-%m-%d %H:%M:%S') if scenario.created_at else None,
                    'updated_at': scenario.updated_at.strftime('%Y-%m-%d %H:%M:%S') if scenario.updated_at else None
                })
            return result
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': 'Failed to fetch scenarios'}
    
    def get_scenario_by_id(self, scenario_id):
        """Get a specific scenario by ID"""
        try:
            scenario = Scenario.query.get(scenario_id)
            if not scenario:
                return {'error': f'Scenario with ID {scenario_id} not found'}
            
            return {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'created_at': scenario.created_at.strftime('%Y-%m-%d %H:%M:%S') if scenario.created_at else None,
                'updated_at': scenario.updated_at.strftime('%Y-%m-%d %H:%M:%S') if scenario.updated_at else None
            }
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': 'Failed to fetch scenario'}
    
    def create_scenario(self, data):
        """Create a new scenario"""
        try:
            if not data.get('title') or not data.get('description') or not data.get('difficulty'):
                return {'error': 'Missing required fields'}
            
            new_scenario = Scenario(
                title=data.get('title'),
                description=data.get('description'),
                difficulty=data.get('difficulty'),
                created_at=datetime.now()
            )
            
            db.session.add(new_scenario)
            db.session.commit()
            
            return {
                'id': new_scenario.id,
                'title': new_scenario.title,
                'description': new_scenario.description,
                'difficulty': new_scenario.difficulty,
                'message': 'Scenario created successfully'
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': 'Failed to create scenario'}
    
    def update_scenario(self, scenario_id, data):
        """Update an existing scenario"""
        try:
            scenario = Scenario.query.get(scenario_id)
            if not scenario:
                return {'error': f'Scenario with ID {scenario_id} not found'}
            
            if data.get('title'):
                scenario.title = data.get('title')
            if data.get('description'):
                scenario.description = data.get('description')
            if data.get('difficulty'):
                scenario.difficulty = data.get('difficulty')
            
            scenario.updated_at = datetime.now()
            
            db.session.commit()
            
            return {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'message': 'Scenario updated successfully'
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': 'Failed to update scenario'}
    
    def delete_scenario(self, scenario_id):
        """Delete a scenario"""
        try:
            scenario = Scenario.query.get(scenario_id)
            if not scenario:
                return {'error': f'Scenario with ID {scenario_id} not found'}
            
            db.session.delete(scenario)
            db.session.commit()
            
            return {'message': f'Scenario with ID {scenario_id} deleted successfully'}
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return {'error': 'Failed to delete scenario'}