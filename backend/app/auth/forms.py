# WTForms for Authentication

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from backend.app.models.user import User, UserRole

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(min=2, max=50, message="First name must be between 2 and 50 characters")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message="Last name is required"), 
        Length(min=2, max=50, message="Last name must be between 2 and 50 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    organization = StringField('Organization (Optional)', validators=[
        Length(max=100, message="Organization must be less than 100 characters")
    ])
    role = SelectField('Account Type', validators=[
        DataRequired(message="Please select an account type")
    ], choices=[
        (UserRole.RESEARCHER.value, 'Researcher - Basic AGB analysis and carbon estimates'),
        (UserRole.PROJECT_DEVELOPER.value, 'Project Developer - Full carbon market assessment and reporting')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    terms_accepted = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[
        DataRequired(message="You must accept the terms to register")
    ])
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email address is already registered. Please use a different email or try logging in.')
    
    def validate_password(self, password):
        """Validate password strength"""
        password_val = password.data
        if len(password_val) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(c.isupper() for c in password_val):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(c.islower() for c in password_val):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not any(c.isdigit() for c in password_val):
            raise ValidationError('Password must contain at least one number.')
