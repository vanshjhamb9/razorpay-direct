"""
Auto-fix Order SO-05224-7
This script automatically triggers the webhook to process the order
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

ORDER_NAME = "SO-05224-7"
AMOUNT = 14.16

def get_order_details():
    """Get order details from Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            return None
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Try SO-05224-7 first, then SO-05224
        for order_name in [ORDER_NAME, "SO-05224"]:
            order_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order', 'search',
                [[('name', '=', order_name)]],
                {'limit': 1}
            )
            if order_ids:
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
                    'order_name': order.get('name', order_name),
                    'customer_email': customer_email or "assessments@bodhih.com"
                }
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def trigger_webhook(order_name, customer_email):
    """Trigger webhook manually"""
    print(f"\nTriggering webhook for order: {order_name}")
    print(f"Customer email: {customer_email}")
    
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_manual_{order_name.replace('-', '_')}",
                    "amount": int(AMOUNT * 100),
                    "order_id": f"order_manual_{order_name}",
                    "description": order_name,
                    "contact": "+919876543210",
                    "email": customer_email,
                    "status": "captured",
                    "method": "card",
                    "currency": "INR",
                    "notes": {
                        "name": "Customer",
                        "user_email": customer_email,
                        "gender": "Male",
                        "order_id": order_name
                    }
                }
            }
        }
    }
    
    try:
        print(f"Sending webhook to: {WEBHOOK_URL}")
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook triggered successfully!")
            print("\nWhat happened:")
            print("  1. Webhook sent to server")
            print("  2. Server should query Odoo for products")
            print("  3. Server should call DISC API")
            print("  4. Server should send email to:", customer_email)
            print("  5. Server should update Odoo order status")
            print("\nPlease check:")
            print("  - Email inbox:", customer_email)
            print("  - Odoo order status (should change to 'sale')")
            print("  - Vercel logs for processing details")
            return True
        else:
            print(f"\n[FAIL] Webhook returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False

def main():
    print("=" * 80)
    print("AUTO-FIX ORDER SO-05224-7")
    print("=" * 80)
    
    # Get order details
    print("\n1. Getting order details from Odoo...")
    order_info = get_order_details()
    
    if not order_info:
        print("[FAIL] Order not found in Odoo")
        return
    
    print(f"[OK] Found order: {order_info['order_name']} (ID: {order_info['order_id']})")
    print(f"[OK] Customer email: {order_info['customer_email']}")
    
    # Trigger webhook
    print("\n2. Triggering webhook manually...")
    success = trigger_webhook(order_info['order_name'], order_info['customer_email'])
    
    if success:
        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print("Webhook was triggered successfully.")
        print("Wait 1-2 minutes and check:")
        print(f"  1. Email inbox: {order_info['customer_email']}")
        print("  2. Odoo order status (should be 'sale' now)")
    else:
        print("\n" + "=" * 80)
        print("FAILED")
        print("=" * 80)
        print("Webhook trigger failed. Check server logs for details.")

if __name__ == "__main__":
    main()
