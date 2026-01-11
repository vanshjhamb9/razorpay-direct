"""
Fix Order SO-05231-1 - Manual Webhook Trigger
Order was paid but webhook skipped it because event was 'order.paid' instead of 'payment.captured'
"""

import requests
import json
import xmlrpc.client
import os

# Configuration
BASE_URL = os.environ.get("BASE_URL", "https://bodhih.vercel.app")
WEBHOOK_URL = f"{BASE_URL}/razorpay-webhook"

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

ORDER_NAME = "SO-05231-1"
AMOUNT = 1.18
PAYMENT_ID = "pay_S27SAnV0ZuC8Es"

def get_order_details():
    """Get order details from Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            return None
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[('name', '=', ORDER_NAME)]],
            {'limit': 1}
        )
        
        if not order_ids:
            return None
        
        order_id = order_ids[0]
        order = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [[order_id]],
            {'fields': ['name', 'partner_id']}
        )[0]
        
        partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
        customer_email = None
        if partner_id:
            partner = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['email']}
            )[0]
            customer_email = partner.get('email')
        
        return {
            'order_id': order_id,
            'order_name': order.get('name', ORDER_NAME),
            'customer_email': customer_email or "vanshjhamb9@gmail.com"
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def trigger_webhook():
    """Trigger webhook with order.paid event structure"""
    order_info = get_order_details()
    
    if not order_info:
        print(f"[WARN] Order {ORDER_NAME} not found in Odoo, using default email")
        customer_email = "vanshjhamb9@gmail.com"
    else:
        customer_email = order_info['customer_email']
        print(f"[OK] Found order: {order_info['order_name']} (ID: {order_info['order_id']})")
    
    print(f"[OK] Customer email: {customer_email}")
    
    # Create webhook payload matching Razorpay order.paid event structure
    payload = {
        "entity": "event",
        "account_id": "acc_PtxbfWAGj8D2mC",
        "event": "order.paid",  # This is what Razorpay is sending now
        "contains": ["payment", "order"],
        "payload": {
            "payment": {
                "entity": {
                    "id": PAYMENT_ID,
                    "entity": "payment",
                    "amount": int(AMOUNT * 100),  # 118 paise
                    "currency": "INR",
                    "status": "captured",
                    "order_id": "order_S27RpoFSxrCtSe",
                    "invoice_id": None,
                    "international": False,
                    "method": "upi",
                    "amount_refunded": 0,
                    "refund_status": None,
                    "captured": True,
                    "description": ORDER_NAME,  # Order ID in description
                    "card_id": None,
                    "bank": None,
                    "wallet": None,
                    "vpa": "vanshjhamb9-3@okaxis",
                    "email": customer_email,
                    "contact": "+918769626027",
                    "customer_id": "cust_RilPcQXVMuNbGq",
                    "notes": [],
                    "fee": 3,
                    "tax": 0
                }
            }
        }
    }
    
    print(f"\nTriggering webhook for order: {ORDER_NAME}")
    print(f"Sending to: {WEBHOOK_URL}")
    print(f"Event: order.paid")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook triggered successfully!")
            print("\nWhat should happen:")
            print("  1. Webhook processes order.paid event")
            print("  2. Server queries Odoo for products")
            print("  3. Server calls DISC API")
            print("  4. Server sends email to:", customer_email)
            print("  5. Server updates Odoo order status")
            print("\nCheck:")
            print(f"  - Email inbox: {customer_email}")
            print("  - Odoo order status (should change to 'sale')")
            print("  - Vercel logs for processing details")
            return True
        else:
            print(f"\n[FAIL] Webhook returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("FIX ORDER SO-05231-1")
    print("=" * 80)
    print("\nThis order was paid but webhook skipped it because")
    print("Razorpay sent 'order.paid' event instead of 'payment.captured'")
    print("\nNow triggering webhook manually...\n")
    
    trigger_webhook()
