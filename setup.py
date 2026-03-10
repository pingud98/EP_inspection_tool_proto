#!/usr/bin/env python3

import os
import sys
import subprocess
import hashlib
import ipaddress
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

def generate_self_signed_cert():
    """Generate a self-signed certificate for development"""
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "EP Inspection Tool"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Save private key
    with open("certs/private.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save certificate
    with open("certs/certificate.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Self-signed certificate generated successfully")

def create_directories():
    """Create required directories"""
    dirs = ['uploads', 'certs']
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def setup_database():
    """Initialize the database"""
    try:
        from app import create_app
        from app.models import db
        
        # Create a simple config object
        class DevelopmentConfig:
            SECRET_KEY = 'dev-secret-key'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            MAX_CONTENT_LENGTH = 10 * 1024 * 1024
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            CERT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'cert.pem')
            KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'key.pem')
        
        app = create_app(DevelopmentConfig)
        
        with app.app_context():
            db.create_all()
            print("Database initialized")
    except Exception as e:
        print(f"Error setting up database: {e}")

def create_admin_user():
    """Create the default admin user"""
    try:
        from app import create_app
        from app.models import db, User
        
        # Create a simple config object
        class DevelopmentConfig:
            SECRET_KEY = 'dev-secret-key'
            SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
            MAX_CONTENT_LENGTH = 10 * 1024 * 1024
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            CERT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'cert.pem')
            KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'certs', 'key.pem')
        
        app = create_app(DevelopmentConfig)
        
        with app.app_context():
            # Check if admin user already exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                admin_user.set_password('password')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin user: {e}")

def main():
    """Main setup function"""
    print("Setting up EP Inspection Tool...")
    
    # Create directories
    create_directories()
    
    # Generate certificates
    generate_self_signed_cert()
    
    # Setup database
    setup_database()
    
    # Create admin user
    create_admin_user()
    
    print("Setup completed successfully!")

if __name__ == '__main__':
    main()