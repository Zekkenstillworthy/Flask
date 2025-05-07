from flask import request, jsonify, Blueprint
from admin import db
from admin.models.topology import Topology
from datetime import datetime
import json

class TopologyController:
    
    def get_all_topologies(self):
        """Get all topology challenges"""
        try:
            topologies = Topology.query.all()
            return jsonify([topology.to_dict() for topology in topologies]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_topology(self, topology_id):
        """Get a specific topology challenge by ID"""
        topology = Topology.query.get_or_404(topology_id)
        return jsonify(topology.to_dict()), 200
    
    def create_topology(self):
        """Create a new topology challenge"""
        data = request.json
        
        if not data or not all(k in data for k in ['title', 'description', 'expected_config']):
            return jsonify({"error": "Missing required fields"}), 400
        
        try:
            # Create new topology object
            new_topology = Topology(
                title=data['title'],
                description=data['description'],
                difficulty=data.get('difficulty', 'medium'),
                topology_type=data.get('topology_type', 'point-to-point'),
                base_score=data.get('base_score', 10),
                time_bonus=data.get('time_bonus', 0),
                perfect_match_bonus=data.get('perfect_match_bonus', 5),
                is_active=data.get('is_active', True)
            )
            
            # Set configuration fields
            if 'initial_config' in data:
                new_topology.initial_config = data['initial_config']
            
            new_topology.expected_config = data['expected_config']
            
            # Save to database
            db.session.add(new_topology)
            db.session.commit()
            
            return jsonify({"message": "Topology created successfully", "id": new_topology.id}), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    def update_topology(self, topology_id):
        """Update an existing topology challenge"""
        topology = Topology.query.get_or_404(topology_id)
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            # Update basic fields
            if 'title' in data:
                topology.title = data['title']
            
            if 'description' in data:
                topology.description = data['description']
            
            if 'difficulty' in data:
                topology.difficulty = data['difficulty']
                
            if 'topology_type' in data:
                topology.topology_type = data['topology_type']
                
            if 'base_score' in data:
                topology.base_score = data['base_score']
                
            if 'time_bonus' in data:
                topology.time_bonus = data['time_bonus']
                
            if 'perfect_match_bonus' in data:
                topology.perfect_match_bonus = data['perfect_match_bonus']
                
            if 'is_active' in data:
                topology.is_active = data['is_active']
            
            # Update configuration fields
            if 'initial_config' in data:
                topology.initial_config = data['initial_config']
            
            if 'expected_config' in data:
                topology.expected_config = data['expected_config']
            
            # Update the updated_at timestamp
            topology.updated_at = datetime.utcnow()
            
            # Save to database
            db.session.commit()
            
            return jsonify({"message": "Topology updated successfully"}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    def delete_topology(self, topology_id):
        """Delete a topology challenge"""
        topology = Topology.query.get_or_404(topology_id)
        
        try:
            db.session.delete(topology)
            db.session.commit()
            return jsonify({"message": "Topology deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    def preview_topology(self, topology_id):
        """Get a topology in a format suitable for previewing"""
        topology = Topology.query.get_or_404(topology_id)
        
        # Return the topology with both configuration fields for the preview
        preview_data = topology.to_dict()
        
        return jsonify(preview_data), 200
    
    def toggle_active_status(self, topology_id):
        """Toggle the active status of a topology challenge"""
        topology = Topology.query.get_or_404(topology_id)
        
        try:
            # Toggle the is_active field
            topology.is_active = not topology.is_active
            
            # Update the updated_at timestamp
            topology.updated_at = datetime.utcnow()
            
            # Save to database
            db.session.commit()
            
            return jsonify({
                "message": f"Topology is now {'active' if topology.is_active else 'inactive'}",
                "is_active": topology.is_active
            }), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500