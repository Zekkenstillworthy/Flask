from flask import render_template, session, Blueprint, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
import os
import time  # Add the missing time module import
from werkzeug.utils import secure_filename
from .models import db, User, Score, Topology
from flask_login import login_required, current_user

# Create blueprint as expected by main __init__.py
user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    return render_template('user/index.html')

@user_bp.route('/overview')
def overview():
    return render_template('user/overview.html')

@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')

    user = User.query.get(session['user_id'])
    user_score = Score.query.filter_by(user_id=user.id).all()

    # Overall leaderboard data
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

    # Category-specific leaderboards
    categories = ['topology', 'crimping', 'troubleshoot', 'riddle']
    category_leaderboards = {}
    
    for category in categories:
        category_leaderboards[f"{category}_leaderboard"] = (
            db.session.query(
                User.username, 
                func.max(Score.score).label('highest_score'), 
                func.max(Score.date_attempted).label('latest_attempt')
            )
            .join(Score)
            .filter(Score.category == category)
            .group_by(User.id)
            .order_by(func.max(Score.score).desc())
            .all()
        )

    return render_template(
        'user/dashboard.html', 
        user=user, 
        score=user_score, 
        leaderboard=leaderboard_data,
        **category_leaderboards
    )

@user_bp.route('/leaderboard')
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

    return render_template('user/dashboard.html', leaderboard=leaderboard_data)

@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')

    user = User.query.get(session['user_id'])
    username = request.form['username']
    password = request.form['password']
    profile_img = request.files.get('profile_img')

    user.username = username
    if password:
        user.set_password(password)
    if profile_img and profile_img.filename:
        img_filename = secure_filename(profile_img.filename)
        profile_img.save(os.path.join('static/img', img_filename))
        user.profile_img = f'img/{img_filename}'

    db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/delete_score/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    if 'user_id' not in session:
        return render_template('user/index.html', message='You need to log in first!')
        
    score = Score.query.get(score_id)
    if score and score.user_id == session['user_id']:
        db.session.delete(score)
        db.session.commit()
    return redirect(url_for('user.dashboard'))

@user_bp.route('/troubleshoot')
def troubleshoot():
    return render_template('user/troubleshoot.html', title="troubleshoot")

@user_bp.route('/crimp')
def crimp():
    return render_template('user/crimping-simulation.html', title="crimp")

@user_bp.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('user.index'))

@user_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    otp = request.form.get('otp')
    
    # Find the user by username
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return render_template('user/index.html', message='Invalid username.')
    
    # Validate password
    if not user.check_password(password):
        return render_template('user/index.html', message='Invalid password.')
    
    # Validate OTP if TOTP is enabled for this user
    if user.totp_enabled:
        if not otp:
            return render_template('user/index.html', message='OTP is required for this account.')
        
        try:
            import pyotp
            totp = pyotp.TOTP(user.totp_secret)
            
            # Check with a larger window of validity to account for time drift
            # This adds a window of 30 seconds before and after the current time
            if not totp.verify(otp, valid_window=1):
                # Try with an even larger window if the first attempt fails
                if not totp.verify(otp, valid_window=2):
                    return render_template('user/index.html', message='Invalid OTP code. Please make sure your device time is synchronized.')
        except Exception as e:
            print(f"Error validating OTP: {str(e)}")
            return render_template('user/index.html', message='Error validating OTP. Please try again.')
    
    # Set user in session
    session['user_id'] = user.id
    
    # Redirect to dashboard on successful login
    return redirect(url_for('user.dashboard'))

@user_bp.route('/signup', methods=['POST'])
def signup():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'status': 'error', 'message': 'Username already exists. Please choose another one.'}, 400
        
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return {'status': 'success', 'message': 'Account created successfully!'}, 201
    else:
        # Handle regular form submission
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('user/index.html', message='Username already exists. Please choose another one.')
        
        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('user.index', message='Account created successfully! Please log in.'))

@user_bp.route('/generate_qr', methods=['POST'])
def generate_qr():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = request.get_json()
            username = data.get('username')
            
            if not username:
                return {'status': 'error', 'message': 'Username is required'}, 400
            
            # Find the user in the database
            user = User.query.filter_by(username=username).first()
            if not user:
                return {'status': 'error', 'message': 'User not found'}, 404
            
            # Generate a random secret key for TOTP
            import pyotp
            import qrcode
            import os
            from io import BytesIO
            import base64
            
            # Generate a new TOTP secret
            totp_secret = pyotp.random_base32()
            
            # Update the user's TOTP secret in the database
            user.totp_secret = totp_secret
            user.totp_enabled = True  # Enable TOTP for this user
            db.session.commit()
            
            # Create the provisioning URI for the QR code
            totp = pyotp.TOTP(totp_secret)
            provisioning_uri = totp.provisioning_uri(username, issuer_name="RiddleNet")
            
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save the QR code to a file
            qr_code_dir = os.path.join('static', 'qrcodes')
            os.makedirs(qr_code_dir, exist_ok=True)
            
            qr_code_filename = f"qr_{username}_{int(time.time())}.png"
            qr_code_path = os.path.join(qr_code_dir, qr_code_filename)
            
            img.save(qr_code_path)
            
            # Return the path to the QR code image
            web_path = os.path.join('static', 'qrcodes', qr_code_filename).replace('\\', '/')
            
            return {'status': 'success', 'message': 'QR code generated', 'qr_code_path': web_path}, 200
            
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return {'status': 'error', 'message': 'Failed to generate QR code'}, 500
    else:
        return {'status': 'error', 'message': 'This endpoint only accepts AJAX requests'}, 400

@user_bp.route('/topology')
@login_required
def topology():
    """Render the topology page."""
    return render_template('user/topology.html')

@user_bp.route('/topology/challenges')
@login_required
def get_topology_challenges():
    """Get all active topology challenges"""
    topologies = Topology.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': topology.id,
        'title': topology.title,
        'description': topology.description,
        'difficulty': topology.difficulty,
        'topology_type': topology.topology_type,
        'base_score': topology.base_score
    } for topology in topologies]), 200

@user_bp.route('/topology/challenge/<int:topology_id>')
@login_required
def get_topology_challenge(topology_id):
    """Get a specific topology challenge by ID"""
    topology = Topology.query.get_or_404(topology_id)
    
    return jsonify({
        'id': topology.id,
        'title': topology.title,
        'description': topology.description,
        'difficulty': topology.difficulty,
        'topology_type': topology.topology_type,
        'initial_config': topology.get_initial_config(),
        'base_score': topology.base_score,
        'time_bonus': topology.time_bonus,
        'perfect_match_bonus': topology.perfect_match_bonus
    }), 200

@user_bp.route('/topology/completed')
@login_required
def get_completed_topologies():
    """Get IDs of topology challenges completed by the current user"""
    user_id = current_user.id
    
    # Query the Score table for completed topology challenges
    completed_score = Score.query.filter_by(
        user_id=user_id,
        category='topology'
    ).all()
    
    # Since topic_id doesn't exist, we'll return empty list for now
    # This can be updated later if you add a way to track completed topologies
    completed_ids = []
    
    return jsonify({'completed': completed_ids}), 200

@user_bp.route('/save_topology_score', methods=['POST'])
@login_required
def save_topology_score():
    """Save a topology score for the current user"""
    data = request.json
    user_id = current_user.id
    
    if not data or 'score' not in data or 'category' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # Create a new score record
    new_score = Score(
        user_id=user_id,
        score=data['score'],
        category=data['category']
        # topic_id field removed as it doesn't exist in the database
    )
    
    db.session.add(new_score)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Score saved successfully'}), 200
