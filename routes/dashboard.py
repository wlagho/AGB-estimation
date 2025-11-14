from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from utils.decorators import login_required, two_factor_verified, role_required
from models.user import User
from models.project import Project

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/project-developer')
@login_required
@two_factor_verified
def project_developer():
    """Project Developer Dashboard"""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    # Get project statistics for initial page load
    stats = Project.get_user_stats(user_id)
    
    return render_template(
        'dashboard/project_developer.html',
        user=user,
        stats=stats  # Only pass stats for initial display
    )

@dashboard_bp.route('/farmer')
@login_required
@two_factor_verified
def farmer():
    """Farmer Dashboard"""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard/farmer.html', user=user)

@dashboard_bp.route('/verifier')
@login_required
@two_factor_verified
def verifier():
    """Verifier Dashboard"""
    user_id = session.get('user_id')
    user = User.get_by_id(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard/verifier.html', user=user)

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
        # Get stats for the main dashboard too
        stats = Project.get_user_stats(session['user_id'])
        dashboard_data['stats'] = stats
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

# ============ API ENDPOINTS ============

@dashboard_bp.route('/api/stats')
@login_required
@two_factor_verified
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        user_id = session.get('user_id')
        stats = Project.get_user_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/projects')
@login_required
@two_factor_verified
def api_user_projects():
    """API endpoint for user projects"""
    try:
        user_id = session.get('user_id')
        projects = Project.get_by_user(user_id)
        
        return jsonify({
            'success': True,
            'projects': [p.to_dict() for p in projects]
        })
        
    except Exception as e:
        print(f"Error fetching user projects: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/activity')
@login_required
@two_factor_verified
def api_recent_activity():
    """API endpoint for recent activity"""
    try:
        user_id = session.get('user_id')
        
        # For now, create mock activity based on projects
        projects = Project.get_by_user(user_id)
        activities = []
        
        for project in projects[:5]:  # Last 5 projects as activity
            activities.append({
                'id': project.id,
                'type': 'project_created',
                'description': f'Created project: {project.project_name}',
                'project_id': project.id,
                'created_at': project.created_at.isoformat() if project.created_at else None
            })
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        print(f"Error fetching activity: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500