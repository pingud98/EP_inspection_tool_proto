#!/usr/bin/env python3
"""
Run the Inspection Reporting Tool application.
"""
import os
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    # Ensure certificates exist
    if not os.path.exists(Config.CERT_PATH) or not os.path.exists(Config.KEY_PATH):
        print("TLS certificates not found. Please run setup.py first.")
        print("Run: python setup.py")
        exit(1)

    # Run the application with SSL
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=(Config.CERT_PATH, Config.KEY_PATH),
        debug=True
    )