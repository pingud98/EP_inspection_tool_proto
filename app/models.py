from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=12)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    installation_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    reference_number = db.Column(db.Integer, nullable=False)
    observations = db.Column(db.Text)
    conclusion_text = db.Column(db.Text)
    conclusion_status = db.Column(db.Enum('ok', 'minor', 'major'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', backref=db.backref('inspections', lazy=True))
    inspectors = db.relationship('InspectionInspector', backref='inspection', lazy=True)
    photos = db.relationship('Photo', backref='inspection', lazy=True)
    
    def __repr__(self):
        return f'<Inspection {self.reference_number} - {self.installation_name}>'

class InspectionInspector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    free_text_name = db.Column(db.String(120), nullable=True)
    
    # Relationship to user (optional)
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<InspectionInspector {self.id}>'

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspection.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.Text)
    action_required = db.Column(db.Enum('none', 'urgent', 'before_next'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Photo {self.filename}>'