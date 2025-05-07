from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
import csv
from io import StringIO
from datetime import datetime
from sqlalchemy import func
from ..app import db
from ..models.score import Score
from ..models.user import User

score_bp = Blueprint('score', __name__, url_prefix='/scores')

class ScoreController:
    @staticmethod
    @score_bp.route('/')
    def index():
        scores = Score.query.order_by(Score.date_attempted.desc()).all()
        
        # Fetch users for the user list view
        users = User.query.all()
        
        category_stats = (
            db.session.query(
                Score.category, 
                func.count(Score.id).label('count'),
                func.avg(Score.score).label('avg_score'),
                func.max(Score.score).label('max_score')
            )
            .group_by(Score.category)
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
    def reset_scores():
        category = request.form.get('category')
        
        try:
            if category:
                Score.query.filter_by(category=category).delete()
            else:
                Score.query.delete()
            
            db.session.commit()
            flash('Scores reset successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error resetting scores: {str(e)}', 'error')
        
        return redirect(url_for('score.index'))

    @staticmethod
    @score_bp.route('/delete/<int:score_id>', methods=['POST'])
    def delete_score(score_id):
        try:
            score = Score.query.get_or_404(score_id)
            db.session.delete(score)
            db.session.commit()
            flash('Score deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting score: {str(e)}', 'error')
        
        return redirect(url_for('score.index'))

    @staticmethod
    @score_bp.route('/export')
    def export_scores():
        try:
            scores = Score.query.order_by(Score.date_attempted.desc()).all()
            
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
    def user_scores(user_id):
        # Fetch all scores for a specific user
        user_scores = Score.query.filter_by(user_id=user_id).order_by(Score.date_attempted.desc()).all()
        
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
