from flask import Blueprint, send_file, flash, redirect, url_for
from flask_login import login_required
from app.models import Inspection
from app.utils.pdf_generator import generate_inspection_pdf
import io
import os

export_bp = Blueprint('export', __name__)

@export_bp.route('/inspection/<int:id>/pdf')
@login_required
def export_pdf(id):
    inspection = Inspection.query.get_or_404(id)

    # Generate PDF
    pdf_data = generate_inspection_pdf(inspection)

    # Create filename
    filename = f"inspection_report_{inspection.reference_number}_v{inspection.version}.pdf"

    # Return PDF file
    return send_file(
        io.BytesIO(pdf_data),
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )