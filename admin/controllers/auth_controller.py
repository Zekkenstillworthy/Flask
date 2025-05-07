from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from admin.app import db
from admin.models.user import Admin

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @staticmethod
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        # Check if admin is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Debug logging
            print(f"Login attempt for username: {username}")
            
            # Try to find the user in the Admin table
            admin = Admin.query.filter_by(username=username).first()
            
            if admin and admin.check_password(password):
                # Use Flask-Login to log in the user with remember=True
                login_user(admin, remember=True)
                # Update last login
                admin.last_login = datetime.utcnow()
                db.session.commit()
                
                # Debug logging
                print(f"Login successful: {admin.username}, ID: {admin.id}, is_authenticated: {current_user.is_authenticated}")
                
                flash('Welcome to Admin Dashboard', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid admin credentials', 'error')
        
        return render_template('admin/login.html')

    @staticmethod
    @auth_bp.route('/logout')
    @login_required
    def logout():
        logout_user()  # Use Flask-Login's logout_user
        flash('Logged out successfully', 'success')
        return redirect(url_for('auth.login'))

# Add a context processor to help with URL generation
@auth_bp.context_processor
def inject_url_prefix():
    """
    This function helps the templates determine whether to use 'admin.' prefix
    for URLs depending on whether we're using the standalone admin app or the
    integrated blueprint.
    """
    def get_url_prefix():
        return ''  # No prefix for standalone app
        
    return dict(url_prefix=get_url_prefix)
