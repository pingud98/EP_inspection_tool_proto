#!/usr/bin/env python3
"""
Setup script for Inspection Reporting Tool.
This script installs dependencies, creates database,
and sets up the admin user.
"""
import os
import sys
import subprocess
from app.models import User
from app import create_app, db

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_database():
    """Create the database and tables."""
    print("Creating database...")

    # Create app instance and context
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()

        print("Database created successfully.")
        return True

def create_admin_user():
    """Create the initial admin user."""
    print("Creating admin user...")

    # Create app instance and context
    app = create_app()

    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("Admin user already exists.")
            return True

        # Get user input for admin credentials
        print("Please provide admin credentials:")
        username = input("Username (default: admin): ").strip() or 'admin'
        full_name = input("Full name: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()

        # Create admin user
        admin = User(
            username=username,
            full_name=full_name,
            email=email,
            is_admin=True,
            is_active=True
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")
        return True

def main():
    print("Setting up Inspection Reporting Tool...")

    # Install dependencies
    print("Installing dependencies...")
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install dependencies")
        sys.exit(1)

    # Create database
    if not create_database():
        print("Failed to create database")
        sys.exit(1)

    # Create admin user
    if not create_admin_user():
        print("Failed to create admin user")
        sys.exit(1)

    print("\nSetup completed successfully!")
    print("You can now start the application with: python run.py")
    print("The application will be accessible at: https://localhost:5000")

if __name__ == "__main__":
    main()