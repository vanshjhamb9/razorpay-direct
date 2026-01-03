"""
Vercel serverless function entry point
This file is required for Vercel to recognize the Flask app as a serverless function
"""

import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the Flask app for Vercel
# Vercel Python runtime automatically handles Flask apps
handler = app


