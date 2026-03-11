from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.models import db, Config as ConfigModel, User
import os
from datetime import datetime

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

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
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app