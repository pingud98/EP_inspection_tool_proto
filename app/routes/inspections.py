from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Inspection, InspectionInspector, Photo, User, db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField, SelectField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, Optional

inspections_bp = Blueprint('inspections', __name__)

class InspectionForm(FlaskForm):
    # Basic inspection information
    installation_name = StringField('Installation Name', validators=[DataRequired(), Length(max=200)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    inspection_date = DateField('Inspection Date', validators=[DataRequired()])
    reference_number = IntegerField('Reference Number', validators=[DataRequired()])
    
    # Observations
    observations = TextAreaField('Observations')
    
    # Inspectors (multiple fields)
    inspectors = FieldList(StringField('Inspector'), min_entries=1)
    
    # Conclusion
    conclusion_text = TextAreaField('Conclusion Text')
    conclusion_status = SelectField('Conclusion Status', 
                                   choices=[('ok', 'OK'), ('minor', 'Minor Issue'), ('major', 'Major Issue')],
                                   validators=[DataRequired()])
    
    # Submit button
    submit = SubmitField('Save Inspection')
    update = SubmitField('Update Inspection')

@inspections_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@inspections_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all inspections for the current user
    inspections = Inspection.query.join(User, Inspection.created_by_id == User.id)\
        .filter((User.id == current_user.id) | (User.is_admin == True))\
        .order_by(Inspection.created_at.desc()).all()
    
    return render_template('dashboard.html', inspections=inspections)

@inspections_bp.route('/inspection/new', methods=['GET', 'POST'])
@login_required
def inspection_new():
    form = InspectionForm()
    
    # Pre-fill inspectors with current user's full name
    if form.inspectors.entries:
        form.inspectors[0].data = current_user.full_name
    
    if form.validate_on_submit():
        # Create the inspection
        inspection = Inspection(
            installation_name=form.installation_name.data,
            location=form.location.data,
            inspection_date=form.inspection_date.data,
            reference_number=form.reference_number.data,
            observations=form.observations.data,
            conclusion_text=form.conclusion_text.data,
            conclusion_status=form.conclusion_status.data,
            created_by_id=current_user.id
        )
        
        db.session.add(inspection)
        db.session.flush()  # Get the inspection ID without committing
        
        # Add inspectors
        for inspector in form.inspectors.data:
            if inspector:
                # Check if inspector is a registered user
                user = User.query.filter_by(full_name=inspector).first()
                if user:
                    inspector_entry = InspectionInspector(
                        inspection_id=inspection.id,
                        user_id=user.id
                    )
                else:
                    inspector_entry = InspectionInspector(
                        inspection_id=inspection.id,
                        free_text_name=inspector
                    )
                db.session.add(inspector_entry)
        
        db.session.commit()
        flash('Inspection report created successfully.', 'success')
        return redirect(url_for('inspections.inspection_view', id=inspection.id))
    
    return render_template('inspection_form.html', form=form)

@inspections_bp.route('/inspection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def inspection_edit(id):
    inspection = Inspection.query.get_or_404(id)
    
    # Verify user has permission to edit
    if not (current_user.is_admin or inspection.created_by_id == current_user.id):
        flash('You do not have permission to edit this inspection.', 'error')
        return redirect(url_for('inspections.dashboard'))
    
    form = InspectionForm(obj=inspection)
    
    # Pre-fill inspectors with existing inspectors
    if inspection.inspectors:
        inspector_names = []
        for inspector in inspection.inspectors:
            if inspector.free_text_name:
                inspector_names.append(inspector.free_text_name)
            elif inspector.user:
                inspector_names.append(inspector.user.full_name)
        # Fill the first inspector field
        if inspector_names:
            form.inspectors[0].data = inspector_names[0]
            # Add additional fields if needed
            while len(form.inspectors) < len(inspector_names):
                form.inspectors.append_entry()
            # Fill remaining fields
            for i, name in enumerate(inspector_names[1:], 1):
                form.inspectors[i].data = name
    
    if form.validate_on_submit():
        # Update inspection
        inspection.installation_name = form.installation_name.data
        inspection.location = form.location.data
        inspection.inspection_date = form.inspection_date.data
        inspection.reference_number = form.reference_number.data
        inspection.observations = form.observations.data
        inspection.conclusion_text = form.conclusion_text.data
        inspection.conclusion_status = form.conclusion_status.data
        inspection.updated_at = datetime.utcnow()
        
        # Increment version
        inspection.version += 1
        
        # Update inspectors
        InspectionInspector.query.filter_by(inspection_id=inspection.id).delete()
        for inspector in form.inspectors.data:
            if inspector:
                # Check if inspector is a registered user
                user = User.query.filter_by(full_name=inspector).first()
                if user:
                    inspector_entry = InspectionInspector(
                        inspection_id=inspection.id,
                        user_id=user.id
                    )
                else:
                    inspector_entry = InspectionInspector(
                        inspection_id=inspection.id,
                        free_text_name=inspector
                    )
                db.session.add(inspector_entry)
        
        db.session.commit()
        flash('Inspection report updated successfully.', 'success')
        return redirect(url_for('inspections.inspection_view', id=inspection.id))
    
    return render_template('inspection_form.html', form=form, inspection=inspection)

@inspections_bp.route('/inspection/<int:id>')
@login_required
def inspection_view(id):
    inspection = Inspection.query.get_or_404(id)
    
    # Verify user has permission to view
    if not (current_user.is_admin or inspection.created_by_id == current_user.id):
        flash('You do not have permission to view this inspection.', 'error')
        return redirect(url_for('inspections.dashboard'))
    
    return render_template('inspection_view.html', inspection=inspection)

@inspections_bp.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if filename:
            # Generate unique filename
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            # Create uploads directory if it doesn't exist
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            return jsonify({'filename': unique_filename, 'original_filename': filename})
    
    return jsonify({'error': 'Upload failed'}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS