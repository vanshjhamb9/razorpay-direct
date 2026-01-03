"""
Vercel serverless function for /razorpay-webhook endpoint
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import Flask app
from main import app

# Vercel expects the Flask app as handler
# The app will handle routing internally
handler = app
