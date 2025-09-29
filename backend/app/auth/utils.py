# Authentication Utilities

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify
from backend.app.models.user import User, UserRole
import secrets
import string

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'info')
                return redirect(url_for('auth.login', next=request.url))
            
            user = User.query.get(session['user_id'])
            if not user or user.role not in allowed_roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get currently logged in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def generate_secure_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def login_user(user, remember=False):
    """Log in a user by setting session data"""
    session['user_id'] = user.id
    session['user_role'] = user.role.value
    session['user_email'] = user.email
    
    if remember:
        session.permanent = True

def logout_user():
    """Log out user by clearing session"""
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_email', None)
