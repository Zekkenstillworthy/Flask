from flask import redirect, url_for, flash, request, session
from flask_login import current_user
from functools import wraps

def admin_login_required(f):
    """
    Custom decorator to check if the user is authenticated as an admin.
    If not, redirects to the admin login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            flash('Please log in to access the admin area', 'warning')
            next_url = request.url  # Save the URL the user was trying to access
            return redirect(url_for('auth.login', next=next_url))
        
        # Check if user is an admin (additional check if needed)
        # Assuming admin users have an 'is_admin' attribute or similar
        if hasattr(current_user, 'is_admin') and not current_user.is_admin:
            flash('You do not have permission to access this area', 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def protect_admin_routes(app):
    """
    Add a before_request handler to protect all admin routes.
    This should be called during application setup.
    """
    @app.before_request
    def check_admin_auth():
        # List of routes that don't require authentication (login/static files)
        exempt_routes = [
            '/static/', 
            '/admin/login',
            '/admin/auth/login',
            '/admin/logout',
            '/admin/auth/logout'
        ]
        
        # Skip check for exempt routes
        if any(request.path.startswith(route) for route in exempt_routes):
            return None
            
        # Check if user is authenticated
        if not current_user.is_authenticated:
            if request.path.startswith('/admin'):
                flash('Please log in to access the admin area', 'warning')
                return redirect(url_for('auth.login', next=request.url))