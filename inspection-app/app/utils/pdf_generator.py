from weasyprint import HTML, CSS
from flask import render_template_string
from datetime import datetime
import os

def generate_inspection_pdf(inspection):
    """Generate a PDF from an inspection report."""

    # Define CSS for the PDF
    css = """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
        }
    }

    body {
        font-family: Arial, sans-serif;
        font-size: 12pt;
        line-height: 1.4;
        color: #333;
    }

    h1, h2, h3 {
        color: #2c5282;
    }

    .header {
        text-align: center;
        border-bottom: 2px solid #2c5282;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    .section {
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 14pt;
        font-weight: bold;
        margin-bottom: 10px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 5px;
    }

    .field {
        margin-bottom: 8px;
    }

    .field-label {
        font-weight: bold;
    }

    .field-value {
        margin-left: 10px;
    }

    .photo-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-top: 15px;
    }

    .photo-item {
        text-align: center;
    }

    .photo-item img {
        max-width: 100%;
        height: auto;
        border: 1px solid #ccc;
        padding: 5px;
    }

    .photo-caption {
        margin-top: 5px;
        font-size: 10pt;
    }

    .action-required {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 8pt;
        font-weight: bold;
    }

    .action-none {
        background-color: #d1fae5;
        color: #065f46;
    }

    .action-urgent {
        background-color: #fee2e2;
        color: #b91c1c;
    }

    .action-before-next {
        background-color: #fef3c7;
        color: #92400e;
    }

    .inspector-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 5px;
    }

    .inspector-tag {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10pt;
    }
    """

    # Generate HTML content
    html_content = render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Inspection Report - {{ inspection.reference_number }} - v{{ inspection.version }}</title>
        <style>
            {{ css }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Inspection Report</h1>
            <p>Reference: {{ inspection.reference_number }} | Version: {{ inspection.version }}</p>
        </div>

        <div class="section">
            <h2 class="section-title">Installation Details</h2>
            <div class="field"><span class="field-label">Installation Name:</span> <span class="field-value">{{ inspection.installation_name }}</span></div>
            <div class="field"><span class="field-label">Location:</span> <span class="field-value">{{ inspection.location }}</span></div>
            <div class="field"><span class="field-label">Date of Inspection:</span> <span class="field-value">{{ inspection.inspection_date.strftime('%Y-%m-%d') }}</span></div>
        </div>

        {% if inspection.inspectors %}
        <div class="section">
            <h2 class="section-title">Inspectors</h2>
            <div class="inspector-tags">
                {% for inspector in inspection.inspectors %}
                <span class="inspector-tag">{{ inspector.user.full_name if inspector.user else inspector.free_text_name }}</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% if inspection.observations %}
        <div class="section">
            <h2 class="section-title">Observations</h2>
            <div class="field-value">{{ inspection.observations|safe }}</div>
        </div>
        {% endif %}

        {% if inspection.conclusion_text or inspection.conclusion_status %}
        <div class="section">
            <h2 class="section-title">Conclusion</h2>
            {% if inspection.conclusion_status %}
            <div class="field"><span class="field-label">Status:</span>
                <span class="field-value">{{ inspection.conclusion_status|title }}</span>
            </div>
            {% endif %}
            {% if inspection.conclusion_text %}
            <div class="field"><span class="field-label">Comments:</span>
                <div class="field-value">{{ inspection.conclusion_text|safe }}</div>
            </div>
            {% endif %}
        </div>
        {% endif %}

        {% if inspection.photos %}
        <div class="section">
            <h2 class="section-title">Photos</h2>
            <div class="photo-grid">
                {% for photo in inspection.photos %}
                <div class="photo-item">
                    <img src="{{ photo.filename }}" alt="{{ photo.caption }}">
                    <div class="photo-caption">
                        <div><strong>{{ photo.caption }}</strong></div>
                        <div><span class="action-required action-{{ photo.action_required }}">Action Required: {{ photo.action_required|title }}</span></div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <div style="margin-top: 30px; font-size: 10pt; color: #666; text-align: center;">
            <p>Generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M') }}</p>
        </div>
    </body>
    </html>
    """, inspection=inspection, css=css, datetime=datetime)

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    return pdf