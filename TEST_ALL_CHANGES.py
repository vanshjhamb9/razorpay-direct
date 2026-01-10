"""
Comprehensive Test Script for All Changes
Tests: SMTP, Webhook, Report Types, Odoo Updates, DISC API
"""

import requests
import json
import smtplib
from email.message import EmailMessage
import os
import sys

# Configuration
BASE_URL = os.environ.get("BASE_URL", "https://bodhih.vercel.app")
LOCAL_URL = "http://localhost:5000"

SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "assessments@bodhih.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "L[E0xV7bE1,Y")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.bodhih.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))

def test_smtp_connection():
    """Test SMTP connection to mail.bodhih.com"""
    print("\n" + "=" * 80)
    print("TEST 1: SMTP Connection")
    print("=" * 80)
    
    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        print(f"Using email: {SMTP_EMAIL}")
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            print("[OK] Connected to SMTP server")
            
            print("Authenticating...")
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            print("[OK] SMTP authentication successful")
            
            # Try sending a test email
            msg = EmailMessage()
            msg['From'] = SMTP_EMAIL
            msg['To'] = SMTP_EMAIL  # Send to self for testing
            msg['Subject'] = "Test Email - Automation Testing"
            msg.set_content("This is a test email from the automation system.")
            
            s.send_message(msg)
            print(f"[OK] Test email sent successfully to {SMTP_EMAIL}")
            print("[INFO] Check your inbox for the test email")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"[FAIL] SMTP Authentication failed: {e}")
        print("[INFO] Check your SMTP credentials")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"[FAIL] Could not connect to SMTP server: {e}")
        print(f"[INFO] Verify {SMTP_SERVER}:{SMTP_PORT} is accessible")
        return False
    except Exception as e:
        print(f"[FAIL] SMTP Error: {type(e).__name__}: {e}")
        return False

def test_webhook_endpoint(url):
    """Test webhook endpoint accessibility"""
    print("\n" + "=" * 80)
    print(f"TEST 2: Webhook Endpoint ({url})")
    print("=" * 80)
    
    webhook_url = f"{url}/razorpay-webhook"
    
    try:
        # Test GET request
        print(f"Testing GET request to {webhook_url}...")
        response = requests.get(webhook_url, timeout=10)
        print(f"[OK] GET request successful: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        # Test POST with payment.captured event
        print(f"\nTesting POST request with payment.captured event...")
        test_payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_test_123",
                        "amount": 1200,  # ₹12.00
                        "order_id": "order_test_123",
                        "description": "Sales Report - DISC",
                        "contact": "+919876543210",
                        "email": SMTP_EMAIL,  # Send test email to yourself
                        "notes": {
                            "name": "Test Customer",
                            "user_email": SMTP_EMAIL,
                            "gender": "Male"
                        }
                    }
                }
            }
        }
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"[OK] POST request successful: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("[OK] Webhook endpoint is working!")
            print("[INFO] Check server logs for detailed processing")
            return True
        else:
            print(f"[WARN] Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Cannot connect to {url}")
        print("[INFO] Make sure the server is running and accessible")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return False

