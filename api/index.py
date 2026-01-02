"""
Vercel serverless function entry point
This file is required for Vercel to recognize the Flask app as a serverless function
"""

from main import app

# Export the Flask app for Vercel
handler = app


