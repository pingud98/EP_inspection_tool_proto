"""Flask blueprints for authentication and main inspection functionality."""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
import io
from datetime import datetime

from models import User, Inspection, Photo, db, load_user
from forms import LoginForm, RegisterForm, InspectionForm, PasswordChangeForm
from utils import save_photo, generate_pdf

# Flask-Login requires user loader
@login_manager.user_loader
def load_user_id(user_id):
    return load_user(user_id)

# Auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next') or url_for('main.index')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'warning')
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

# Main blueprint for inspection CRUD
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    inspections = Inspection.query.order_by(Inspection.created_at.desc()).all()
    return render_template('inspections.html', inspections=inspections)

@main_bp.route('/inspection/new', methods=['GET', 'POST'])
@login_required
def create_inspection():
    form = InspectionForm()
    if form.validate_on_submit():
        insp = Inspection(
            title=form.title.data,
            description=form.description.data,
            remark_a=form.remark_a.data,
            remark_b=form.remark_b.data,
            remark_c=form.remark_c.data,
            created_by=current_user.id
        )
        db.session.add(insp)
        db.session.commit()
        # Handle photos
        files = request.files.getlist('photos')
        for f in files:
            if f and f.filename:
                try:
                    filename = save_photo(f)
                except ValueError:
                    continue
                photo = Photo(filename=filename, inspection_id=insp.id)
                db.session.add(photo)
        db.session.commit()
        flash('Inspection created', 'success')
        return redirect(url_for('main.detail', inspection_id=insp.id))
    return render_template('inspection_form.html', form=form, action='Create')

@main_bp.route('/inspection/<int:inspection_id>')
@login_required
def detail(inspection_id):
    insp = Inspection.query.get_or_404(inspection_id)
    return render_template('inspection_detail.html', inspection=insp)

@main_bp.route('/inspection/<int:inspection_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inspection(inspection_id):
    insp = Inspection.query.get_or_404(inspection_id)
    form = InspectionForm(obj=insp)
    if form.validate_on_submit():
        insp.title = form.title.data
        insp.description = form.description.data
        insp.remark_a = form.remark_a.data
        insp.remark_b = form.remark_b.data
        insp.remark_c = form.remark_c.data
        # Handle new photos
        files = request.files.getlist('photos')
        for f in files:
            if f and f.filename:
                try:
                    filename = save_photo(f)
                except ValueError:
                    continue
                photo = Photo(filename=filename, inspection_id=insp.id)
                db.session.add(photo)
        db.session.commit()
        flash('Inspection updated', 'success')
        return redirect(url_for('main.detail', inspection_id=insp.id))
    return render_template('inspection_form.html', form=form, action='Edit')

@main_bp.route('/inspection/<int:inspection_id>/delete', methods=['POST'])
@login_required
def delete_inspection(inspection_id):
    insp = Inspection.query.get_or_404(inspection_id)
    db.session.delete(insp)
    db.session.commit()
    flash('Inspection deleted', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/inspection/<int:inspection_id>/close', methods=['POST'])
@login_required
def close_inspection(inspection_id):
    insp = Inspection.query.get_or_404(inspection_id)
    insp.closed_at = datetime.utcnow()
    db.session.commit()
    flash('Inspection closed', 'success')
    return redirect(url_for('main.detail', inspection_id=insp.id))

@main_bp.route('/inspection/<int:inspection_id>/pdf')
@login_required
def download_pdf(inspection_id):
    insp = Inspection.query.get_or_404(inspection_id)
    output_path = os.path.join(Config.PDF_FOLDER, f'inspection_{insp.id}.pdf')
    generate_pdf('pdf_template.html', {'inspection': insp}, output_path)
    return send_file(output_path, as_attachment=True, download_name=f'inspection_{insp.id}.pdf')