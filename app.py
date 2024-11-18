from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'your_secret_key'  
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)
    profile_img = db.Column(db.String(150), nullable=True)  # Add this line


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

# Score model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Score {self.score} on {self.date_attempted}>"

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please choose another.')
            return redirect(url_for('signup'))

        # Create a new user
        new_user = User(username=username)
        new_user.set_password(password)  # Hash and store password
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.')
        return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # Verify the password
        if user and user.check_password(password):
            session['user_id'] = user.id  # Store user id in session
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

    return render_template('index.html')  # Your login HTML form

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        flash('You need to log in first!')
        return redirect(url_for('login'))

    user_id = session['user_id']
    score = request.form['score']  # Assuming score is passed from the quiz logic

    new_score = Score(score=score, user_id=user_id)
    db.session.add(new_score)
    db.session.commit()

    flash('Quiz score saved!')
    return redirect(url_for('dashboard'))  # Redirect to the dashboard

@app.route('/save_score', methods=['POST'])
def save_score():
    if 'user_id' not in session:
        print("User not logged in")
        return jsonify({"status": "error", "message": "User not logged in."}), 403
    
    data = request.get_json()  # Get JSON data from the request
    score = data.get('score')  # Extract the score from the JSON

    print(f"Received score: {score} for user_id: {session['user_id']}")  # Log received score

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

@app.route('/dashboard')
def dashboard():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first!')
        return redirect(url_for('login'))

    # Get the current logged-in user
    user = User.query.get(session['user_id'])

    # Fetch all the scores of the current user
    user_scores = Score.query.filter_by(user_id=user.id).all()

    # Get the leaderboard data
    leaderboard_data = (
        db.session.query(
            User.username, 
            func.max(Score.score).label('highest_score'), 
            func.max(Score.date_attempted).label('latest_attempt')
        )
        .join(Score)
        .group_by(User.id)
        .order_by(func.max(Score.score).desc())
        .all()
    )

    # Pass the user, their scores, and the leaderboard data to the template
    return render_template('dashboard.html', user=user, scores=user_scores, leaderboard=leaderboard_data)

@app.route('/leaderboard')
def leaderboard():
    try:
        leaderboard_data = (
            db.session.query(User.username, func.max(Score.score).label('highest_score'), func.max(Score.date_attempted).label('latest_attempt'))
            .join(Score)
            .group_by(User.id)
            .order_by(func.max(Score.score).desc())
            .all()
        )
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        leaderboard_data = []

    return render_template('dashboard.html', leaderboard=leaderboard_data)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash('You need to log in first!')
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    profile_img = request.files.get('profile_img')

    # Fetch the current user from the session
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Update username and password if provided
    user.username = username
    if password:
        user.set_password(password)
    if profile_img:
        img_filename = secure_filename(profile_img.filename)
        profile_img.save(os.path.join('static/img', img_filename))
        user.profile_img = f'img/{img_filename}'
    
    db.session.commit()

    flash('Profile updated successfully.')
    return redirect(url_for('dashboard'))
@app.route('/delete_score/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    score = Score.query.get(score_id)
    db.session.delete(score)
    db.session.commit()
    flash('Score deleted successfully.')
    return redirect(url_for('dashboard'))


@app.route('/topology')
def topology():
    return render_template('topology.html', title="topology")

@app.route('/guide')
def guide():
    return render_template('guide.html', title="guide")

@app.route('/crimp')
def crimp():
    return render_template('crimping-simulation.html', title="crimp")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
