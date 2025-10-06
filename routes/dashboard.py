from flask import Blueprint, render_template, session
from utils.decorators import login_required, two_factor_verified, role_required
from models.user import User

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@two_factor_verified
def index():
    user = User.get_by_id(session['user_id'])

    dashboard_data = {
        'user': user,
        'role': user.role,
        'user_name': session.get('user_name'),
        'email': user.email
    }

    if user.role == 'researcher':
        return render_template('dashboard/researcher.html', **dashboard_data)
    elif user.role == 'project_developer':
        return render_template('dashboard/project_developer.html', **dashboard_data)
    elif user.role == 'admin':
        users = User.get_all_users()
        dashboard_data['users'] = users
        return render_template('dashboard/admin.html', **dashboard_data)

    return render_template('dashboard/base.html', **dashboard_data)

@dashboard_bp.route('/profile')
@login_required
@two_factor_verified
def profile():
    user = User.get_by_id(session['user_id'])
    return render_template('dashboard/profile.html', user=user)

@dashboard_bp.route('/admin/users')
@login_required
@two_factor_verified
@role_required('admin')
def admin_users():
    users = User.get_all_users()
    return render_template('dashboard/admin_users.html', users=users)
