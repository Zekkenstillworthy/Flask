from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime
import pyotp
import qrcode
import os
from ..app import db
from ..models.user import User, Admin
from ..models.score import Score
from ..models.essay_response import EssayResponse

user_bp = Blueprint('user', __name__, url_prefix='/users')

class UserController:
    @staticmethod
    @user_bp.route('/')
    def index():
        # Get regular users with their stats
        users = User.query.all()
        user_stats = []
        for user in users:
            scores_count = Score.query.filter_by(user_id=user.id).count()
            highest_score = db.session.query(func.max(Score.score)).filter_by(user_id=user.id).scalar() or 0
            
            user_stats.append({
                'user': user,
                'scores_count': scores_count,
                'highest_score': highest_score
            })
        
        # Get admin users
        admins = Admin.query.all()
        
        return render_template('admin/user_management.html', 
                            user_stats=user_stats, 
                            admins=admins,
                            active_page='users')

    @staticmethod
    @user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email', '')
            password = request.form.get('password')
            status = request.form.get('status', 'active')
            is_admin = request.form.get('is_admin') == 'true'
            
            # Update user fields
            user.username = username
            user.email = email
            user.status = status
            user.is_admin = is_admin
            
            # Only update password if a new one is provided
            if password:
                user.set_password(password)
            
            try:
                db.session.commit()
                flash('User updated successfully', 'success')
                return redirect(url_for('user.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating user: {str(e)}', 'error')
        
        return render_template('admin/edit_user.html', user=user, active_page='users')

    @staticmethod
    @user_bp.route('/delete/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        
        # Check if the user is an admin and if they're the only admin
        if user.is_admin and User.query.filter_by(is_admin=True).count() <= 1:
            flash('Cannot delete the only admin user in the system', 'error')
            return redirect(url_for('user.index'))
        
        try:
            # Delete related scores first
            Score.query.filter_by(user_id=user.id).delete()
            
            # Handle essay responses - either delete them or handle differently
            from admin.models.essay import EssayResponse
            # Option 1: Delete associated essay responses (preferred approach)
            essay_responses = EssayResponse.query.filter_by(user_id=user.id).all()
            for essay in essay_responses:
                db.session.delete(essay)
            
            # Option 2 (alternative): Set essay user_id to null if NOT NULL constraint is removed
            # EssayResponse.query.filter_by(user_id=user.id).update({EssayResponse.user_id: None})
            
            # Now delete the user
            db.session.delete(user)
            db.session.commit()
            flash('User and all related data deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting user: {str(e)}', 'error')
        
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/admins/edit/<int:admin_id>', methods=['GET', 'POST'])
    def edit_admin(admin_id):
        admin = Admin.query.get_or_404(admin_id)
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email', '')
            password = request.form.get('password')
            role = request.form.get('role', 'admin')
            
            admin.username = username
            admin.email = email
            admin.role = role
            if password:
                admin.password_hash = generate_password_hash(password)
            
            try:
                db.session.commit()
                flash('Admin updated successfully', 'success')
                return redirect(url_for('user.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating admin: {str(e)}', 'error')
        
        return render_template('admin/edit_admin.html', admin=admin, active_page='users')

    @staticmethod
    @user_bp.route('/admins/delete/<int:admin_id>', methods=['POST'])
    def delete_admin(admin_id):
        admin = Admin.query.get_or_404(admin_id)
        
        # Prevent deleting the last admin
        if Admin.query.count() <= 1:
            flash('Cannot delete the last admin account', 'error')
            return redirect(url_for('user.index'))
        
        try:
            db.session.delete(admin)
            db.session.commit()
            flash('Admin deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting admin: {str(e)}', 'error')
        
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/admins/add', methods=['GET', 'POST'])
    def add_admin():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            email = request.form.get('email', '')
            role = request.form.get('role', 'admin')
            
            # Validate inputs
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('user.index'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('user.index'))
            
            # Check if username already exists
            existing_admin = Admin.query.filter_by(username=username).first()
            if existing_admin:
                flash('Username already exists', 'error')
                return redirect(url_for('user.index'))
            
            # Create new admin user
            new_admin = Admin(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                role=role,
                created_at=datetime.utcnow()
            )
            
            try:
                db.session.add(new_admin)
                db.session.commit()
                flash(f'Admin user "{username}" created successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating admin: {str(e)}', 'error')
            
            return redirect(url_for('user.index'))
        
        # For GET requests, redirect to user management page
        # No need for a separate add_admin.html page anymore
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/reset-user-password/<int:user_id>', methods=['POST'])
    def reset_user_password(user_id):
        user = User.query.get_or_404(user_id)
        # Logic to reset password - this would generate a random password or trigger a reset email
        flash(f'Password reset for {user.username}', 'success')
        return redirect(url_for('dashboard.index'))

    @staticmethod
    @user_bp.route('/add', methods=['POST'])
    def add_user():
        """Add a regular user"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            status = request.form.get('status', 'active')
            
            # Validate input
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('user.index'))
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'error')
                return redirect(url_for('user.index'))
            
            # Create new user
            try:
                new_user = User(
                    username=username,
                    email=email,
                    status=status,
                    created_at=datetime.utcnow()
                )
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash(f'User {username} has been created successfully', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating user: {str(e)}', 'error')
            
            return redirect(url_for('user.index'))
        
        # For GET requests, just redirect to the user management page
        return redirect(url_for('user.index'))

    @staticmethod
    @user_bp.route('/generate_totp/<int:user_id>', methods=['POST'])
    def generate_totp(user_id):
        """Generate a new TOTP key for a user"""
        user = User.query.get_or_404(user_id)
        
        # Generate a new random TOTP key
        key = pyotp.random_base32()
        totp = pyotp.TOTP(key)
        uri = totp.provisioning_uri(name=f"{user.id}_{user.username}", issuer_name="RiddleNet")
        
        # Ensure directory exists
        qr_dir = os.path.join('static', 'img', 'img_qr')
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
            
        # Generate QR code
        qr_code_path = f"static/img/img_qr/{user.id}_totp.png"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join('static', 'img', 'img_qr', f"{user.id}_totp.png"))
        
        # Save the key to the user
        user.totp_key = key
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "TOTP enabled successfully",
            "totp_key": key,
            "qr_code_path": qr_code_path
        })
    
    @staticmethod
    @user_bp.route('/disable_totp/<int:user_id>', methods=['POST'])
    def disable_totp(user_id):
        """Disable TOTP for a user"""
        user = User.query.get_or_404(user_id)
        
        # Remove TOTP key
        user.totp_key = None
        db.session.commit()
        
        # Delete QR code image if it exists
        qr_path = os.path.join('static', 'img', 'img_qr', f"{user.id}_totp.png")
        if os.path.exists(qr_path):
            os.remove(qr_path)
            
        return jsonify({
            "status": "success",
            "message": "TOTP disabled successfully"
        })
        
    @staticmethod
    @user_bp.route('/get_totp_info/<int:user_id>')
    def get_totp_info(user_id):
        """Get TOTP information for a user"""
        user = User.query.get_or_404(user_id)
        
        totp_data = {
            "has_totp": user.totp_key is not None,
            "totp_key": user.totp_key if user.totp_key else None,
        }
        
        # Add QR code path if TOTP is enabled
        if user.totp_key:
            qr_path = f"/static/img/img_qr/{user.id}_totp.png"
            totp_data["qr_code_path"] = qr_path
            
        return jsonify(totp_data)

    @staticmethod
    @user_bp.route('/essay-responses')
    def user_essays():
        """Display users with option to view their essay responses"""
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get all users with pagination
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/user_responses.html', 
                            users=users,
                            active_page='users')
    
    @staticmethod
    @user_bp.route('/api/<int:user_id>/essays')
    def get_user_essays(user_id):
        """API endpoint to get all essays for a specific user"""
        user = User.query.get_or_404(user_id)
        essays = EssayResponse.query.filter_by(user_id=user_id).order_by(EssayResponse.submission_date.desc()).all()
        
        # Format essay data for JSON response
        essays_data = []
        for essay in essays:
            essays_data.append({
                'id': essay.id,
                'question': essay.question,
                'answer': essay.answer,
                'category': essay.category,
                'submission_date': essay.submission_date.strftime('%Y-%m-%d %H:%M') if essay.submission_date else 'N/A',
                'is_graded': essay.is_graded,
                'graded_score': essay.graded_score
            })
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'essays': essays_data
        })
