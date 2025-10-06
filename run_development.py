# Development Server Runner

import os
from backend.app import create_app

# Set environment variables for development
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Create and run the app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from backend.app.models.user import db
        db.create_all()
    
    print("🚀 Starting SHCAP Development Server...")
    print("📱 Access the application at: http://localhost:5000")
    print("👤 Demo users available (run create_demo_users.py first)")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )