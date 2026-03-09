# Inspection Reporting Tool

A production-ready web application for managing inspection reports with PDF export capabilities.

## Features

- User authentication and authorization
- Admin panel for user management
- Inspection report creation and management
- Photo upload and management
- PDF export functionality
- Responsive web interface with Tailwind CSS

## Requirements

- Python 3.11 or higher
- OpenSSL (for generating TLS certificates)

## Setup Instructions

1. **Install system dependencies (required for WeasyPrint):**
   - Debian/Ubuntu: `sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0`
   - macOS: `brew install pango`
   - Windows: See [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)

2. **Install Python dependencies:**
   ```bash
   python setup.py
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Access the application:**
   Open your browser and go to `https://localhost:5000`

## Security Notes

The application uses self-signed certificates for local development. You will see a browser security warning. This is expected and can be safely ignored for local testing.

## Development

The application follows a standard Flask structure:
- `app/` - Main application code
  - `models.py` - Database models
  - `routes/` - Route handlers
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS)
  - `utils/` - Utility functions

## License

This project is licensed under the MIT License.