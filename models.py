"""SQLAlchemy models for the inspection app."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Database instance will be initialized in app.py
# Importing here avoids circular imports

from config import Config

# Create a new SQLAlchemy instance; it will be bound to the Flask app later

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with password hashing and admin flag."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    needs_password_change = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Inspection(db.Model):
    """Inspection record with remarks and photos."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Three remark categories
    remark_a = db.Column(db.Boolean, default=False)
    remark_b = db.Column(db.Boolean, default=False)
    remark_c = db.Column(db.Boolean, default=False)
    closed_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship
    photos = db.relationship('Photo', backref='inspection', lazy=True, cascade='all, delete-orphan')


class Photo(db.Model):
    """Uploaded photo belonging to an inspection."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    upload_path = db.Column(db.String(512), nullable=False)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# Helper to load user for Flask-Login

def load_user(user_id):
    return User.query.get(int(user_id))
