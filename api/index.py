"""
Vercel serverless function entry point for all other routes
"""
# sys and os 
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)  

# Import Flask app
from main import app

# Vercel expects the Flask app as handler
handler = app
