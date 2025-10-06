from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from forms.auth_forms import (RegistrationForm, LoginForm, PasswordResetRequestForm,
                               PasswordResetForm, TwoFactorForm)
from models.user import User, UserToken
from utils.email_service import (send_password_reset_email, send_2fa_code_email,
                                  send_welcome_email, generate_2fa_code)
from utils.decorators import logout_required, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        try:
            user = User.create(
                email=form.email.data,
                password=form.password.data,
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                organization=form.organization.data,
                phone_number=form.phone_number.data if form.phone_number.data else None
            )

            if user:
                send_welcome_email(user.email, user.first_name)
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration failed. Please try again.', 'danger')

        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'danger')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.get_by_email(form.email.data)

            if user and User.verify_password(form.password.data, user.password_hash):
                if user.two_factor_enabled:
                    code = generate_2fa_code()
                    token = UserToken.create_token(user.id, 'two_factor', expiry_minutes=10)

                    session['temp_user_id'] = str(user.id)
                    session['two_factor_code'] = code
                    session['two_factor_required'] = True
                    session['two_factor_verified'] = False

                    send_2fa_code_email(user.email, code)
                    flash('A verification code has been sent to your email.', 'info')
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    session['user_id'] = str(user.id)
                    session['user_email'] = user.email
                    session['user_role'] = user.role
                    session['user_name'] = f"{user.first_name} {user.last_name}"
                    session.permanent = True

                    user.update_last_login()
                    flash(f'Welcome back, {user.first_name}!', 'success')
                    return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid email or password.', 'danger')

        except Exception as e:
            flash(f'An error occurred during login: {str(e)}', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('auth.login'))

    form = TwoFactorForm()

    if form.validate_on_submit():
        try:
            if form.code.data == session.get('two_factor_code'):
                user_id = session.pop('temp_user_id')
                session.pop('two_factor_code')
                session['two_factor_verified'] = True

                user = User.get_by_id(user_id)

                if user:
                    session['user_id'] = str(user.id)
                    session['user_email'] = user.email
                    session['user_role'] = user.role
                    session['user_name'] = f"{user.first_name} {user.last_name}"
                    session.permanent = True

                    user.update_last_login()
                    flash(f'Welcome back, {user.first_name}!', 'success')
                    return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid verification code. Please try again.', 'danger')

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('auth/verify_2fa.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('public.index'))

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
@logout_required
def reset_password_request():
    form = PasswordResetRequestForm()

    if form.validate_on_submit():
        try:
            user = User.get_by_email(form.email.data)

            if user:
                token = UserToken.create_token(user.id, 'password_reset', expiry_minutes=60)
                if token:
                    send_password_reset_email(user.email, token)

            flash('If an account exists with this email, a password reset link has been sent.', 'info')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@logout_required
def reset_password(token):
    form = PasswordResetForm()

    try:
        user_id = UserToken.verify_token(token, 'password_reset')

        if not user_id:
            flash('Invalid or expired reset link.', 'danger')
            return redirect(url_for('auth.reset_password_request'))

        if form.validate_on_submit():
            user = User.get_by_id(user_id)

            if user:
                user.update_password(form.password.data)
                UserToken.mark_as_used(token)
                flash('Your password has been reset successfully. You can now log in.', 'success')
                return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    return render_template('auth/reset_password.html', form=form, token=token)

@auth_bp.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    try:
        user = User.get_by_id(session['user_id'])
        if user:
            user.enable_two_factor()
            flash('Two-factor authentication has been enabled.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('dashboard.index'))

@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    try:
        user = User.get_by_id(session['user_id'])
        if user:
            user.disable_two_factor()
            flash('Two-factor authentication has been disabled.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('dashboard.index'))
