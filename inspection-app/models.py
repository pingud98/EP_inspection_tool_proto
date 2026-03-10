"""Database models for the inspection tool."""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relationship with inspections
    inspections = db.relationship('Inspection', backref='creator', lazy=True)

    def set_password(self, password):
        """Set password hash for user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Inspection(db.Model):
    """Inspection model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    remark_a = db.Column(db.Boolean, default=False)
    remark_b = db.Column(db.Boolean, default=False)
    remark_c = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship with photos
    photos = db.relationship('Photo', backref='inspection', lazy=True)

    def __repr__(self):
        return f'<Inspection {self.title}>'

class Photo(db.Model):
    """Photo model for inspection images."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'), nullable=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'

def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))