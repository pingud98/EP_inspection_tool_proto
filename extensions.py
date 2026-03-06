from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# Database instance

db = SQLAlchemy()

# Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# CSRF protection
csrf = CSRFProtect()
