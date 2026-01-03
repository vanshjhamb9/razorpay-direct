"""
Vercel serverless function - Main entry point
Flask app for Vercel deployment
"""

import sys
import os

# Add parent directory to path to import from main.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the Flask app from main.py
from main import app

# Vercel expects 'handler' to be the WSGI application
# Flask app IS a WSGI application, so export it directly
handler = app
