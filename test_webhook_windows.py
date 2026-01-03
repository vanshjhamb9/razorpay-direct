"""
Test webhook endpoint on Windows
Simple script to test if webhook is receiving requests
"""

import requests
import json

WEBHOOK_URL = "https://bodhih.vercel.app/razorpay-webhook"

def test_webhook():
    """Test webhook endpoint"""
    print("=" * 80)
    print("Testing Webhook Endpoint")
    print("=" * 80)
    print(f"URL: {WEBHOOK_URL}")
    print()
    
    # Test payload
    payload = {
        "entity": "event",
        "account_id": "acc_PtxbfWAGj8D2mC",
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_TEST_WINDOWS",
                    "entity": "payment",
                    "amount": 500,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": "order_TEST",
                    "description": "35456",  # Test order ID
                    "email": "test@example.com",
                    "contact": "+919876543210",
                    "notes": {
                        "name": "Test User",
                        "user_email": "test@example.com",
                        "gender": "Male"
                    }
                }
            }
        }
    }
    
    print("Sending test webhook...")
    print(f"Event: payment.captured")
    print(f"Order ID in description: 35456")
    print()
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook endpoint responded successfully!")
            print("\n[IMPORTANT] Now check Vercel logs:")
            print("  1. Go to Vercel Dashboard")
            print("  2. Select your project 'bodhih'")
            print("  3. Click 'Logs' tab")
            print("  4. Look for:")
            print("     - 'WEBHOOK ENDPOINT HIT'")
            print("     - 'WEBHOOK RECEIVED'")
            print("     - 'Event: payment.captured'")
        else:
            print(f"\n[WARN] Unexpected status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out")
        print("Server might be processing or slow to respond")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server")
        print(f"Verify server is accessible: {WEBHOOK_URL}")
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("1. Check Vercel logs for webhook request")
    print("2. If you see logs, webhook is working!")
    print("3. If no logs, check vercel.json and api/index.py files")
    print("4. Make sure files are committed and deployed")
    print("=" * 80)

if __name__ == "__main__":
    test_webhook()


