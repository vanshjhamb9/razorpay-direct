"""
Manually test webhook for order 35474 to see what would happen
"""

import requests
import json

WEBHOOK_URL = "http://localhost:5000/razorpay-webhook"

# Simulate payment webhook for order 35474
test_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_TEST_35474",
                "entity": "payment",
                "amount": 500,  # Rs 5.00
                "currency": "INR",
                "status": "captured",
                "order_id": "order_TEST_35474",
                "invoice_id": None,
                "international": False,
                "method": "upi",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                # IMPORTANT: Description contains Odoo order ID
                "description": "35474",  # This will trigger Odoo query
                "card_id": None,
                "bank": None,
                "wallet": None,
                "vpa": "test@okicici",
                "email": "vanshjhamb9@gmail.com",  # Customer email from order
                "contact": "+918769626027",
                "customer_id": "cust_TEST_35474",
                "notes": {
                    "name": "Vansh Jhamb",  # Customer name from order
                    "user_email": "vanshjhamb9@gmail.com",
                    "gender": "Male"
                }
            }
        }
    }
}

print("=" * 80)
print("Testing Webhook for Order 35474")
print("=" * 80)
print(f"\nWebhook URL: {WEBHOOK_URL}")
print(f"Order ID in description: 35474")
print(f"Customer: Vansh Jhamb")
print(f"Email: vanshjhamb9@gmail.com")
print(f"Product: Test - DISC Asia+ Basic Report")
print("\nThis will:")
print("  1. Query Odoo for order 35474")
print("  2. Retrieve products (DISC product)")
print("  3. Detect product type (DISC)")
print("  4. Call DISC Asia+ API")
print("  5. Send email to vanshjhamb9@gmail.com")
print("\n" + "=" * 80)
print()

try:
    response = requests.post(WEBHOOK_URL, json=test_payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n[OK] Webhook processed successfully!")
        print("\nCheck Flask server logs to see:")
        print("  - Odoo query results")
        print("  - Product detection")
        print("  - API registration")
        print("  - Email sending status")
    else:
        print(f"\n[WARN] Unexpected status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Could not connect to webhook!")
    print("Make sure Flask server is running:")
    print("  python main.py")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("Note: This is a test. If email is sent, it will go to vanshjhamb9@gmail.com")
print("=" * 80)

