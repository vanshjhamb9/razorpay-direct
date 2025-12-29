"""
Diagnostic script to test Odoo authentication
Tests different authentication methods to find the correct one
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")

def test_authentication():
    """Test different authentication methods"""
    print("=" * 80)
    print("ODOO AUTHENTICATION DIAGNOSTIC")
    print("=" * 80)
    print(f"Odoo URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Username: {ODOO_USERNAME}")
    print(f"Password: {'*' * len(ODOO_PASSWORD)}")
    print()
    
    # Test 1: Standard authentication with username as-is
    print("TEST 1: Authenticate with username as-is (user ID or email)")
    print("-" * 80)
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        version = common.version()
        print(f"[OK] Odoo Version: {version.get('server_version', 'Unknown')}")
        
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if uid:
            print(f"[OK] Authentication SUCCESSFUL! User ID: {uid}")
            return uid, ODOO_USERNAME
        else:
            print("[FAIL] Authentication failed with username as-is")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    
    print()
    
    # Test 2: Try with user ID as integer
    print("TEST 2: Authenticate with user ID as integer")
    print("-" * 80)
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        user_id_int = int(ODOO_USERNAME) if ODOO_USERNAME.isdigit() else None
        if user_id_int:
            # Try with string representation
            uid = common.authenticate(ODOO_DB, str(user_id_int), ODOO_PASSWORD, {})
            if uid:
                print(f"[OK] Authentication SUCCESSFUL with integer! User ID: {uid}")
                return uid, str(user_id_int)
            else:
                print("[FAIL] Authentication failed with integer")
        else:
            print("[SKIP] Username is not numeric, skipping this test")
    except Exception as e:
        print(f"[ERROR] Error: {type(e).__name__}: {e}")
    
    print()
    
    # Test 3: Try common email patterns
    print("TEST 3: Try common email patterns (if username is numeric)")
    print("-" * 80)
    if ODOO_USERNAME.isdigit():
        common_emails = [
            "admin@bodhih.com",
            "administrator@bodhih.com",
            "info@bodhih.com",
            "support@bodhih.com",
            "odoo@bodhih.com"
        ]
        
        for email in common_emails:
            try:
                common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
                uid = common.authenticate(ODOO_DB, email, ODOO_PASSWORD, {})
                if uid:
                    print(f"[OK] Authentication SUCCESSFUL with email: {email}! User ID: {uid}")
                    return uid, email
                else:
                    print(f"  [FAIL] Failed with: {email}")
            except Exception as e:
                print(f"  [ERROR] Error with {email}: {type(e).__name__}")
    else:
        print("[SKIP] Username is not numeric, skipping email tests")
    
    print()
    print("=" * 80)
    print("[FAIL] All authentication methods failed!")
    print("=" * 80)
    print("\nPossible issues:")
    print("1. Username should be an email address, not user ID")
    print("2. Password might be incorrect")
    print("3. Database name might be incorrect")
    print("4. User might not have XML-RPC access enabled")
    print("\nPlease provide:")
    print("- The email address used to login to Odoo web interface")
    print("- Or verify the password is correct")
    return None, None

if __name__ == "__main__":
    uid, username = test_authentication()
    if uid:
        print(f"\n[SUCCESS] Use this username in your environment: {username}")
        print(f"  Set ODOO_USERNAME={username}")

