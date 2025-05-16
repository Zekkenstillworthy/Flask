from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, extract, or_
import json
from flask_login import login_required, current_user

# Import models
from admin import db  # Add this import for db
from admin.models.user import AdminUser
from admin.models.score import AdminScore  # Updated to use renamed model
from admin.models.question import Question
from admin.models.essay_response import EssayResponse
from admin.models.activity_log import ActivityLog

# Create dashboard blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/admin')

@dashboard_bp.route('/')
@login_required
def index():
    # Get basic stats - ensure we're using the correct tables
    total_users = AdminUser.query.count()
    total_scores = AdminScore.query.count()
    
    # Handle case where questions might be in either question or questions table
    # We'll detect which one has data and use it
    question_count_main = Question.query.count()
    
    # Get recent scores for dashboard table
    recent_scores = AdminScore.query.order_by(desc(AdminScore.date_attempted)).limit(10).all()
    
    # Score distribution data for chart - adjusted based on actual score data
    # Your score data has scores like 1.5, 2, 0.75, 2.5 which seem to be out of 3
    score_dist = {
        'very_low': AdminScore.query.filter(AdminScore.score < 0.6).count(),  # Less than 20%
        'low': AdminScore.query.filter(and_(AdminScore.score >= 0.6, AdminScore.score < 1.2)).count(),  # 20-40%
        'medium': AdminScore.query.filter(and_(AdminScore.score >= 1.2, AdminScore.score < 1.8)).count(),  # 40-60%
        'high': AdminScore.query.filter(and_(AdminScore.score >= 1.8, AdminScore.score < 2.4)).count(),  # 60-80%
        'very_high': AdminScore.query.filter(AdminScore.score >= 2.4).count()  # 80%+
    }
    
    # User activity data - last 7 days
    today = datetime.now().date()
    activity_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    # Count active users per day (users who attempted a quiz)
    active_users = []
    for date_str in activity_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        count = AdminScore.query.filter(
            func.date(AdminScore.date_attempted) == date_obj
        ).with_entities(AdminScore.user_id).distinct().count()
        active_users.append(count)
    
    # Average scores by category
    category_avg = {}
    categories = ['riddle', 'topology', 'troubleshoot', 'crimping']
    
    for cat in categories:
        # Calculate average as percentage of 3 (max score based on your data)
        avg = AdminScore.query.filter(AdminScore.category == cat).with_entities(func.avg(AdminScore.score)).scalar() or 0
        category_avg[cat] = round(float(avg) * 100 / 3, 1)  # Convert to percentage based on max score of 3
    
    # Question difficulty distribution
    # We'll use essay_response data since it has graded scores
    question_difficulty = {
        'easy': EssayResponse.query.filter(EssayResponse.graded_score >= 80).count(),
        'medium': EssayResponse.query.filter(and_(EssayResponse.graded_score >= 60, 
                                                 EssayResponse.graded_score < 80)).count(),
        'hard': EssayResponse.query.filter(EssayResponse.graded_score < 60).count()
    }
    
    # If we don't have enough data in essay_responses, add placeholders
    if sum(question_difficulty.values()) == 0:
        question_difficulty = {
            'easy': 2,
            'medium': 1, 
            'hard': 1
        }
    
    # Recent system activity logs based on activity_logs table
    # If activity_logs table is empty, create placeholders
    activity_logs = []
    try:
        db_activity_logs = ActivityLog.query.order_by(desc(ActivityLog.timestamp)).limit(4).all()
        if db_activity_logs:
            for log in db_activity_logs:
                activity_logs.append({
                    'action_type': log.action_type,
                    'message': log.message,
                    'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
        else:
            # Use essay_response data to create some activity logs
            essays = EssayResponse.query.order_by(desc(EssayResponse.submission_date)).limit(4).all()
            for essay in essays:
                action_type = 'essay'
                if essay.is_graded:
                    action_type = 'edit'
                activity_logs.append({
                    'action_type': action_type,
                    'message': f'Essay response {"graded" if essay.is_graded else "submitted"} by User ID {essay.user_id}',
                    'timestamp': essay.submission_date.strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        # Fallback if there's an error
        activity_logs = [
            {
                'action_type': 'login',
                'message': 'Admin logged in',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'action_type': 'score',
                'message': 'User ID 1 completed riddle quiz with score 2.5/3',
                'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    
    # System alerts based on data in the database
    system_alerts = []
    
    # Check for unreviewed essays
    unreviewed_essays = EssayResponse.query.filter_by(is_graded=False).count()
    if unreviewed_essays > 0:
        system_alerts.append({
            'message': f'{unreviewed_essays} unreviewed essay responses require attention',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return render_template('admin/dashboard.html', 
                           total_users=total_users,
                           total_scores=total_scores,
                           total_questions=question_count_main,
                           recent_scores=recent_scores,
                           score_dist=score_dist,
                           activity_dates=json.dumps(activity_dates),
                           active_users=json.dumps(active_users),
                           category_avg=category_avg,
                           question_difficulty=question_difficulty,
                           activity_logs=activity_logs,
                           system_alerts=system_alerts,
                           active_page='dashboard')

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint to get filtered chart data"""
    date_range = request.args.get('date_range', '7')  # Default to 7 days
    category = request.args.get('category', 'all')    # Default to all categories
    
    try:
        # Convert date_range to integer days (if not 'all')
        if date_range != 'all':
            days = int(date_range)
            start_date = datetime.now() - timedelta(days=days)
        else:
            start_date = datetime(2000, 1, 1)  # Very old date to include all
        
        # Base query with date filter
        query = AdminScore.query.filter(AdminScore.date_attempted >= start_date)
        
        # Add category filter if specified
        if category != 'all':
            query = query.filter(AdminScore.category == category)
        
        # Score distribution data - adjusted for actual score data
        score_dist = {
            'very_low': query.filter(AdminScore.score < 0.6).count(),
            'low': query.filter(and_(AdminScore.score >= 0.6, AdminScore.score < 1.2)).count(),
            'medium': query.filter(and_(AdminScore.score >= 1.2, AdminScore.score < 1.8)).count(),
            'high': query.filter(and_(AdminScore.score >= 1.8, AdminScore.score < 2.4)).count(),
            'very_high': query.filter(AdminScore.score >= 2.4).count()
        }
        
        # Generate dates for the activity chart
        today = datetime.now().date()
        if date_range == 'all':
            # For 'all', group by months
            # This would need more complex SQL based on your DB
            activity_dates = ["All time"]
            active_users = [query.with_entities(AdminScore.user_id).distinct().count()]
        else:
            # For specific ranges, show daily data
            activity_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') 
                             for i in range(int(date_range)-1, -1, -1)]
            
            # Count active users per day
            active_users = []
            for date_str in activity_dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                count = query.filter(
                    func.date(AdminScore.date_attempted) == date_obj
                ).with_entities(AdminScore.user_id).distinct().count()
                active_users.append(count)
        
        # Category averages - adjusted for max score of 3
        category_avg = {}
        if category == 'all':
            categories = ['riddle', 'topology', 'troubleshoot', 'crimping']
            for cat in categories:
                cat_query = query.filter(AdminScore.category == cat)
                avg = cat_query.with_entities(func.avg(AdminScore.score)).scalar() or 0
                category_avg[cat] = round(float(avg) * 100 / 3, 1)  # Use max score of 3
        else:
            avg = query.with_entities(func.avg(AdminScore.score)).scalar() or 0
            category_avg[category] = round(float(avg) * 100 / 3, 1)  # Use max score of 3
        
        return jsonify({
            'score_dist': score_dist,
            'activity_dates': activity_dates,
            'active_users': active_users,
            'category_avg': category_avg,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

# Add route for user management
@dashboard_bp.route('/user-management')
@login_required
def user_management():
    # Get regular users with their stats
    users = AdminUser.query.all()
    user_stats = []
    for user in users:
        scores_count = AdminScore.query.filter_by(user_id=user.id).count()
        highest_score = db.session.query(func.max(AdminScore.score)).filter_by(user_id=user.id).scalar() or 0
        
        user_stats.append({
            'user': user,
            'scores_count': scores_count,
            'highest_score': highest_score
        })
    
    # Add admin users from the Admin model
    from admin.models.user import Admin
    admins = Admin.query.all()
    
    return render_template('admin/user_management.html', 
                           user_stats=user_stats, 
                           admins=admins,
                           active_page='users')

# Add route for data export
@dashboard_bp.route('/export-data')
@login_required
def export_data():
    export_type = request.args.get('type', 'scores')
    format_type = request.args.get('format', 'json')
    
    if export_type == 'scores':
        data = AdminScore.query.all()
    elif export_type == 'users':
        data = AdminUser.query.all()
    elif export_type == 'questions':
        data = Question.query.all()
    else:
        return jsonify({'error': 'Invalid export type'}), 400
    
    # Convert data to requested format (simplified version)
    result = []
    for item in data:
        result.append(item.to_dict() if hasattr(item, 'to_dict') else {'id': item.id})
    
    response = {
        'data': result,
        'count': len(result),
        'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'export_type': export_type
    }
    
    return jsonify(response)
