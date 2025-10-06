# Script to Create Demo Users

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.models.user import User, UserRole, db

def create_demo_users():
    """Create demo users for testing"""
    app = create_app()
    
    with app.app_context():
        # Create tables first
        db.create_all()
        
        # Demo users data
        demo_users = [
            {
                'email': 'researcher@demo.com',
                'password': 'Demo123!',
                'first_name': 'John',
                'last_name': 'Researcher',
                'organization': 'University of Nairobi',
                'role': UserRole.RESEARCHER,
                'email_verified': True
            },
            {
                'email': 'developer@demo.com',
                'password': 'Demo123!',
                'first_name': 'Mary',
                'last_name': 'Developer',
                'organization': 'Kenya Forestry Research Institute',
                'role': UserRole.PROJECT_DEVELOPER,
                'email_verified': True
            },
            {
                'email': 'admin@demo.com',
                'password': 'Demo123!',
                'first_name': 'Admin',
                'last_name': 'User',
                'organization': 'SHCAP System',
                'role': UserRole.ADMIN,
                'email_verified': True
            }
        ]
        
        for user_data in demo_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"User {user_data['email']} already exists")
                continue
            
            # Create new user
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                organization=user_data['organization'],
                role=user_data['role'],
                email_verified=user_data['email_verified']
            )
            user.set_password(user_data['password'])
            
            db.session.add(user)
            print(f"✅ Created {user_data['role'].value} user: {user_data['email']}")
        
        db.session.commit()
        print("\n✅ Demo users created successfully!")
        print("\nLogin credentials:")
        for user_data in demo_users:
            print(f"Email: {user_data['email']} | Password: {user_data['password']} | Role: {user_data['role'].value}")

if __name__ == "__main__":
    create_demo_users()