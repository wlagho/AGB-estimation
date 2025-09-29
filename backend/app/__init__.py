# Flask Application Factory

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.app.config import Config
from backend.app.models.user import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from backend.app.auth.routes import auth
    app.register_blueprint(auth)
    
    # Main routes (for later)
    from backend.app.main.routes import main
    app.register_blueprint(main)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app