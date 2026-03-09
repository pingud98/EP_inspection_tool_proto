from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Inspection, InspectionInspector, Photo, User
from app import db
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename

inspections_bp = Blueprint('inspections', __name__)

@inspections_bp.route('/')
@login_required
def dashboard():
    # For now, show all inspections
    inspections = Inspection.query.all()
    return render_template('dashboard.html', inspections=inspections)

@inspections_bp.route('/inspection/new', methods=['GET', 'POST'])
@login_required
def new_inspection():
    if request.method == 'POST':
        # Get form data
        installation_name = request.form['installation_name']
        location = request.form['location']
        inspection_date = datetime.strptime(request.form['inspection_date'], '%Y-%m-%d')
        reference_number = int(request.form['reference_number'])
        observations = request.form.get('observations', '')
        conclusion_text = request.form.get('conclusion_text', '')
        conclusion_status = request.form.get('conclusion_status')

        # Create inspection
        inspection = Inspection(
            installation_name=installation_name,
            location=location,
            inspection_date=inspection_date,
            reference_number=reference_number,
            observations=observations,
            conclusion_text=conclusion_text,
            conclusion_status=conclusion_status,
            created_by_id=current_user.id
        )

        db.session.add(inspection)
        db.session.flush()  # Get the ID for the new inspection

        # Handle inspectors
        inspector_names = request.form.getlist('inspector_names')
        inspector_user_ids = request.form.getlist('inspector_user_ids')

        # Add registered users as inspectors
        for user_id in inspector_user_ids:
            if user_id:
                inspector = InspectionInspector(
                    inspection_id=inspection.id,
                    user_id=int(user_id)
                )
                db.session.add(inspector)

        # Add free text inspectors
        for name in inspector_names:
            if name:
                inspector = InspectionInspector(
                    inspection_id=inspection.id,
                    free_text_name=name
                )
                db.session.add(inspector)

        # Handle photo uploads
        files = request.files.getlist('photos')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join('uploads', unique_filename)
                file.save(file_path)

                # Create photo record
                photo = Photo(
                    inspection_id=inspection.id,
                    filename=unique_filename,
                    caption=request.form.get(f'caption_{file.filename}', ''),
                    action_required=request.form.get(f'action_required_{file.filename}', 'none')
                )
                db.session.add(photo)

        db.session.commit()
        flash('Inspection report created successfully!', 'success')
        return redirect(url_for('inspections.view_inspection', id=inspection.id))

    # Get all users for inspector dropdown
    users = User.query.filter_by(is_active=True).all()
    return render_template('inspection_form.html', users=users, edit=False)

@inspections_bp.route('/inspection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inspection(id):
    inspection = Inspection.query.get_or_404(id)

    # Only allow editing if user is creator or admin
    if inspection.created_by_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to edit this inspection.', 'error')
        return redirect(url_for('inspections.dashboard'))

    if request.method == 'POST':
        # Get form data
        inspection.installation_name = request.form['installation_name']
        inspection.location = request.form['location']
        inspection.inspection_date = datetime.strptime(request.form['inspection_date'], '%Y-%m-%d')
        inspection.reference_number = int(request.form['reference_number'])
        inspection.observations = request.form.get('observations', '')
        inspection.conclusion_text = request.form.get('conclusion_text', '')
        inspection.conclusion_status = request.form.get('conclusion_status')

        # Update version
        inspection.version += 1

        # Update inspectors
        # Clear existing inspectors
        InspectionInspector.query.filter_by(inspection_id=inspection.id).delete()

        # Add new inspectors
        inspector_names = request.form.getlist('inspector_names')
        inspector_user_ids = request.form.getlist('inspector_user_ids')

        for user_id in inspector_user_ids:
            if user_id:
                inspector = InspectionInspector(
                    inspection_id=inspection.id,
                    user_id=int(user_id)
                )
                db.session.add(inspector)

        for name in inspector_names:
            if name:
                inspector = InspectionInspector(
                    inspection_id=inspection.id,
                    free_text_name=name
                )
                db.session.add(inspector)

        # Handle photo uploads
        files = request.files.getlist('photos')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join('uploads', unique_filename)
                file.save(file_path)

                # Create photo record
                photo = Photo(
                    inspection_id=inspection.id,
                    filename=unique_filename,
                    caption=request.form.get(f'caption_{file.filename}', ''),
                    action_required=request.form.get(f'action_required_{file.filename}', 'none')
                )
                db.session.add(photo)

        db.session.commit()
        flash('Inspection report updated successfully!', 'success')
        return redirect(url_for('inspections.view_inspection', id=inspection.id))

    # Get all users for inspector dropdown
    users = User.query.filter_by(is_active=True).all()
    return render_template('inspection_form.html', inspection=inspection, users=users, edit=True)

@inspections_bp.route('/inspection/<int:id>')
@login_required
def view_inspection(id):
    inspection = Inspection.query.get_or_404(id)
    return render_template('inspection_view.html', inspection=inspection)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}