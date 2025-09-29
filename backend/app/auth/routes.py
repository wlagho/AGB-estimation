# Authentication Routes

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from backend.app.auth.forms import LoginForm, RegistrationForm
from backend.app.auth.utils import login_required, login_user, logout_user, get_current_user
from backend.app.models.user import User, UserRole, db
from datetime import datetime

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user
            login_user(user, remember=form.remember_me.data)
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            organization=form.organization.data or None,
            role=UserRole(form.role.data)
        )
        user.set_password(form.password.data)
        
        # Save to database
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {e}")  # For debugging
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    user = get_current_user()
    if user:
        flash(f'You have been logged out, {user.first_name}. See you soon!', 'info')
    
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    return render_template('auth/profile.html', user=user)