from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('public/landing.html')

@public_bp.route('/demo')
def demo():
    return render_template('public/demo.html')

@public_bp.route('/about')
def about():
    return render_template('public/about.html')
