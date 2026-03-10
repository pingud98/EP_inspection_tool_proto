"""Flask application factory.

This module creates the Flask app, configures extensions, registers blueprints
and sets up HTTPS using certificates defined in :class:`config.Config`.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from config import Config

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    """Create and configure a :class:`flask.Flask` instance.

    Parameters
    ----------
    test_config: dict, optional
        If provided, overrides :data:`Config` and is useful for tests.
    """
    app = Flask(__name__)
    # Load config
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # Set secure cookie attributes
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Initialise extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes import auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    # HTTPS context
    ssl_context = (
        Config.CERT_PATH,
        Config.KEY_PATH,
    )

    return app