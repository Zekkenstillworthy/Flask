from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
from flask_login import login_required, current_user
from ..app import db
from ..models.question import Question
from ..models.question_group import QuestionGroup

question_bp = Blueprint('question', __name__, url_prefix='/questions')

class QuestionController:
    @staticmethod
    @question_bp.route('/')
    @login_required
    def index():
        # Show question groups first instead of all questions
        groups = QuestionGroup.query.order_by(QuestionGroup.name).all()
        
        return render_template(
            'admin/questions.html',
            groups=groups,
            active_page='questions'
        )
    @staticmethod
    @question_bp.route('/ungrouped', methods=['GET'])
    @login_required
    def get_ungrouped_questions():
        grouped_question_ids = []
        for group in groups:
            for question in group.questions:
                grouped_question_ids.append(question.id)
        
        ungrouped_questions = Question.query.filter(~Question.id.in_(grouped_question_ids)).all() if grouped_question_ids else Question.query.all()
        
        # Group ungrouped questions by category
        categorized_questions = {}
        for question in ungrouped_questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        return render_template(
            'admin/questions.html', 
            groups=groups,
            questions=ungrouped_questions,
            categorized_questions=categorized_questions,
            question_count=len(ungrouped_questions),
            active_page='questions'
        )

    @staticmethod
    @question_bp.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_question():
        if request.method == 'POST':
            numb = int(request.form.get('numb', 1))
            question_text = request.form.get('question')
            explanation = request.form.get('explanation', '')
            category = request.form.get('category', 'riddle')
            question_type = request.form.get('question_type', 'multiple_choice')
            
            options = []
            answer = None
            
            # Process different question types
            if question_type == 'multiple_choice':
                # Get options from form for multiple choice
                for i in range(4):
                    option = request.form.get(f'option{i+1}')
                    if option:
                        options.append(option)
                
                answer = request.form.get('mc_answer')
                
                if not question_text or not answer or len(options) < 2:
                    flash('Please fill all required fields for multiple choice questions', 'error')
                    return render_template('admin/add_question.html')
                    
            elif question_type == 'true_false':
                # For true/false, we only need the true/false answer
                options = ["True", "False"]
                answer = request.form.get('tf_answer')
                
                if not question_text or not answer:
                    flash('Please fill all required fields for true/false questions', 'error')
                    return render_template('admin/add_question.html')
                    
            elif question_type == 'fill_blank':
                # For fill-in-the-blank, we store possible answers
                options = []
                answer = request.form.get('blank_answer')
                
                if not question_text or not answer:
                    flash('Please provide a question and at least one correct answer', 'error')
                    return render_template('admin/add_question.html')
                    
            elif question_type == 'short_answer':
                # For short answer, store the keywords or expected answer
                options = []
                answer = request.form.get('sa_answer')
                
                if not question_text or not answer:
                    flash('Please provide a question and answer keywords', 'error')
                    return render_template('admin/add_question.html')
                    
            elif question_type == 'matching':
                # For matching, store the matching pairs
                items = request.form.getlist('matching_item[]')
                matches = request.form.getlist('matching_match[]')
                
                # Check if drag-and-drop style is selected
                drag_drop_style = request.form.get('drag_drop_style')
                
                # Create matching pairs as JSON and store in answer
                matching_pairs = []
                for i in range(min(len(items), len(matches))):
                    if items[i] and matches[i]:  # Only include non-empty pairs
                        matching_pairs.append({"item": items[i], "match": matches[i]})
                
                if not question_text or len(matching_pairs) < 2:
                    flash('Please provide a question and at least 2 matching pairs', 'error')
                    return render_template('admin/add_question.html')
                    
                options = []
                answer = json.dumps(matching_pairs)
                
                # Add drag-and-drop style flag to explanation if selected
                if drag_drop_style:
                    if '[TYPE:matching]' not in explanation:
                        explanation = '[TYPE:matching] [STYLE:drag_drop] ' + explanation
                    else:
                        explanation = explanation.replace('[TYPE:matching]', '[TYPE:matching] [STYLE:drag_drop]')
                
            elif question_type == 'essay':
                # For essay, store rubric and model answer
                rubric = request.form.get('rubric', '')
                model_answer = request.form.get('model_answer', '')
                
                if not question_text:
                    flash('Please provide an essay question', 'error')
                    return render_template('admin/add_question.html')
                    
                options = []
                # Store a placeholder answer since we need something for the NOT NULL constraint
                answer = "Essay question - see model answer"
            
            # Create the question
            new_question = Question(
                numb=numb,
                question=question_text,
                answer=answer,
                options=options,
                category=category
            )
            
            # Store question type in the explanation field if not already there
            if question_type != 'matching' or '[TYPE:' not in explanation:
                new_question.explanation = f"[TYPE:{question_type}] {explanation}"
            else:
                # For matching with drag-drop style, the explanation is already properly formatted
                new_question.explanation = explanation
            
            try:
                db.session.add(new_question)
                db.session.commit()
                flash('Question added successfully', 'success')
                return redirect(url_for('question.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding question: {str(e)}', 'error')
        
        return render_template('admin/add_question.html')

    @staticmethod
    @question_bp.route('/edit/<int:question_id>', methods=['GET', 'POST'])
    @login_required
    def edit_question(question_id):
        question = Question.query.get_or_404(question_id)
        
        if request.method == 'POST':
            question.numb = int(request.form.get('numb', 1))
            question.question = request.form.get('question')
            question.explanation = request.form.get('explanation', '')
            question.category = request.form.get('category', 'riddle')
            
            # Get question type
            question_type = request.form.get('question_type', 'multiple_choice')
            
            # Handle different question types and their answers
            if question_type == 'multiple_choice':
                # Get options from form for multiple choice
                options = []
                for i in range(4):
                    option = request.form.get(f'option{i+1}')
                    if option:
                        options.append(option)
                
                if len(options) < 2:
                    flash('Please provide at least 2 options for multiple choice questions', 'error')
                    return render_template('admin/edit_question.html', question=question)
                    
                question.options = options
                question.answer = request.form.get('answer')
                
            elif question_type == 'true_false':
                # For true/false, we only need the true/false answer
                question.options = ["True", "False"]
                question.answer = request.form.get('tf_answer')
                
                # Make sure we have a valid answer
                if not question.answer:
                    flash('Please select True or False for the answer', 'error')
                    return render_template('admin/edit_question.html', question=question)
                
            elif question_type == 'fill_blank':
                # For fill-in-the-blank, we store possible answers
                question.options = []
                question.answer = request.form.get('blank_answer')
                
                if not question.answer:
                    flash('Please provide at least one correct answer', 'error')
                    return render_template('admin/edit_question.html', question=question)
                
            elif question_type == 'short_answer':
                # For short answer, store the keywords or expected answer
                question.options = []
                question.answer = request.form.get('sa_answer')
                
                if not question.answer:
                    flash('Please provide answer keywords', 'error')
                    return render_template('admin/edit_question.html', question=question)
                
            elif question_type == 'matching':
                # For matching, store the matching pairs
                items = request.form.getlist('matching_item[]')
                matches = request.form.getlist('matching_match[]')
                
                # Check if drag-and-drop style is selected
                drag_drop_style = request.form.get('drag_drop_style')
                
                # Create matching pairs as JSON and store in answer
                matching_pairs = []
                for i in range(min(len(items), len(matches))):
                    if items[i] and matches[i]:  # Only include non-empty pairs
                        matching_pairs.append({"item": items[i], "match": matches[i]})
                
                if len(matching_pairs) < 2:
                    flash('Please provide at least 2 matching pairs', 'error')
                    return render_template('admin/edit_question.html', question=question)
                    
                question.options = []
                question.answer = json.dumps(matching_pairs)
                
                # Add or remove drag-and-drop style flag in the explanation field
                if drag_drop_style:
                    if '[TYPE:matching]' in question.explanation:
                        if '[STYLE:drag_drop]' not in question.explanation:
                            question.explanation = question.explanation.replace('[TYPE:matching]', '[TYPE:matching] [STYLE:drag_drop]')
                    else:
                        question.explanation = '[TYPE:matching] [STYLE:drag_drop] ' + question.explanation
                else:
                    # Remove drag-drop flag if it exists
                    if '[STYLE:drag_drop]' in question.explanation:
                        question.explanation = question.explanation.replace('[STYLE:drag_drop]', '').replace('  ', ' ')
                
            elif question_type == 'essay':
                # For essay, store rubric and model answer in options
                rubric = request.form.get('rubric', '')
                model_answer = request.form.get('model_answer', '')
                
                question.options = []
                # Store a placeholder answer since we need something for the NOT NULL constraint
                question.answer = "Essay question - see model answer"
            
            try:
                # Save the question type as part of the question metadata
                # Store the question type in the explanation field with a prefix
                if '[TYPE:' not in question.explanation:
                    question.explanation = f"[TYPE:{question_type}] {question.explanation}"
                else:
                    # Replace existing type tag if it's different from the current question type
                    current_type_match = question.explanation.find('[TYPE:')
                    if current_type_match >= 0:
                        end_type = question.explanation.find(']', current_type_match)
                        if end_type > current_type_match:
                            # Extract the current type
                            current_type = question.explanation[current_type_match+6:end_type]
                            if current_type != question_type:
                                # Replace the type tag
                                question.explanation = question.explanation.replace(
                                    question.explanation[current_type_match:end_type+1],
                                    f"[TYPE:{question_type}]"
                                )
                    else:
                        # No existing type tag found, add one
                        question.explanation = f"[TYPE:{question_type}] {question.explanation}"
                
                db.session.commit()
                flash('Question updated successfully', 'success')
                return redirect(url_for('question.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating question: {str(e)}', 'error')
        
        # Determine question type from explanation field
        question_type = 'multiple_choice'  # Default
        if question.explanation and '[TYPE:' in question.explanation:
            start_idx = question.explanation.find('[TYPE:') + 6
            end_idx = question.explanation.find(']', start_idx)
            if end_idx > start_idx:
                question_type = question.explanation[start_idx:end_idx]
                
        # Add question_type to question object for template
        question.question_type = question_type
        
        # Remove the type metadata from explanation for display
        clean_explanation = question.explanation
        if '[TYPE:' in clean_explanation:
            type_start = clean_explanation.find('[TYPE:')
            type_end = clean_explanation.find(']', type_start) + 1
            if type_end > type_start:
                # Remove the type tag and any leading space
                clean_explanation = clean_explanation[type_end:].lstrip()
                
        # Add clean explanation for template
        question.clean_explanation = clean_explanation
        
        return render_template('admin/edit_question.html', question=question)

    @staticmethod
    @question_bp.route('/delete/<int:question_id>', methods=['POST'])
    @login_required
    def delete_question(question_id):
        question = Question.query.get_or_404(question_id)
        
        try:
            db.session.delete(question)
            db.session.commit()
            flash('Question deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting question: {str(e)}', 'error')
        
        return redirect(url_for('question.index'))

    @staticmethod
    @question_bp.route('/api/questions')
    @login_required
    def get_questions_api():
        category = request.args.get('category', 'riddle')
        questions = Question.query.filter_by(category=category).order_by(Question.numb).all()
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'numb': q.numb,
                'question': q.question,
                'options': q.options,
                'answer': q.answer,
                'explanation': q.explanation
            })
        
        return jsonify(questions_data)

    @staticmethod
    @question_bp.route('/create_sample_blank_question')
    @login_required
    def create_sample_blank_question():
        """Create a sample fill-in-the-blank question for testing."""
        try:
            # Check if a similar question already exists
            existing = Question.query.filter_by(
                question="What protocol uses port 80 for web traffic?"
            ).first()
            
            if existing:
                flash('Sample fill-in-the-blank question already exists', 'info')
                return redirect(url_for('question.index'))
            
            # Create a new fill-in-the-blank question
            blank_question = Question(
                numb=100,  # Using high number to avoid conflicts
                question="What protocol uses port 80 for web traffic?",
                answer="HTTP",
                options=[],  # No options for fill-in-the-blank
                explanation="[TYPE:fill_blank] HTTP (Hypertext Transfer Protocol) uses port 80 by default.",
                category="riddle"
            )
            
            # Create another sample with multiple accepted answers
            blank_question2 = Question(
                numb=101,
                question="What is the default subnet mask for a Class C network?",
                answer="255.255.255.0",
                options=[],
                explanation="[TYPE:fill_blank] Class C networks use 255.255.255.0 or /24 as their default subnet mask.",
                category="riddle"
            )
            
            db.session.add(blank_question)
            db.session.add(blank_question2)
            db.session.commit()
            
            flash('Sample fill-in-the-blank questions created successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sample question: {str(e)}', 'error')
        
        return redirect(url_for('question.index'))

    @staticmethod
    @question_bp.route('/group_questions', methods=['POST'])
    @login_required
    def group_questions():
        """Add selected questions to a group from the questions page"""
        if request.method == 'POST':
            question_ids = request.form.getlist('question_ids')
            group_id = request.form.get('group_id')
            
            if not question_ids:
                flash('No questions selected', 'error')
                return redirect(url_for('question.index'))
                
            if not group_id:
                flash('Please select a group', 'error')
                return redirect(url_for('question.index'))
            
            try:
                group = QuestionGroup.query.get_or_404(int(group_id))
                selected_questions = Question.query.filter(Question.id.in_(question_ids)).all()
                
                for question in selected_questions:
                    if question not in group.questions:
                        group.questions.append(question)
                
                db.session.commit()
                flash(f'Added {len(selected_questions)} question(s) to "{group.name}" group', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding questions to group: {str(e)}', 'error')
            
        return redirect(url_for('question.index'))
        
    @staticmethod
    @question_bp.route('/list_ungrouped', methods=['GET'])
    @login_required
    def list_ungrouped():
        """Display ungrouped questions with options to add them to groups"""
        # Get all question groups for selection
        groups = QuestionGroup.query.order_by(QuestionGroup.name).all()
        
        # Check if we need to create a new group
        if len(groups) == 0:
            flash('You need to create at least one question group first', 'warning')
            return redirect(url_for('question_group.add_group'))
        
        # Get all ungrouped questions
        grouped_question_ids = []
        for group in groups:
            for question in group.questions:
                grouped_question_ids.append(question.id)
                
        ungrouped_questions = Question.query.filter(~Question.id.in_(grouped_question_ids)).all() if grouped_question_ids else Question.query.all()
        
        # Group by category for better organization
        categorized_questions = {}
        for question in ungrouped_questions:
            if question.category not in categorized_questions:
                categorized_questions[question.category] = []
            categorized_questions[question.category].append(question)
        
        # Instead of using a separate template, redirect to the main questions page with a flag to open the modal
        return redirect(url_for('question.index', show_ungrouped_modal=True))

    @staticmethod
    @question_bp.route('/get_groups', methods=['GET'])
    @login_required
    def get_groups():
        """API endpoint to get all question groups for the grouping modal"""
        try:
            groups = QuestionGroup.query.order_by(QuestionGroup.name).all()
            groups_data = [{'id': group.id, 'name': group.name} for group in groups]
            return jsonify({'success': True, 'groups': groups_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    @question_bp.route('/api/group_questions', methods=['POST'])
    @login_required
    def group_questions_api():
        """Handle grouping questions from the modal dialog"""
        try:
            question_ids = json.loads(request.form.get('question_ids', '[]'))
            action = request.form.get('action')
            
            if not question_ids:
                return jsonify({'success': False, 'error': 'No questions selected'}), 400
            
            # Get the selected questions
            questions = Question.query.filter(Question.id.in_(question_ids)).all()
            
            if action == 'create':
                # Create a new group
                group_name = request.form.get('group_name')
                group_description = request.form.get('group_description', '')
                
                if not group_name:
                    return jsonify({'success': False, 'error': 'Group name is required'}), 400
                
                new_group = QuestionGroup(
                    name=group_name,
                    description=group_description
                )
                
                db.session.add(new_group)
                db.session.flush()  # Get the ID without committing
                
                # Add questions to the new group
                for question in questions:
                    new_group.questions.append(question)
                
                db.session.commit()
                return jsonify({
                    'success': True, 
                    'message': f'Created group "{group_name}" with {len(questions)} question(s)',
                    'group_id': new_group.id
                })
                
            elif action == 'add':
                # Add to existing group
                group_id = request.form.get('group_id')
                
                if not group_id:
                    return jsonify({'success': False, 'error': 'Group ID is required'}), 400
                
                group = QuestionGroup.query.get(group_id)
                
                if not group:
                    return jsonify({'success': False, 'error': 'Group not found'}), 404
                
                # Add questions to the existing group
                added_count = 0
                for question in questions:
                    if question not in group.questions:
                        group.questions.append(question)
                        added_count += 1
                
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Added {added_count} question(s) to "{group.name}"'
                })
                
            else:
                return jsonify({'success': False, 'error': 'Invalid action'}), 400
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    @question_bp.route('/get/<int:question_id>', methods=['GET'])
    @login_required
    def get_question(question_id):
        """API endpoint to get question data for editing in the modal"""
        try:
            question = Question.query.get_or_404(question_id)
            
            # Extract question type from explanation field
            question_type = 'multiple_choice'  # Default
            if question.explanation and '[TYPE:' in question.explanation:
                type_start = question.explanation.find('[TYPE:') + 6
                type_end = question.explanation.find(']', type_start)
                if type_end > type_start:
                    question_type = question.explanation[type_start:type_end]
            
            # Prepare explanation without the type tag for display
            clean_explanation = question.explanation
            if '[TYPE:' in clean_explanation:
                type_start = clean_explanation.find('[TYPE:')
                type_end = clean_explanation.find(']', type_start) + 1
                if type_end > type_start:
                    # Remove the type tag and any leading space
                    clean_explanation = clean_explanation[type_end:].lstrip()
                    
            # Parse matching question data if necessary
            matching_pairs = []
            if question_type == 'matching' and question.answer:
                try:
                    matching_pairs = json.loads(question.answer)
                except:
                    pass
            
            return jsonify({
                'success': True,
                'question': {
                    'id': question.id,
                    'numb': question.numb,
                    'question': question.question,
                    'options': question.options,
                    'answer': question.answer,
                    'explanation': clean_explanation,
                    'category': question.category,
                    'question_type': question_type,
                    'matching_pairs': matching_pairs
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    @question_bp.route('/api/ungrouped', methods=['GET'])
    @login_required
    def get_ungrouped_questions_api():
        """API endpoint to get ungrouped questions for the group modal"""
        try:
            category = request.args.get('category', 'all')
            
            # Get all question groups for selection
            groups = QuestionGroup.query.all()
            
            # Get all ungrouped questions
            grouped_question_ids = []
            for group in groups:
                for question in group.questions:
                    grouped_question_ids.append(question.id)
            
            # Build the query
            query = Question.query
            
            # Apply category filter if not 'all'
            if category != 'all':
                query = query.filter_by(category=category)
            
            # Filter out questions that are already in groups
            if grouped_question_ids:
                query = query.filter(~Question.id.in_(grouped_question_ids))
                
            # Get the results
            questions = query.order_by(Question.numb).all()
            
            # Format for response
            questions_data = []
            for q in questions:
                # Extract question type for display
                question_type = 'Multiple Choice'  # Default
                if q.explanation and '[TYPE:' in q.explanation:
                    type_start = q.explanation.find('[TYPE:') + 6
                    type_end = q.explanation.find(']', type_start)
                    if type_end > type_start:
                        question_type = q.explanation[type_start:type_end].replace('_', ' ').title()
                        
                questions_data.append({
                    'id': q.id,
                    'question': q.question[:60] + ('...' if len(q.question) > 60 else ''),
                    'category': q.category,
                    'type': question_type
                })
                
            return jsonify({'success': True, 'questions': questions_data})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    def get_questions_by_category(self, category):
        """Get questions by category"""
        try:
            questions = Question.query.filter_by(category=category).order_by(Question.numb).all()
            return questions
        except Exception as e:
            print(f"Error fetching questions by category: {str(e)}")
            return []
    
    def get_all_questions(self):
        """Get all questions"""
        try:
            questions = Question.query.order_by(Question.numb).all()
            return questions
        except Exception as e:
            print(f"Error fetching all questions: {str(e)}")
            return []
            
    def get_question_by_id(self, question_id):
        """Get a question by ID"""
        try:
            question = Question.query.get(question_id)
            return question
        except Exception as e:
            print(f"Error fetching question by ID: {str(e)}")
            return None
