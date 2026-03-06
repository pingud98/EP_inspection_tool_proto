# Minimal routes for the application

from flask import Blueprint, render_template

# Auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    return 'Login page'

# Main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return 'Hello, World!'
