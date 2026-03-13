import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.models import db, Config as ConfigModel, User
from datetime import datetime
import secrets

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
# Enhanced session security
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))

def get_logo_filename():
    """Get the logo filename from database configuration"""
    try:
        logo_config = ConfigModel.query.filter_by(key='logo_filename').first()
        return logo_config.value if logo_config else None
    except:
        return None

def format_date(value, format='%Y'):
    """Format date for Jinja2 templates"""
    if value:
        return value.strftime(format)
    return ''

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enhanced security configuration
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ep_inspection_tool.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('EP Inspection Tool startup')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    
    # Create uploads directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create certs directory if it doesn't exist
    os.makedirs(os.path.dirname(app.config['CERT_PATH']), exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.inspections import inspections_bp
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inspections_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)
    
    # Add logo filename to template context
    @app.context_processor
    def inject_logo():
        return dict(logo_filename=get_logo_filename())
    
    # Add custom filters
    @app.template_filter('format_date')
    def format_date_filter(value, format='%Y'):
        return format_date(value, format)
    
    # Add current date function
    @app.context_processor
    def inject_current_date():
        return dict(moment=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Page not found: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500
    
    # Security headers
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app