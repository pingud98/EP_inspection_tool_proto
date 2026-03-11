#!/usr/bin/env python3

import os
import sys
from app import create_app
from config import Config

# Create and run the application
app = create_app(Config)

if __name__ == '__main__':
    # Run with debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')