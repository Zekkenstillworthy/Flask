from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, Response
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from flask_login import login_required, current_user
import json
from io import StringIO
import csv

# Import models
from admin import db
from admin.models.user import AdminUser, Admin
from admin.models.activity_log import ActivityLog

# Create audit log blueprint
audit_log_bp = Blueprint('audit_log', __name__, url_prefix='/logs')

@audit_log_bp.route('/')
@login_required
def index():
    """Display the audit logs page with filtering options"""
    # Get query parameters for filtering
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Base query
    query = ActivityLog.query.order_by(desc(ActivityLog.timestamp))
    
    # Apply filters if provided
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action_type:
        query = query.filter_by(action_type=action_type)
        
    if entity_type:
        query = query.filter_by(related_entity_type=entity_type)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(ActivityLog.timestamp >= from_date_obj)
        except ValueError:
            flash('Invalid from date format. Please use YYYY-MM-DD.', 'error')
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            # Add one day to include the entire end date
            to_date_obj = to_date_obj + timedelta(days=1)
            query = query.filter(ActivityLog.timestamp <= to_date_obj)
        except ValueError:
            flash('Invalid to date format. Please use YYYY-MM-DD.', 'error')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Execute query with pagination
    logs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get distinct action types for filter dropdown
    action_types = db.session.query(ActivityLog.action_type.distinct()).all()
    action_types = [a[0] for a in action_types]
    
    # Get distinct entity types for filter dropdown
    entity_types = db.session.query(ActivityLog.related_entity_type.distinct()).filter(ActivityLog.related_entity_type != None).all()
    entity_types = [e[0] for e in entity_types]
    
    # Get all users for filter dropdown
    users = AdminUser.query.all()
    admins = Admin.query.all()
    
    # Get stats for summary cards
    total_logs = ActivityLog.query.count()
    today = datetime.utcnow().date()
    today_logs = ActivityLog.query.filter(
        func.date(ActivityLog.timestamp) == today
    ).count()
    
    # Group logs by action type for chart
    action_type_stats = (
        db.session.query(
            ActivityLog.action_type,
            func.count(ActivityLog.id).label('count')
        )
        .group_by(ActivityLog.action_type)
        .all()
    )
    action_type_data = {action: count for action, count in action_type_stats}
    
    return render_template(
        'admin/audit_logs.html',
        logs=logs,
        users=users,
        admins=admins,
        action_types=action_types,
        entity_types=entity_types,
        total_logs=total_logs,
        today_logs=today_logs,
        action_type_data=json.dumps(action_type_data),
        active_page='audit_logs',
        # Pass filter values back to the template
        selected_user_id=user_id,
        selected_action_type=action_type,
        selected_entity_type=entity_type,
        selected_from_date=from_date,
        selected_to_date=to_date
    )

@audit_log_bp.route('/export')
@login_required
def export_logs():
    """Export audit logs as CSV"""
    # Similar filtering logic as in index
    user_id = request.args.get('user_id', type=int)
    action_type = request.args.get('action_type')
    entity_type = request.args.get('entity_type')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # Base query
    query = ActivityLog.query.order_by(desc(ActivityLog.timestamp))
    
    # Apply filters if provided
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if action_type:
        query = query.filter_by(action_type=action_type)
        
    if entity_type:
        query = query.filter_by(related_entity_type=entity_type)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(ActivityLog.timestamp >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            to_date_obj = to_date_obj + timedelta(days=1)
            query = query.filter(ActivityLog.timestamp <= to_date_obj)
        except ValueError:
            pass
    
    # Fetch all logs matching the criteria
    logs = query.all()
    
    # Create a CSV string
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'User ID', 'Action Type', 'Message', 'Timestamp', 'Entity Type', 'Entity ID'])
    
    # Write data
    for log in logs:
        timestamp_str = log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else 'N/A'
        writer.writerow([
            log.id, 
            log.user_id, 
            log.action_type, 
            log.message, 
            timestamp_str, 
            log.related_entity_type or 'N/A', 
            log.related_entity_id or 'N/A'
        ])
    
    # Prepare the response
    output.seek(0)
    filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@audit_log_bp.route('/clear', methods=['POST'])
@login_required
def clear_logs():
    """Clear old audit logs"""
    days = request.form.get('days', 30, type=int)
    
    if days < 1:
        flash('Please enter a valid number of days', 'error')
        return redirect(url_for('audit_log.index'))
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Log this activity first before deleting logs
        ActivityLog.log_activity(
            user_id=current_user.id,
            action_type='clear_logs',
            message=f'Cleared audit logs older than {days} days'
        )
        
        # Delete logs older than cutoff date
        deleted_count = ActivityLog.query.filter(ActivityLog.timestamp < cutoff_date).delete()
        
        db.session.commit()
        flash(f'Successfully cleared {deleted_count} logs older than {days} days', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing logs: {str(e)}', 'error')
    
    return redirect(url_for('audit_log.index'))
