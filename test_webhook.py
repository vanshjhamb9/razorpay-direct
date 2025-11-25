import requests
import json

WEBHOOK_URL = "http://localhost:5000/razorpay-webhook"

disc_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_TEST123456789",
                "entity": "payment",
                "amount": 525,
                "currency": "INR",
                "status": "captured",
                "order_id": "order_TEST987654321",
                "invoice_id": None,
                "international": False,
                "method": "upi",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                "description": "DISC Self-Awareness Advanced Report",
                "card_id": None,
                "bank": None,
                "wallet": None,
                "vpa": "test@okicici",
                "email": "test@example.com",
                "contact": "+919876543210",
                "customer_id": "cust_TEST123",
                "notes": {
                    "product_id": "101",
                    "product_name": "DISC Self-Awareness Advanced Assessment",
                    "product_type": "disc",
                    "name": "Test User",
                    "user_email": "test@example.com",
                    "gender": "Male"
                }
            }
        }
    }
}

harrason_payload = {
    "entity": "event",
    "account_id": "acc_PtxbfWAGj8D2mC",
    "event": "payment.captured",
    "contains": ["payment"],
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_TEST987654321",
                "entity": "payment",
                "amount": 1050,
                "currency": "INR",
                "status": "captured",
                "order_id": "order_TEST123456789",
                "invoice_id": None,
                "international": False,
                "method": "card",
                "amount_refunded": 0,
                "refund_status": None,
                "captured": True,
                "description": "Harrason Leadership Assessment",
                "card_id": "card_TEST123",
                "bank": None,
                "wallet": None,
                "vpa": None,
                "email": "test2@example.com",
                "contact": "+919876543211",
                "customer_id": "cust_TEST456",
                "notes": {
                    "product_id": "202",
                    "product_name": "Harrason Leadership Assessment",
                    "product_type": "harrason",
                    "name": "Test User 2",
                    "user_email": "test2@example.com",
                    "gender": "Female"
                }
            }
        }
    }
}

print("=" * 80)
print("Testing DISC Assessment Webhook")
print("=" * 80)
response = requests.post(WEBHOOK_URL, json=disc_payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
print()

print("=" * 80)
print("Testing Harrason Assessment Webhook")
print("=" * 80)
response = requests.post(WEBHOOK_URL, json=harrason_payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
print()

print("Check the Flask server logs above to see the detailed processing!")
