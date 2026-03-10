"""Utility functions for the inspection tool."""

import os
from werkzeug.utils import secure_filename
from flask import current_app
from weasyprint import HTML
import io

def save_photo(file):
    """Save an uploaded photo to the uploads directory."""
    filename = secure_filename(file.filename)
    if not filename:
        raise ValueError("Invalid filename")

    # Check if file extension is allowed
    if '.' not in filename or not filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
        raise ValueError("Invalid file type")

    # Save file
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filename

def generate_pdf(template_name, context, output_path):
    """Generate a PDF from a template."""
    # This is a placeholder - actual implementation would depend on the template engine used
    # For now, we'll create a simple PDF with basic content
    html_content = f"""
    <html>
        <head>
            <title>Inspection Report</title>
        </head>
        <body>
            <h1>Inspection Report</h1>
            <p>This is a placeholder PDF generation function.</p>
            <p>Actual PDF generation would be implemented here.</p>
        </body>
    </html>
    """

    # Generate PDF to file
    HTML(string=html_content).write_pdf(output_path)