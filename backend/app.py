# Main Flask Application (Updated)

from flask import Flask, render_template
from backend.app import create_app
import os

# Create Flask app
app = create_app()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        from backend.app.models.user import db
        db.create_all()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)