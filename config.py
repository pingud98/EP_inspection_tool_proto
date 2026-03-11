import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Self-signed certificate paths
    CERT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'cert.pem')
    KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'key.pem')
    
    # Logo configuration
    LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'logo.png')