from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
import csv
from io import StringIO
from datetime import datetime
from sqlalchemy import func
from flask_login import login_required, current_user
from ..app import db
from ..models.score import AdminScore  # Updated to use renamed model
from ..models.user import User as AdminUser  # Rename to avoid conflicts

score_bp = Blueprint('score', __name__, url_prefix='/scores')

class ScoreController:
    @staticmethod
    @score_bp.route('/')
    @login_required
    def index():
        scores = AdminScore.query.order_by(AdminScore.date_attempted.desc()).all()
        
        # Fetch users for the user list view
        users = AdminUser.query.all()
        
        category_stats = (
            db.session.query(
                AdminScore.category, 
                func.count(AdminScore.id).label('count'),
                func.avg(AdminScore.score).label('avg_score'),
                func.max(AdminScore.score).label('max_score')
            )
            .group_by(AdminScore.category)
            .all()
        )
        
        return render_template(
            'admin/scores.html', 
            scores=scores,
            category_stats=category_stats,
            users=users,
            active_page='scores'
        )

    @staticmethod
    @score_bp.route('/reset', methods=['POST'])
    @login_required
    def reset_scores():
        category = request.form.get('category')
        
        try:
            if category:
                AdminScore.query.filter_by(category=category).delete()
            else:
                AdminScore.query.delete()
            
            db.session.commit()
            flash('Scores reset successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error resetting scores: {str(e)}', 'error')
        
        return redirect(url_for('score.index'))

    @staticmethod
    @score_bp.route('/delete/<int:score_id>', methods=['POST'])
    @login_required
    def delete_score(score_id):
        try:
            score = AdminScore.query.get_or_404(score_id)
            db.session.delete(score)
            db.session.commit()
            flash('Score deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting score: {str(e)}', 'error')
        
        return redirect(url_for('score.index'))

    @staticmethod
    @score_bp.route('/export')
    @login_required
    def export_scores():
        try:
            scores = AdminScore.query.order_by(AdminScore.date_attempted.desc()).all()
            
            # Create a CSV string
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'User ID', 'Score', 'Category', 'Date Attempted'])
            
            # Write data
            for score in scores:
                date_str = score.date_attempted.strftime('%Y-%m-%d %H:%M:%S') if score.date_attempted else 'N/A'
                writer.writerow([score.id, score.user_id, score.score, score.category, date_str])
            
            # Prepare the response
            output.seek(0)
            filename = f"riddlenet_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename={filename}"}
            )
        except Exception as e:
            flash(f'Error exporting scores: {str(e)}', 'error')
            return redirect(url_for('score.index'))

    @staticmethod
    @score_bp.route('/user/<int:user_id>', methods=['GET'])
    @login_required
    def user_scores(user_id):
        # Fetch all scores for a specific user
        user_scores = AdminScore.query.filter_by(user_id=user_id).order_by(AdminScore.date_attempted.desc()).all()
        
        # Format the scores for JSON response
        scores_data = []
        for score in user_scores:
            scores_data.append({
                'id': score.id,
                'score': score.score,
                'category': score.category,
                'date_attempted': score.date_attempted.strftime('%Y-%m-%d %H:%M') if score.date_attempted else 'N/A'
            })
            
        # Calculate statistics per category
        stats = {}
        category_scores = {}
        
        for score in user_scores:
            category = score.category
            
            if category not in category_scores:
                category_scores[category] = []
                
            category_scores[category].append(score.score)
            
        for category, scores in category_scores.items():
            stats[category] = {
                'count': len(scores),
                'avg_score': sum(scores) / len(scores) if len(scores) > 0 else 0,
                'max_score': max(scores) if len(scores) > 0 else 0
            }
            
        return jsonify({
            'success': True,
            'scores': scores_data,
            'stats': stats
        })