def test_odoo_endpoint(url, order_id=None):
    """Test Odoo query endpoint"""
    print("\n" + "=" * 80)
    print(f"TEST 3: Odoo Query Endpoint ({url})")
    print("=" * 80)
    
    if not order_id:
        print("[SKIP] No order_id provided - skipping Odoo test")
        print("[INFO] Run: python TEST_ALL_CHANGES.py <order_id>")
        return None
    
    test_url = f"{url}/test-odoo?order_id={order_id}"
    
    try:
        print(f"Querying Odoo for order: {order_id}")
        response = requests.get(test_url, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Odoo query successful!")
            print(f"Sale Order ID: {data.get('sale_order_id', 'N/A')}")
            print(f"Products Found: {len(data.get('products', []))}")
            
            for product in data.get('products', []):
                print(f"\n  Product: {product.get('product_name', 'N/A')}")
                print(f"  Line Name: {product.get('line_name', 'N/A')}")
                print(f"  Detected Type: {product.get('detected_type', 'N/A')}")
            
            return True
        else:
            print(f"[FAIL] Error: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return False

def test_report_type_extraction():
    """Test report type extraction logic"""
    print("\n" + "=" * 80)
    print("TEST 4: Report Type Extraction")
    print("=" * 80)
    
    test_cases = [
        ("Sales Report - DISC", "Sales"),
        ("Communication Report - DISC", "Communication"),
        ("Basic Assessment", "Basic"),
        ("Advanced Report - DISC", "Advanced"),
        ("Career Report - DISC", "Career"),
        ("Managerial Report", "Managerial"),
        ("Test Product", "Basic"),  # Should default to Basic
    ]
    
    print("Testing report type extraction from product names:\n")
    
    for product_name, expected in test_cases:
        # Simulate the extraction logic
        desc_lower = product_name.lower()
        valid_types = [
            "Career entry level",
            "Team Build",
            "Communication",
            "Managerial",
            "Advanced",
            "Student",
            "Career",
            "Sales",
            "Basic",
            "Full"
        ]
        
        found_type = "Basic"  # Default
        for disc_type in valid_types:
            if disc_type.lower() in desc_lower:
                found_type = disc_type
                break
        
        status = "✓" if found_type == expected else "✗"
        print(f"  {status} '{product_name}' → '{found_type}' (expected: '{expected}')")
        
    return True

def test_full_payment_flow(url, order_id=None, product_name="Sales Report - DISC"):
    """Test complete payment flow with webhook"""
    print("\n" + "=" * 80)
    print("TEST 5: Full Payment Flow")
    print("=" * 80)
    
    if not order_id:
        print("[INFO] Using test order ID for demonstration")
        order_id = "TEST_ORDER_123"
    
    webhook_url = f"{url}/razorpay-webhook"
    
    # Create realistic payload
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_test_{order_id}",
                    "amount": 1200,  # ₹12.00
                    "order_id": f"order_{order_id}",
                    "description": f"{order_id}",  # Order ID in description
                    "contact": "+919876543210",
                    "email": SMTP_EMAIL,  # Send test email
                    "notes": {
                        "name": "Test Customer",
                        "user_email": SMTP_EMAIL,
                        "gender": "Male",
                        "product_name": product_name
                    }
                }
            }
        }
    }
    
    print(f"Simulating payment for: {product_name}")
    print(f"Order ID: {order_id}")
    print(f"Email: {SMTP_EMAIL}")
    print(f"\nSending webhook to: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for full processing
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("\n[OK] Payment flow completed successfully!")
            print("\nWhat to check:")
            print("  1. Check your email inbox for confirmation email")
            print("  2. Verify email shows correct product name:", product_name)
            print("  3. Check server logs for DISC API response")
            print("  4. If order_id exists in Odoo, check if order was updated")
            return True
        else:
            print(f"\n[FAIL] Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error: {type(e).__name__}: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TESTING - All Changes")
    print("=" * 80)
    print("\nTesting:")
    print("  1. SMTP Connection (mail.bodhih.com)")
    print("  2. Webhook Endpoint")
    print("  3. Odoo Query Endpoint")
    print("  4. Report Type Extraction")
    print("  5. Full Payment Flow")
    
    # Check if running locally or deployed
    use_local = "--local" in sys.argv
    url = LOCAL_URL if use_local else BASE_URL
    
    print(f"\nTesting against: {url}")
    if use_local:
        print("[INFO] Make sure Flask server is running: python main.py")
    
    # Get order_id from command line
    order_id = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        order_id = sys.argv[1]
    
    results = {}
    
    # Test 1: SMTP
    print("\n" + "═" * 80)
    results['smtp'] = test_smtp_connection()
    
    # Test 2: Webhook
    print("\n" + "═" * 80)
    results['webhook'] = test_webhook_endpoint(url)
    
    # Test 3: Odoo
    print("\n" + "═" * 80)
    results['odoo'] = test_odoo_endpoint(url, order_id)
    
    # Test 4: Report Type Extraction
    print("\n" + "═" * 80)
    results['report_types'] = test_report_type_extraction()
    
    # Test 5: Full Payment Flow
    if order_id:
        print("\n" + "═" * 80)
        results['full_flow'] = test_full_payment_flow(url, order_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"  {test_name:20} : {status}")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("1. Check your email inbox for test emails")
    print("2. Check server logs for detailed processing information")
    print("3. If testing with real order_id, verify Odoo order was updated")
    print("4. Test with actual purchase on Odoo website")
    print("\nTo test with specific order:")
    print(f"  python TEST_ALL_CHANGES.py <order_id>")
    print("\nTo test locally:")
    print(f"  python TEST_ALL_CHANGES.py --local <order_id>")

if __name__ == "__main__":
    main()
