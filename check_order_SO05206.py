"""
Check order SO-05206 which shows payment was made
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def check_order_SO05206():
    """Check the specific order SO-05206"""
    print("=" * 80)
    print("Checking Order SO-05206 (Payment Confirmed)")
    print("=" * 80)
    
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Search for order by name
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[('name', '=', 'SO-05206')]],
            {'limit': 1}
        )
        
        if not order_ids:
            print("[FAIL] Order SO-05206 not found!")
            return
        
        order_id = order_ids[0]
        print(f"[OK] Found order: ID {order_id}\n")
        
        # Get order details
        order = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [[order_id]],
            {'fields': ['name', 'date_order', 'amount_total', 'state', 'partner_id', 'note']}
        )[0]
        
        print(f"Order Details:")
        print(f"  ID: {order_id}")
        print(f"  Name: {order.get('name', 'N/A')}")
        print(f"  State: {order.get('state', 'N/A')}")
        print(f"  Amount: Rs {order.get('amount_total', 0)}")
        print(f"  Date: {order.get('date_order', 'N/A')}")
        
        # Get customer
        partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
        if partner_id:
            partner = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['name', 'email', 'phone']}
            )[0]
            print(f"\nCustomer:")
            print(f"  Name: {partner.get('name', 'N/A')}")
            print(f"  Email: {partner.get('email', 'N/A')}")
            print(f"  Phone: {partner.get('phone', 'N/A')}")
        
        # Get products
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', order_id)]],
            {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit']}
        )
        
        print(f"\nProducts:")
        for line in order_lines:
            product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
            print(f"  - {product_name}")
            if 'disc' in product_name.lower():
                print(f"    [DISC] This should trigger DISC API")
        
        print("\n" + "=" * 80)
        print("WEBHOOK DIAGNOSIS:")
        print("=" * 80)
        print("\n[CHECKLIST] To verify webhook is working:")
        print("  1. Check Flask server logs for webhook calls")
        print("  2. Verify Razorpay webhook URL is configured correctly")
        print("  3. Check if payment description contains order ID or name")
        print("  4. Verify webhook endpoint is accessible from internet")
        print("\n[TEST] Test webhook manually:")
        print(f"  curl \"http://localhost:5000/test-odoo?order_id={order_id}\"")
        print(f"  curl \"http://localhost:5000/test-odoo?order_id=SO-05206\"")
        print("\n[IMPORTANT] For webhook to work:")
        print("  - Razorpay payment description must contain: '{order_id}' or 'SO-05206'")
        print("  - Webhook URL must be accessible: http://your-server/razorpay-webhook")
        print("  - Event 'payment.captured' must be enabled in Razorpay")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_order_SO05206()

