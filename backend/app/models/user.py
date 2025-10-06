from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    RESEARCHER = "researcher"
    PROJECT_DEVELOPER = "project_developer" 
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.RESEARCHER)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    
    # Account status
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships (for later sprints)
    # processing_sessions = db.relationship('ProcessingSession', backref='user', lazy=True)
    # agb_results = db.relationship('AGBResult', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def get_full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_role_display(self):
        """Return human-readable role name"""
        role_names = {
            UserRole.RESEARCHER: "Researcher",
            UserRole.PROJECT_DEVELOPER: "Project Developer", 
            UserRole.ADMIN: "Administrator"
        }
        return role_names.get(self.role, "Unknown")
    
    def has_permission(self, permission):
        """Check if user has specific permission (for role-based access)"""
        permissions = {
            UserRole.RESEARCHER: ['view_demo', 'basic_analysis'],
            UserRole.PROJECT_DEVELOPER: ['view_demo', 'basic_analysis', 'carbon_assessment', 'export_reports'],
            UserRole.ADMIN: ['view_demo', 'basic_analysis', 'carbon_assessment', 'export_reports', 'user_management']
        }
        return permission in permissions.get(self.role, [])
    
    def to_dict(self):
        """Convert user to dictionary (for API responses)"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role.value,
            'full_name': self.get_full_name(),
            'organization': self.organization,
            'email_verified': self.email_verified,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }