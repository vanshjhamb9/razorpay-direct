"""
Test webhook for Harrison products
Usage: python test_harrison_webhook.py [order_id]
"""

import requests
import json
import sys
import os
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

WEBHOOK_URL = "http://localhost:5000/razorpay-webhook"

def get_order_details_from_odoo(order_id):
    """Get order details from Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            return None
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Try as integer first
        try:
            order_id_int = int(order_id)
            order_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order', 'search',
                [[('id', '=', order_id_int)]],
                {'limit': 1}
            )
        except ValueError:
            # Try as order name
            order_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order', 'search',
                [[('name', '=', order_id)]],
                {'limit': 1}
            )
        
        if not order_ids:
            return None
        
        order_id_found = order_ids[0]
        
        # Get order details
        order = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [[order_id_found]],
            {'fields': ['name', 'amount_total', 'partner_id']}
        )[0]
        
        # Get customer
        partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
        customer_name = "Test Customer"
        customer_email = "test@example.com"
        
        if partner_id:
            partner = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['name', 'email', 'phone']}
            )[0]
            customer_name = partner.get('name', 'Test Customer')
            customer_email = partner.get('email', 'test@example.com')
        
        # Get products
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', order_id_found)]],
            {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit']}
        )
        
        return {
            'order_id': order_id_found,
            'order_name': order.get('name', 'N/A'),
            'amount': order.get('amount_total', 0),
            'customer_name': customer_name,
            'customer_email': customer_email,
            'products': order_lines
        }
    except Exception as e:
        print(f"[ERROR] Could not fetch order details: {e}")
        return None

def test_harrison_webhook(order_id=None):
    """Test webhook with Harrison product"""
    print("=" * 80)
    print("Testing Webhook for Harrison Product")
    print("=" * 80)
    
    # Get order details if order_id provided
    order_details = None
    if order_id:
        print(f"\nFetching order details for: {order_id}")
        order_details = get_order_details_from_odoo(order_id)
        
        if order_details:
            print(f"[OK] Found order: {order_details['order_name']}")
            print(f"  Customer: {order_details['customer_name']}")
            print(f"  Email: {order_details['customer_email']}")
            print(f"  Products: {len(order_details['products'])}")
            for line in order_details['products']:
                product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
                print(f"    - {product_name}")
        else:
            print(f"[WARN] Could not fetch order details, using default values")
    
    # Create webhook payload
    if order_details:
        order_id_value = str(order_details['order_id'])
        customer_name = order_details['customer_name']
        customer_email = order_details['customer_email']
        amount = int(order_details['amount'] * 100)  # Convert to paise
    else:
        # Default test values
        order_id_value = "TEST_HARRISON_ORDER"
        customer_name = "Test Customer"
        customer_email = "test@example.com"
        amount = 100000  # Rs 1000.00
    
    webhook_payload = {
        "entity": "event",
        "account_id": "acc_PtxbfWAGj8D2mC",
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_HARRISON_TEST",
                    "entity": "payment",
                    "amount": amount,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": "order_HARRISON_TEST",
                    "invoice_id": None,
                    "international": False,
                    "method": "card",
                    "amount_refunded": 0,
                    "refund_status": None,
                    "captured": True,
                    # CRITICAL: Description must contain Odoo order ID
                    "description": order_id_value,  # Order ID or name
                    "card_id": "card_HARRISON_TEST",
                    "bank": None,
                    "wallet": None,
                    "vpa": None,
                    "email": customer_email,
                    "contact": "+919876543210",
                    "customer_id": "cust_HARRISON_TEST",
                    "notes": {
                        "name": customer_name,
                        "user_email": customer_email,
                        "gender": "Male"
                    }
                }
            }
        }
    }
    
    print(f"\nWebhook URL: {WEBHOOK_URL}")
    print(f"Order ID in description: {order_id_value}")
    print(f"Customer: {customer_name}")
    print(f"Email: {customer_email}")
    print(f"Amount: Rs {amount / 100}")
    
    print("\nExpected Flow:")
    print("  1. Webhook receives payment.captured event")
    print(f"  2. Extracts order ID '{order_id_value}' from description")
    print("  3. Queries Odoo for order")
    print("  4. Finds Harrison product")
    print("  5. Routes to HARRISON API (not DISC)")
    print(f"  6. Sends email to {customer_email}")
    
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
            print("  - Product detection (should be HARRISON, not DISC)")
            print("  - HARRISON API registration status")
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
    print("Verification:")
    print("=" * 80)
    print("1. Check Flask logs for 'HARRISON' (not 'DISC')")
    print("2. Verify HARRISON API was called")
    print("3. Check email was sent to customer")
    print("=" * 80)

if __name__ == "__main__":
    order_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if order_id:
        test_harrison_webhook(order_id)
    else:
        print("Usage: python test_harrison_webhook.py [order_id]")
        print("\nOr run without order_id to use default test values")
        print("Example: python test_harrison_webhook.py 35456")
        print("\nTo find Harrison orders, run: python find_harrison_orders.py")
        
        response = input("\nDo you want to test with default values? (y/n): ")
        if response.lower() == 'y':
            test_harrison_webhook()

