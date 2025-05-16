from functools import wraps
from flask import session, redirect, url_for, flash, request
from flask_login import current_user

def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check both Flask-Login and session
        if not current_user.is_authenticated or 'user_id' not in session:
            # Save the requested URL for redirecting after login
            next_url = request.url
            flash('You need to log in first!', 'error')
            return redirect(url_for('user.login', next=next_url))
        return f(*args, **kwargs)
    return decorated_function
