"""
Vercel serverless function for /test-odoo route
"""

import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import app

# Export handler
handler = app
