"""
Utility helpers for the inspection app.
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
# from flask import current_app

# Allowed extensions defined in config
from config import Config


def allowed_file(filename: str) -> bool:
    """Return True if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_photo(file_storage) -> str:
    """Save an uploaded photo to the upload folder.

    Returns the relative filename stored in the database.
    """
    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type")
    filename = secure_filename(file_storage.filename)
    # Prepend a UUID to avoid collisions
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    upload_path = Path(Config.UPLOAD_FOLDER) / unique_name
    # Ensure upload folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file_storage.save(str(upload_path))
    return unique_name


def generate_pdf(template_name: str, context: dict, output_path: str) -> None:
    """Render a Jinja template into a PDF using WeasyPrint.

    Parameters
    ----------
    template_name: str
        Name of the Jinja template in the templates directory.
    context: dict
        Context data passed to the template.
    output_path: str
        Full path to write the generated PDF.
    """
    from flask import render_template
    from weasyprint import HTML

    html = render_template(template_name, **context)
    HTML(string=html).write_pdf(output_path)

    # Ensure output directory exists
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
