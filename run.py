#!/usr/bin/env python3

import os
import sys
from app import create_app

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set the configuration
config_name = os.environ.get('FLASK_ENV', 'development')

# Create and run the application
app = create_app(config_name)

if __name__ == '__main__':
    # Check if we're in development mode
    if config_name == 'development':
        # Run with debug mode for development
        app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
    else:
        # Production mode
        app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')