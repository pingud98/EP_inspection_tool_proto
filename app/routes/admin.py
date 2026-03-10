from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, db
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

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

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    is_admin = BooleanField('Administrator')
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

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