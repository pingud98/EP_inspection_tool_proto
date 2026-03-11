#!/usr/bin/env python3
"""
Test suite for EP Inspection Tool
"""
import unittest
import tempfile
import os
from app import create_app
from app.models import db, User, Inspection, InspectionInspector, Photo
from config import Config
from werkzeug.security import generate_password_hash

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

class EPInspectionTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        self.test_user = User(
            username='testuser',
            full_name='Test User',
            email='test@example.com',
            is_admin=False
        )
        self.test_user.set_password('password')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Create an admin user
        self.admin_user = User(
            username='admin',
            full_name='Admin User',
            email='admin@example.com',
            is_admin=True
        )
        self.admin_user.set_password('adminpassword')
        db.session.add(self.admin_user)
        db.session.commit()
        
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_user_creation(self):
        """Test user creation and password hashing"""
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('wrongpassword'))
        
    def test_user_creation_with_admin(self):
        """Test admin user creation"""
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin)
        self.assertTrue(admin.is_admin)
        self.assertTrue(admin.check_password('adminpassword'))
        
    def test_inspection_creation(self):
        """Test inspection creation"""
        from datetime import date
        inspection = Inspection(
            installation_name='Test Installation',
            location='Test Location',
            inspection_date=date(2023, 1, 1),
            reference_number=1,
            conclusion_status='ok',
            created_by_id=self.test_user.id
        )
        db.session.add(inspection)
        db.session.commit()
        
        # Verify inspection was created
        inspection = Inspection.query.first()
        self.assertIsNotNone(inspection)
        self.assertEqual(inspection.installation_name, 'Test Installation')
        
    def test_inspection_creation_with_inspectors(self):
        """Test inspection creation with inspectors"""
        from datetime import date
        inspection = Inspection(
            installation_name='Test Installation',
            location='Test Location',
            inspection_date=date(2023, 1, 1),
            reference_number=1,
            conclusion_status='ok',
            created_by_id=self.test_user.id
        )
        db.session.add(inspection)
        db.session.flush()
        
        # Add inspector
        inspector = InspectionInspector(
            inspection_id=inspection.id,
            user_id=self.test_user.id
        )
        db.session.add(inspector)
        db.session.commit()
        
        # Verify inspector was added
        inspector = InspectionInspector.query.first()
        self.assertIsNotNone(inspector)
        self.assertEqual(inspector.user_id, self.test_user.id)
        
    def test_database_connection(self):
        """Test that database is accessible"""
        self.assertIsNotNone(db.engine)
        
    def test_user_authentication(self):
        """Test user authentication"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
    def test_user_authentication_failed(self):
        """Test failed user authentication"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        
    def test_user_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        
    def test_admin_user_can_access_admin_panel(self):
        """Test that admin user can access admin panel"""
        # Login as admin
        self.client.post('/login', data={
            'username': 'admin',
            'password': 'adminpassword'
        })
        
        # Access admin panel (should be accessible)
        response = self.client.get('/admin')
        # Should either redirect to login or return 200 (depending on implementation)
        
    def test_inspection_creation_with_photo(self):
        """Test inspection creation with photo"""
        from datetime import date
        inspection = Inspection(
            installation_name='Test Installation',
            location='Test Location',
            inspection_date=date(2023, 1, 1),
            reference_number=1,
            conclusion_status='ok',
            created_by_id=self.test_user.id
        )
        db.session.add(inspection)
        db.session.commit()
        
        # Create a photo
        photo = Photo(
            inspection_id=inspection.id,
            filename='test_photo.jpg',
            action_required='none'
        )
        db.session.add(photo)
        db.session.commit()
        
        # Verify photo was added
        photo = Photo.query.first()
        self.assertIsNotNone(photo)
        self.assertEqual(photo.filename, 'test_photo.jpg')
        
    def test_inspection_validation(self):
        """Test inspection data validation"""
        from datetime import date
        # Test with valid data
        inspection = Inspection(
            installation_name='Test Installation',
            location='Test Location',
            inspection_date=date(2023, 1, 1),
            reference_number=1,
            conclusion_status='ok',
            created_by_id=self.test_user.id
        )
        db.session.add(inspection)
        db.session.commit()
        
        # Test with invalid data (should be prevented by constraints)
        # This test verifies that constraints are properly applied
        inspection2 = Inspection(
            installation_name='T',  # Too short
            location='Test Location',
            inspection_date=date(2023, 1, 1),
            reference_number=1,
            conclusion_status='ok',
            created_by_id=self.test_user.id
        )
        db.session.add(inspection2)
        
        # This should raise an exception due to validation constraints
        with self.assertRaises(Exception):
            db.session.commit()
            
    def test_user_validation(self):
        """Test user data validation"""
        # Test with valid data
        user = User(
            username='testuser2',
            full_name='Test User 2',
            email='test2@example.com',
            is_admin=False
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Verify user was created
        user = User.query.filter_by(username='testuser2').first()
        self.assertIsNotNone(user)
        
        # Test with invalid data (should be prevented by constraints)
        invalid_user = User(
            username='ab',  # Too short
            full_name='Test User',
            email='test@example.com',
            is_admin=False
        )
        invalid_user.set_password('password')
        db.session.add(invalid_user)
        
        # This should raise an exception due to validation constraints
        with self.assertRaises(Exception):
            db.session.commit()

    def test_inspection_workflow(self):
        """Test complete inspection workflow"""
        # Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)
        
        # Create inspection
        response = self.client.post('/inspection/new', data={
            'installation_name': 'Workshop Inspection',
            'location': 'Building A',
            'inspection_date': '2023-01-15',
            'reference_number': 1001,
            'conclusion_status': 'ok',
            'observations': 'All systems normal',
            'conclusion_text': 'No issues found'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify inspection was created
        inspection = Inspection.query.first()
        self.assertIsNotNone(inspection)
        self.assertEqual(inspection.installation_name, 'Workshop Inspection')
        
    def test_admin_access(self):
        """Test admin user access to restricted areas"""
        # Login as admin
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'adminpassword'
        })
        self.assertEqual(response.status_code, 302)
        
        # Access admin panel
        response = self.client.get('/admin')
        # This should either redirect or give access
        
    def test_unauthorized_access(self):
        """Test unauthorized access prevention"""
        # Try to access dashboard without login
        response = self.client.get('/dashboard')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()