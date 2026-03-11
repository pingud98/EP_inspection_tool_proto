from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, db, Config
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure user is admin"""
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('inspections.dashboard'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def get_logo_filename():
    """Get the logo filename from configuration"""
    logo_config = Config.query.filter_by(key='logo_filename').first()
    return logo_config.value if logo_config else None

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    is_admin = BooleanField('Administrator')
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class LogoForm(FlaskForm):
    logo = FileField('Logo', validators=[])
    submit = SubmitField('Save Logo')

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the last admin user
    if user.is_admin:
        admin_count = User.query.filter_by(is_admin=True).count()
        if admin_count <= 1:
            flash('Cannot delete the last administrator user.', 'error')
            return redirect(url_for('admin.users'))
    
    # Prevent deleting self
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/logo', methods=['GET', 'POST'])
@login_required
@admin_required
def logo():
    form = LogoForm()
    logo_filename = get_logo_filename()
    
    if form.validate_on_submit():
        if form.logo.data:
            # Save the uploaded logo
            filename = form.logo.data.filename
            if filename and '.' in filename:
                # Only allow jpeg and png files
                ext = filename.rsplit('.', 1)[1].lower()
                if ext in ['jpeg', 'jpg', 'png']:
                    # Create uploads directory if it doesn't exist
                    upload_dir = 'uploads'
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file with a unique name
                    logo_filename = f"logo.{ext}"
                    file_path = os.path.join(upload_dir, logo_filename)
                    form.logo.data.save(file_path)
                    
                    # Save filename to config
                    logo_config = Config.query.filter_by(key='logo_filename').first()
                    if logo_config:
                        logo_config.value = logo_filename
                    else:
                        logo_config = Config(key='logo_filename', value=logo_filename)
                        db.session.add(logo_config)
                    
                    db.session.commit()
                    flash('Logo uploaded successfully.', 'success')
                    return redirect(url_for('admin.logo'))
                else:
                    flash('Invalid file type. Only JPEG and PNG files are allowed.', 'error')
            else:
                flash('Invalid filename.', 'error')
        else:
            flash('No file selected.', 'error')
    
    return render_template('admin/logo.html', form=form, logo_filename=logo_filename)

@admin_bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('admin/user_form.html', form=form)
        
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            email=form.email.data,
            is_admin=form.is_admin.data,
            is_active=form.is_active.data
        )
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form)

@admin_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    # Remove the password field from the form for editing
    form.password = PasswordField('Password')
    
    if form.validate_on_submit():
        # Check if username or email already exists (excluding the current user)
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data),
            User.id != user_id
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('admin/user_form.html', form=form)
        
        user.username = form.username.data
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', form=form, user=user)