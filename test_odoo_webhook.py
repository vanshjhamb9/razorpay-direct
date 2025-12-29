"""
Test script for webhook with Odoo integration
This simulates a Razorpay webhook payload with Odoo order information
"""

import requests
import json
import os
import sys

# Get webhook URL
REPLIT_URL = os.environ.get('REPL_SLUG')
if REPLIT_URL:
    WEBHOOK_URL = "http://localhost:5000/razorpay-webhook"
else:
    if len(sys.argv) > 1:
        WEBHOOK_URL = f"{sys.argv[1]}/razorpay-webhook"
    else:
        print("ERROR: Provide your webhook URL")
        print("\nUsage: python test_odoo_webhook.py https://your-url.repl.co")
        print("   OR: python test_odoo_webhook.py  (if running locally)")
        sys.exit(1)

# Test payload with Odoo order ID in description
odoo_order_id_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_ODOO_TEST_001",
                "entity": "payment",
                "amount": 52500,  # ₹525.00
                "currency": "INR",
                "status": "captured",
                "order_id": "order_ODOO_TEST_001",
                "invoice_id": None,
                "international": False,
                "method": "upi",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                # Description contains Odoo order ID - webhook will query Odoo
                "description": "35473",  # Replace with actual Odoo sale order ID
                "card_id": None,
                "bank": None,
                "wallet": None,
                "vpa": "test@okicici",
                "email": "test@example.com",
                "contact": "+919876543210",
                "customer_id": "cust_TEST123",
                "notes": {
                    "name": "Test User",
                    "user_email": "test@example.com",
                    "gender": "Male"
                }
            }
        }
    }
}

# Test payload with Odoo order name in description
odoo_order_name_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_ODOO_TEST_002",
                "entity": "payment",
                "amount": 105000,  # ₹1050.00
                "currency": "INR",
                "status": "captured",
                "order_id": "order_ODOO_TEST_002",
                "invoice_id": None,
                "international": False,
                "method": "card",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                # Description contains Odoo order name - webhook will query Odoo
                "description": "SO-05200-5",  # Replace with actual Odoo sale order name
                "card_id": "card_TEST123",
                "bank": None,
                "wallet": None,
                "vpa": None,
                "email": "test2@example.com",
                "contact": "+919876543211",
                "customer_id": "cust_TEST456",
                "notes": {
                    "name": "Test User 2",
                    "user_email": "test2@example.com",
                    "gender": "Female"
                }
            }
        }
    }
}

# Test payload with order ID in notes
odoo_order_in_notes_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_ODOO_TEST_003",
                "entity": "payment",
                "amount": 75000,  # ₹750.00
                "currency": "INR",
                "status": "captured",
                "order_id": "order_ODOO_TEST_003",
                "invoice_id": None,
                "international": False,
                "method": "netbanking",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                "description": "Payment for Assessment",
                "card_id": None,
                "bank": "HDFC",
                "wallet": None,
                "vpa": None,
                "email": "test3@example.com",
                "contact": "+919876543212",
                "customer_id": "cust_TEST789",
                "notes": {
                    "name": "Test User 3",
                    "user_email": "test3@example.com",
                    "gender": "Male",
                    "sale_order_id": "35473"  # Odoo order ID in notes
                }
            }
        }
    }
}

def test_webhook(payload_name, payload):
    """Test webhook with given payload"""
    print("=" * 80)
    print(f"Testing: {payload_name}")
    print("=" * 80)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Order ID in description: {payload['payload']['payment']['entity'].get('description', 'N/A')}")
    print(f"Order ID in notes: {payload['payload']['payment']['entity'].get('notes', {}).get('sale_order_id', 'N/A')}")
    print()
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Response: {response.text}")
        
        if response.status_code == 200:
            print("✓ Webhook processed successfully!")
            print("\n→ Check the Flask server logs to see:")
            print("  - Odoo connection status")
            print("  - Products retrieved from database")
            print("  - Product type detection (DISC/Harrison)")
            print("  - API registration status")
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out (webhook may be processing)")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    
    print()

def main():
    print("\n" + "=" * 80)
    print("ODOO WEBHOOK INTEGRATION TEST")
    print("=" * 80)
    print("\n⚠ IMPORTANT: Update the order IDs in the payloads before testing!")
    print("   - Replace '35473' with an actual Odoo sale order ID")
    print("   - Replace 'SO-05200-5' with an actual Odoo sale order name")
    print()
    
    # Ask user if they want to proceed
    if len(sys.argv) <= 1:  # Running locally
        response = input("Have you updated the order IDs? (y/n): ")
        if response.lower() != 'y':
            print("Please update the order IDs in this script first!")
            return
    
    # Run tests
    test_webhook("Odoo Order ID in Description", odoo_order_id_payload)
    test_webhook("Odoo Order Name in Description", odoo_order_name_payload)
    test_webhook("Odoo Order ID in Notes", odoo_order_in_notes_payload)
    
    print("=" * 80)
    print("✓ All webhook tests completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Check Flask server logs for Odoo query results")
    print("2. Verify products were retrieved from Odoo")
    print("3. Confirm product type detection (DISC/Harrison)")
    print("4. Check if API registration was successful")

if __name__ == "__main__":
    main()

