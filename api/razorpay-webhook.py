"""
Direct serverless function for webhook endpoint
This ensures the webhook route works properly in Vercel
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export handler for Vercel
# This file handles /razorpay-webhook route specifically
handler = app

