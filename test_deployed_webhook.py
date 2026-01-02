"""
Test webhook on deployed server with real order data
"""

import requests
import json
import sys

BASE_URL = "https://bodhih.vercel.app"
WEBHOOK_URL = f"{BASE_URL}/razorpay-webhook"

def test_webhook_with_order(order_id, customer_email=None, customer_name=None):
    """Test webhook with specific order"""
    print("=" * 80)
    print(f"Testing Webhook on Deployed Server")
    print("=" * 80)
    print(f"Server: {BASE_URL}")
    print(f"Order ID: {order_id}")
    print()
    
    # Webhook payload
    payload = {
        "entity": "event",
        "account_id": "acc_PtxbfWAGj8D2mC",
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_DEPLOYED_{order_id}",
                    "entity": "payment",
                    "amount": 500,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": f"order_DEPLOYED_{order_id}",
                    "invoice_id": None,
                    "international": False,
                    "method": "upi",
                    "amount_refunded": 0,
                    "refund_status": None,
                    "captured": True,
                    # CRITICAL: Order ID in description
                    "description": str(order_id),
                    "card_id": None,
                    "bank": None,
                    "wallet": None,
                    "vpa": "test@okicici",
                    "email": customer_email or "test@example.com",
                    "contact": "+919876543210",
                    "customer_id": f"cust_DEPLOYED_{order_id}",
                    "notes": {
                        "name": customer_name or "Test Customer",
                        "user_email": customer_email or "test@example.com",
                        "gender": "Male"
                    }
                }
            }
        }
    }
    
    print("Webhook Payload:")
    print(f"  Event: payment.captured")
    print(f"  Description: {order_id}")
    print(f"  Customer: {customer_name or 'Test Customer'}")
    print(f"  Email: {customer_email or 'test@example.com'}")
    print()
    
    try:
        print("Sending webhook request...")
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook processed successfully!")
            print("\n[IMPORTANT] Check server logs to verify:")
            print("  1. Odoo query was executed")
            print("  2. Products were retrieved")
            print("  3. Product type was detected (DISC/Harrison)")
            print("  4. API was called (DISC or Harrison)")
            print("  5. Email was sent (if configured)")
        else:
            print(f"\n[WARN] Unexpected status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out")
        print("Server might be processing or slow to respond")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server")
        print(f"Verify server is accessible: {BASE_URL}")
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        order_id = sys.argv[1]
        customer_email = sys.argv[2] if len(sys.argv) > 2 else None
        customer_name = sys.argv[3] if len(sys.argv) > 3 else None
        test_webhook_with_order(order_id, customer_email, customer_name)
    else:
        print("Usage: python test_deployed_webhook.py [order_id] [email] [name]")
        print("\nExample:")
        print("  python test_deployed_webhook.py 35456")
        print("  python test_deployed_webhook.py 35456 vanshjhamb9@gmail.com 'Vansh Jhamb'")
        print("\nTo test with known order:")
        print("  python test_deployed_webhook.py 35456")







