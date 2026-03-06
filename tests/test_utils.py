import os
import io
import tempfile
from pathlib import Path

import pytest
from werkzeug.datastructures import FileStorage

# Import the utilities and config from the project
from utils import allowed_file, save_photo, generate_pdf
from config import Config


def test_allowed_file_valid_extensions():
    # Valid extensions as defined in Config.ALLOWED_EXTENSIONS
    for ext in Config.ALLOWED_EXTENSIONS:
        filename = f"test.{ext}"
        assert allowed_file(filename) is True


def test_allowed_file_invalid_extension():
    assert allowed_file("test.exe") is False
    assert allowed_file("noextension") is False
    assert allowed_file(".hiddenfile") is False


def test_save_photo_success(tmp_path, monkeypatch):
    # Use a temporary directory for uploads
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(Config, "UPLOAD_FOLDER", str(upload_dir))

    # Create a simple in‑memory file storage object
    data = b"fake image data"
    file_storage = FileStorage(stream=io.BytesIO(data), filename="image.png", content_type="image/png")

    # Call the function
    saved_name = save_photo(file_storage)

    # The returned name should be a UUID prefixed filename
    assert saved_name.endswith("_image.png")
    # Ensure the file was actually written to the upload directory
    saved_path = upload_dir / saved_name
    assert saved_path.is_file()
    assert saved_path.read_bytes() == data


def test_save_photo_disallowed_extension(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(Config, "UPLOAD_FOLDER", str(upload_dir))

    data = b"data"
    file_storage = FileStorage(stream=io.BytesIO(data), filename="malicious.exe", content_type="application/octet-stream")

    with pytest.raises(ValueError, match="Unsupported file type"):
        save_photo(file_storage)


def test_generate_pdf_creates_file(tmp_path, monkeypatch):
    # Create a dummy template rendering function
    def fake_render_template(template_name, **context):
        return "<html><body>Test PDF</body></html>"

    # Patch Flask's render_template and WeasyPrint's HTML class
    monkeypatch.setattr('flask.render_template', fake_render_template)

    class DummyHTML:
        def __init__(self, string):
            self.string = string
        def write_pdf(self, output_path):
            # Write a simple PDF header to simulate output
            with open(output_path, "wb") as f:
                f.write(b"%PDF-1.4\n%Test PDF content\n")

    monkeypatch.setattr('weasyprint.HTML', DummyHTML)

    output_file = tmp_path / "report.pdf"
    generate_pdf("dummy.html", {}, str(output_file))

    assert output_file.is_file()
    # Basic check that the file starts with a PDF header
    assert output_file.read_bytes().startswith(b"%PDF-1.4")
