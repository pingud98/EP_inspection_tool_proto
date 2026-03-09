#!/usr/bin/env python3
"""
Test script to verify basic application functionality.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app import create_app
from app.models import db, User
from config import Config

def test_app_creation():
    """Test that app can be created successfully."""
    print("Testing app creation...")

    app = create_app()

    # Test that app is created
    assert app is not None
    print("✓ App creation successful")

    # Test database creation
    with app.app_context():
        db.create_all()
        print("✓ Database creation successful")

        # Test user creation
        user = User(
            username="testuser",
            full_name="Test User",
            email="test@example.com",
            is_admin=False,
            is_active=True
        )
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        # Verify user exists
        found_user = User.query.filter_by(username="testuser").first()
        assert found_user is not None
        assert found_user.check_password("testpassword")
        print("✓ User creation and authentication successful")

        # Clean up test user
        db.session.delete(found_user)
        db.session.commit()

    print("All tests passed!")

if __name__ == "__main__":
    test_app_creation()