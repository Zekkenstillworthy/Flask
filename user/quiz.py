from flask import render_template, request, redirect, url_for, session, jsonify
from user.models import Score, Question, EssayResponse, User  # Direct imports from user.models
from __init__ import db  # Import db from main app

class QuizController:
    def __init__(self, app):
        self.app = app
        self.register_routes()

    def register_routes(self):
        """Register all quiz-related routes"""
        # Quiz submission routes
        self.app.route('/submit_quiz', methods=['POST'])(self.submit_quiz)
        self.app.route('/save_score', methods=['POST'])(self.save_score)
        self.app.route('/save_topology_score', methods=['POST'])(self.save_topology_score)
        self.app.route('/save_crimping_score', methods=['POST'])(self.save_crimping_score)
        self.app.route('/save_troubleshoot_score', methods=['POST'])(self.save_troubleshoot_score)
        
        # Make sure we register both the direct and API routes for essay submission
        self.app.route('/save_essay', methods=['POST'])(self.save_essay)
        
        # Note: We're not registering the API version here since it should come from the API blueprint
        # This avoids conflicts with the blueprint registration
        
        self.app.route('/delete_score/<int:score_id>', methods=['POST'])(self.delete_score)
        
        # Quiz data routes - register both with and without API prefix for fallback
        self.app.route('/questions')(self.get_questions)
        
        # Quiz view routes
        self.app.route('/topology', methods=['GET', 'POST'])(self.topology)
        self.app.route('/troubleshoot', methods=['GET', 'POST'])(self.troubleshoot)
        self.app.route('/crimp', methods=['GET', 'POST'])(self.crimp)

    def submit_quiz(self):
        if 'user_id' not in session:
            return render_template('user/index.html', message='You need to log in first!')

        user_id = session['user_id']
        score = request.form['score']

        new_score = Score(score=score, user_id=user_id)
        db.session.add(new_score)
        db.session.commit()

        return redirect(url_for('dashboard'))

    def save_score(self):
        if 'user_id' not in session:
            print("User not logged in")
            return jsonify({"status": "error", "message": "User not logged in."}), 403
        
        data = request.get_json()
        score = data.get('score')

        print(f"Received score: {score} for user_id: {session['user_id']}")

        if score is not None:
            try:
                new_score = Score(score=score, user_id=session['user_id'])
                db.session.add(new_score)
                db.session.commit()
                print(f"Score {score} saved successfully for user {session['user_id']}")
                return jsonify({"status": "success"}), 200
            except Exception as e:
                print(f"Error saving score: {e}")
                return jsonify({"status": "error", "message": "Database error"}), 500
        else:
            print("Invalid score received")
            return jsonify({"status": "error", "message": "Invalid score"}), 400

    def _save_category_score(self, category):
        """Internal helper method to save a score for a specific category"""
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "User not logged in."}), 403
        
        data = request.get_json()
        score = data.get('score')
        category_name = data.get('category', category)

        if score is not None:
            try:
                new_score = Score(score=score, user_id=session['user_id'], category=category_name)
                db.session.add(new_score)
                db.session.commit()
                return jsonify({"status": "success"}), 200
            except Exception as e:
                return jsonify({"status": "error", "message": "Database error"}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid score"}), 400

    def save_topology_score(self):
        return self._save_category_score('topology')

    def save_crimping_score(self):
        return self._save_category_score('crimping')

    def save_troubleshoot_score(self):
        return self._save_category_score('troubleshoot')

    def get_questions(self):
        category = request.args.get('category', 'riddle')
        
        try:
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
        except Exception as e:
            print(f"Error fetching questions: {str(e)}")
            return jsonify([])

    def save_essay(self):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "User not logged in."}), 403
        
        data = request.get_json()
        question_text = data.get('question')
        question_id = data.get('questionId')
        response_text = data.get('answer')
        category = data.get('category', 'riddle')
        
        if not response_text or not question_text:
            return jsonify({"status": "error", "message": "Missing question or response"}), 400
        
        try:
            new_response = EssayResponse(
                user_id=session['user_id'],
                question_id=question_id,
                question_text=question_text,
                response_text=response_text,
                category=category
            )
            db.session.add(new_response)
            db.session.commit()
            
            print(f"Essay saved successfully for user {session['user_id']}, category: {category}")
            return jsonify({"status": "success", "message": "Essay submitted for review"}), 200
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"Error saving essay: {str(e)}")
            traceback.print_exc()
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    def delete_score(self, score_id):
        # Import locally to avoid circular imports
        from user.models import Score as UserScore
        score = UserScore.query.get(score_id)
        db.session.delete(score)
        db.session.commit()
        return redirect(url_for('dashboard'))

    def topology(self):
        if request.method == 'POST':
            # Handle any POST data here if needed
            data = request.get_json() if request.is_json else request.form
            return jsonify({"status": "success"}), 200
        # For GET requests, render the template
        return render_template('user/topology.html', title="topology")

    def troubleshoot(self):
        if request.method == 'POST':
            # Handle any POST data here if needed
            data = request.get_json() if request.is_json else request.form
            return jsonify({"status": "success"}), 200
        # For GET requests, render the template
        return render_template('user/troubleshoot.html', title="troubleshoot")

    def crimp(self):
        if request.method == 'POST':
            # Handle any POST data here if needed
            data = request.get_json() if request.is_json else request.form
            return jsonify({"status": "success"}), 200
        # For GET requests, render the template
        return render_template('user/crimping-simulation.html', title="crimp")