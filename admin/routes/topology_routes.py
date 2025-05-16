from flask import Blueprint, jsonify, request
from admin.controllers.topology_controller import TopologyController
from flask_login import login_required, current_user

# Create the topology blueprint
topology_bp = Blueprint('topology', __name__, url_prefix='/admin/topology')

# Initialize the controller
controller = TopologyController()

@topology_bp.route('/', methods=['GET'])
@login_required
def get_all_topologies():
    """Get all topology challenges"""
    return controller.get_all_topologies()

@topology_bp.route('/<int:topology_id>', methods=['GET'])
@login_required
def get_topology(topology_id):
    """Get a specific topology challenge by ID"""
    return controller.get_topology(topology_id)

@topology_bp.route('/', methods=['POST'])
@login_required
def create_topology():
    """Create a new topology challenge"""
    return controller.create_topology()

@topology_bp.route('/<int:topology_id>', methods=['PUT'])
@login_required
def update_topology(topology_id):
    """Update an existing topology challenge"""
    return controller.update_topology(topology_id)

@topology_bp.route('/<int:topology_id>', methods=['DELETE'])
@login_required
def delete_topology(topology_id):
    """Delete a topology challenge"""
    return controller.delete_topology(topology_id)

@topology_bp.route('/<int:topology_id>/preview', methods=['GET'])
@login_required
def preview_topology(topology_id):
    """Get a topology in a format suitable for previewing"""
    return controller.preview_topology(topology_id)

@topology_bp.route('/<int:topology_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active_status(topology_id):
    """Toggle the active status of a topology challenge"""
    return controller.toggle_active_status(topology_id)