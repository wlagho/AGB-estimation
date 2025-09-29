# Main Application Routes

from flask import Blueprint, render_template, redirect, url_for
from backend.app.auth.utils import login_required, get_current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Public landing page"""
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard (role-based)"""
    user = get_current_user()
    return render_template('auth/dashboard.html', user=user)

@main.route('/demo')
def demo():
    """Public demo page (limited functionality)"""
    return render_template('demo.html')