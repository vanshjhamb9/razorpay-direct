"""
Test webhook for order SO-05206 (35456) with actual payment data
"""

import requests
import json

WEBHOOK_URL = "http://localhost:5000/razorpay-webhook"

# Simulate actual Razorpay webhook for order SO-05206
webhook_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_SO05206_TEST",
                "entity": "payment",
                "amount": 500,  # Rs 5.00
                "currency": "INR",
                "status": "captured",
                "order_id": "order_SO05206",
                "invoice_id": None,
                "international": False,
                "method": "upi",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                # CRITICAL: Description must contain Odoo order ID or name
                "description": "35456",  # Try with order ID
                # Alternative: "description": "SO-05206",  # Or order name
                "card_id": None,
                "bank": None,
                "wallet": None,
                "vpa": "test@okicici",
                "email": "vanshjhamb9@gmail.com",
                "contact": "+916283075131",
                "customer_id": "cust_SO05206",
                "notes": {
                    "name": "Vansh Jhamb",
                    "user_email": "vanshjhamb9@gmail.com",
                    "gender": "Male"
                    # Optional: Add order ID in notes too
                    # "sale_order_id": "35456"
                }
            }
        }
    }
}

print("=" * 80)
print("Testing Webhook for Order SO-05206 (ID: 35456)")
print("=" * 80)
print(f"\nWebhook URL: {WEBHOOK_URL}")
print(f"Order ID in description: 35456")
print(f"Customer: Vansh Jhamb")
print(f"Email: vanshjhamb9@gmail.com")
print(f"Product: Test - DISC Asia+ Basic Report")
print("\nExpected Flow:")
print("  1. Webhook receives payment.captured event")
print("  2. Extracts order ID '35456' from description")
print("  3. Queries Odoo for order 35456")
print("  4. Finds DISC product")
print("  5. Calls DISC Asia+ API")
print("  6. Sends email to vanshjhamb9@gmail.com")
print("\n" + "=" * 80)
print()

try:
    response = requests.post(WEBHOOK_URL, json=webhook_payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n[OK] Webhook processed!")
        print("\n[IMPORTANT] Check Flask server logs to see:")
        print("  - If Odoo query was successful")
        print("  - Product detection (DISC)")
        print("  - API registration status")
        print("  - Email sending status")
    else:
        print(f"\n[WARN] Status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n[ERROR] Cannot connect to webhook!")
    print("[FIX] Make sure Flask server is running:")
    print("  python main.py")
    print("\nThen run this test again.")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")

print("\n" + "=" * 80)
print("If this test works but real webhook doesn't:")
print("  1. Check Razorpay webhook URL configuration")
print("  2. Verify webhook is accessible from internet (use ngrok)")
print("  3. Check if payment description contains order ID")
print("  4. Verify 'payment.captured' event is enabled in Razorpay")
print("=" * 80)

