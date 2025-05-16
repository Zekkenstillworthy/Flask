from flask import Blueprint, request, jsonify
from admin import db
from admin.models.scenario import Scenario
from admin.controllers.scenario_controller import ScenarioController
from flask_login import login_required, current_user

scenario_routes = Blueprint('scenario_routes', __name__)
scenario_controller = ScenarioController()

@scenario_routes.route('/scenarios/api/list', methods=['GET'])
@login_required
def get_all_scenarios():
    """Get all scenarios"""
    scenarios = scenario_controller.get_all_scenarios()
    return jsonify(scenarios)

@scenario_routes.route('/scenarios/api/create', methods=['POST'])
@login_required
def create_scenario():
    """Create a new scenario"""
    data = request.get_json()
    result = scenario_controller.create_scenario(data)
    return jsonify(result)

@scenario_routes.route('/scenarios/api/update/<int:scenario_id>', methods=['PUT'])
@login_required
def update_scenario(scenario_id):
    """Update an existing scenario"""
    data = request.get_json()
    result = scenario_controller.update_scenario(scenario_id, data)
    return jsonify(result)

@scenario_routes.route('/scenarios/api/delete/<int:scenario_id>', methods=['DELETE'])
@login_required
def delete_scenario(scenario_id):
    """Delete a scenario"""
    result = scenario_controller.delete_scenario(scenario_id)
    return jsonify(result)

@scenario_routes.route('/scenarios/api/<int:scenario_id>', methods=['GET'])
@login_required
def get_scenario(scenario_id):
    """Get a specific scenario"""
    scenario = scenario_controller.get_scenario_by_id(scenario_id)
    return jsonify(scenario)