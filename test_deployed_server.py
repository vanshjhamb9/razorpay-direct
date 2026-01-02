"""
Comprehensive test suite for deployed server at https://bodhih.vercel.app/
Tests all endpoints and functionality
"""

import requests
import json
import sys

BASE_URL = "https://bodhih.vercel.app"

def test_endpoint(url, method="GET", payload=None, description=""):
    """Test an endpoint and return results"""
    print(f"\n{'=' * 80}")
    print(f"TEST: {description}")
    print(f"{'=' * 80}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=15)
        elif method == "POST":
            response = requests.post(url, json=payload, timeout=15)
        else:
            print(f"[ERROR] Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"[OK] Response: {json.dumps(data, indent=2)[:500]}")
                return True, data
            except:
                print(f"[OK] Response: {response.text[:200]}")
                return True, response.text
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection error - server might be down")
        return False, None
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False, None

def test_root_endpoint():
    """Test root endpoint"""
    url = f"{BASE_URL}/"
    return test_endpoint(url, "GET", None, "Root Endpoint")

def test_health_check():
    """Test if server is responding"""
    url = f"{BASE_URL}/health"
    return test_endpoint(url, "GET", None, "Health Check")

def test_odoo_endpoint_with_order(order_id):
    """Test /test-odoo endpoint with order ID"""
    url = f"{BASE_URL}/test-odoo?order_id={order_id}"
    return test_endpoint(url, "GET", None, f"Odoo Test Endpoint (Order: {order_id})")

def test_webhook_endpoint():
    """Test webhook endpoint with test payload"""
    url = f"{BASE_URL}/razorpay-webhook"
    
    # Test payload for DISC product
    payload = {
        "entity": "event",
        "account_id": "acc_PtxbfWAGj8D2mC",
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_DEPLOYED_TEST",
                    "entity": "payment",
                    "amount": 500,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": "order_DEPLOYED_TEST",
                    "invoice_id": None,
                    "international": False,
                    "method": "upi",
                    "amount_refunded": 0,
                    "refund_status": None,
                    "captured": True,
                    "description": "35456",  # Test order ID
                    "card_id": None,
                    "bank": None,
                    "wallet": None,
                    "vpa": "test@okicici",
                    "email": "test@example.com",
                    "contact": "+919876543210",
                    "customer_id": "cust_DEPLOYED_TEST",
                    "notes": {
                        "name": "Test User",
                        "user_email": "test@example.com",
                        "gender": "Male"
                    }
                }
            }
        }
    }
    
    return test_endpoint(url, "POST", payload, "Webhook Endpoint (Test Payment)")

def test_webhook_invalid_event():
    """Test webhook with invalid event (should return 200 but not process)"""
    url = f"{BASE_URL}/razorpay-webhook"
    
    payload = {
        "entity": "event",
        "event": "payment.failed",  # Not payment.captured
        "payload": {}
    }
    
    return test_endpoint(url, "POST", payload, "Webhook Endpoint (Invalid Event)")

def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("COMPREHENSIVE SERVER TEST SUITE")
    print("=" * 80)
    print(f"Server URL: {BASE_URL}")
    print(f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Root endpoint
    success, _ = test_root_endpoint()
    results["Root Endpoint"] = success
    
    # Test 2: Health check (if exists)
    success, _ = test_health_check()
    results["Health Check"] = success
    
    # Test 3: Odoo endpoint with known DISC order
    print("\n" + "=" * 80)
    print("Testing with Known Orders")
    print("=" * 80)
    
    # Test with order 35456 (SO-05206) - DISC product
    success, data = test_odoo_endpoint_with_order("35456")
    results["Odoo Endpoint (Order 35456 - DISC)"] = success
    if success and isinstance(data, dict):
        products = data.get('products', [])
        if products:
            detected_type = products[0].get('detected_type', '')
            print(f"\n[VERIFY] Product Type Detected: {detected_type}")
            if 'DISC' in detected_type.upper():
                print("[OK] Correctly detected as DISC product!")
            else:
                print("[WARN] Product type might be incorrect")
    
    # Test with order name
    success, _ = test_odoo_endpoint_with_order("SO-05206")
    results["Odoo Endpoint (Order SO-05206)"] = success
    
    # Test 4: Webhook endpoint
    print("\n" + "=" * 80)
    print("Testing Webhook Endpoint")
    print("=" * 80)
    
    success, _ = test_webhook_endpoint()
    results["Webhook Endpoint (Valid)"] = success
    
    # Test 5: Webhook with invalid event
    success, _ = test_webhook_invalid_event()
    results["Webhook Endpoint (Invalid Event)"] = success
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Check server logs for details.")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Verify webhook URL in Razorpay: https://bodhih.vercel.app/razorpay-webhook")
    print("2. Test with real payment")
    print("3. Check server logs for detailed processing")
    print("4. Verify email sending works")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific order
        order_id = sys.argv[1]
        test_odoo_endpoint_with_order(order_id)
    else:
        # Run all tests
        run_all_tests()







