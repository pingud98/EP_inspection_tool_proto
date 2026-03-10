from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app.models import Inspection, InspectionInspector, Photo, User, db
from weasyprint import HTML
import os
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/inspection/<int:id>/pdf')
@login_required
def export_pdf(id):
    inspection = Inspection.query.get_or_404(id)
    
    # Verify user has permission to view
    if not (current_user.is_admin or inspection.created_by_id == current_user.id):
        flash('You do not have permission to export this inspection.', 'error')
        return redirect(url_for('inspections.dashboard'))
    
    # Render the PDF template
    html_string = render_template('pdf_template.html', inspection=inspection)
    
    # Generate PDF
    pdf = HTML(string=html_string, base_url=request.url_root).write_pdf()
    
    # Create filename
    filename = f"inspection_report_{inspection.reference_number}_v{inspection.version}.pdf"
    
    # Return PDF as download
    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )