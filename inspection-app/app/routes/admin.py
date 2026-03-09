from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin_panel():
    # Only allow admin users
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('inspections.dashboard'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
def create_user():
    # Only allow admin users
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('inspections.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        is_active = 'is_active' in request.form

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('admin/user_form.html', edit=False)

        # Create new user
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            is_admin=is_admin,
            is_active=is_active
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin/user_form.html', edit=False)

@admin_bp.route('/admin/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    # Only allow admin users
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('inspections.dashboard'))

    user = User.query.get_or_404(id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.is_admin = 'is_admin' in request.form
        user.is_active = 'is_active' in request.form

        # Handle password change
        if request.form.get('password'):
            user.set_password(request.form['password'])

        db.session.commit()

        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin/user_form.html', user=user, edit=True)

@admin_bp.route('/admin/user/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    # Only allow admin users
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('inspections.dashboard'))

    user = User.query.get_or_404(id)

    # Prevent deleting current user
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('admin.admin_panel'))

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.admin_panel'))