from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..app import db
from ..models.question_group import QuestionGroup
from ..models.question import Question

question_group_bp = Blueprint('question_group', __name__, url_prefix='/groups')

class QuestionGroupController:
    @staticmethod
    @question_group_bp.route('/')
    def index():
        groups = QuestionGroup.query.order_by(QuestionGroup.name).all()
        return render_template(
            'admin/question_groups.html',
            groups=groups,
            active_page='question_groups'
        )
    
    @staticmethod
    @question_group_bp.route('/add', methods=['GET', 'POST'])
    def add_group():
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if not name:
                flash('Group name is required', 'error')
                return render_template('admin/add_question_group.html')
            
            new_group = QuestionGroup(
                name=name,
                description=description
            )
            
            try:
                db.session.add(new_group)
                db.session.commit()
                flash('Question group created successfully', 'success')
                return redirect(url_for('question_group.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating question group: {str(e)}', 'error')
                
        return render_template('admin/add_question_group.html')
    
    @staticmethod
    @question_group_bp.route('/edit/<int:group_id>', methods=['GET', 'POST'])
    def edit_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if not name:
                flash('Group name is required', 'error')
                return render_template('admin/edit_question_group.html', group=group)
            
            group.name = name
            group.description = description
            
            try:
                db.session.commit()
                flash('Question group updated successfully', 'success')
                return redirect(url_for('question_group.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating question group: {str(e)}', 'error')
                
        return render_template('admin/edit_question_group.html', group=group)
    
    @staticmethod
    @question_group_bp.route('/delete/<int:group_id>', methods=['POST'])
    def delete_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        try:
            db.session.delete(group)
            db.session.commit()
            flash('Question group deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting question group: {str(e)}', 'error')
            
        return redirect(url_for('question_group.index'))
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>')
    def view_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        # Group questions by category for better organization
        categorized_questions = {}
        for question in group.questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return render_template(
            'admin/group_questions.html',
            group=group,
            questions=group.questions,
            question_count=len(group.questions),
            categorized_questions=categorized_questions,
            active_page='question_groups'
        )
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>/add_questions', methods=['GET', 'POST'])
    def add_questions_to_group(group_id):
        group = QuestionGroup.query.get_or_404(group_id)
        
        if request.method == 'POST':
            question_ids = request.form.getlist('question_ids')
            
            if not question_ids:
                flash('No questions selected', 'error')
                return redirect(url_for('question_group.add_questions_to_group', group_id=group.id))
            
            selected_questions = Question.query.filter(Question.id.in_(question_ids)).all()
            
            for question in selected_questions:
                if question not in group.questions:
                    group.questions.append(question)
            
            try:
                db.session.commit()
                flash(f'Added {len(selected_questions)} question(s) to the group', 'success')
                return redirect(url_for('question_group.view_group', group_id=group.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding questions to group: {str(e)}', 'error')
        
        # Get available questions that are not already in the group
        current_question_ids = [q.id for q in group.questions]
        if current_question_ids:
            available_questions = Question.query.filter(~Question.id.in_(current_question_ids)).all()
        else:
            available_questions = Question.query.all()
        
        # Group questions by category
        categorized_questions = {}
        for question in available_questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return render_template(
            'admin/add_questions_to_group.html',
            group=group,
            categorized_questions=categorized_questions,
            active_page='question_groups'
        )
    
    @staticmethod
    @question_group_bp.route('/<int:group_id>/remove_question/<int:question_id>', methods=['POST'])
    def remove_question_from_group(group_id, question_id):
        group = QuestionGroup.query.get_or_404(group_id)
        question = Question.query.get_or_404(question_id)
        
        if question in group.questions:
            group.questions.remove(question)
            
            try:
                db.session.commit()
                flash('Question removed from group successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error removing question from group: {str(e)}', 'error')
                
        return redirect(url_for('question_group.view_group', group_id=group.id))
    
    @staticmethod
    def delete_group(group_id):
        """Delete a question group and count deleted questions"""
        group = QuestionGroup.query.get(group_id)
        if not group:
            return False, 0
            
        # Count questions in this group before deleting
        deletedQuestions = len(group.questions) if hasattr(group, 'questions') else 0
        
        try:
            db.session.delete(group)
            db.session.commit()
            return True, deletedQuestions
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting group: {str(e)}")
            return False, 0
