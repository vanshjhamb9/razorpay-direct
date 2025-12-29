"""
Simple test script - enter your Odoo login email to test authentication
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")

def test_with_email(email):
    """Test authentication with email"""
    print("=" * 80)
    print("Testing Odoo Authentication")
    print("=" * 80)
    print(f"Odoo URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Email: {email}")
    print()
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        version = common.version()
        print(f"[OK] Odoo Version: {version.get('server_version', 'Unknown')}")
        
        uid = common.authenticate(ODOO_DB, email, ODOO_PASSWORD, {})
        
        if uid:
            print(f"[SUCCESS] Authentication successful! User ID: {uid}")
            print()
            print("=" * 80)
            print("Use this in your environment variables:")
            print(f"ODOO_USERNAME={email}")
            print("=" * 80)
            return uid
        else:
            print("[FAIL] Authentication failed!")
            print()
            print("Possible reasons:")
            print("1. Email address is incorrect")
            print("2. Password is incorrect")
            print("3. User doesn't have XML-RPC access enabled")
            return None
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        print("Enter your Odoo login email address:")
        email = input("Email: ").strip()
    
    if not email:
        print("Error: Email is required")
        sys.exit(1)
    
    test_with_email(email)

