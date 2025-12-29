"""
Debug why payment didn't trigger email
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def debug_order_35474():
    """Debug the specific order 35474"""
    print("=" * 80)
    print("Debugging Order 35474 (Recent Purchase)")
    print("=" * 80)
    
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Get order details
        order = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [[35474]],
            {'fields': ['name', 'date_order', 'amount_total', 'state', 'partner_id', 'note']}
        )[0]
        
        print(f"\nOrder Details:")
        print(f"  ID: 35474")
        print(f"  Name: {order.get('name', 'N/A')}")
        print(f"  State: {order.get('state', 'N/A')} (should be 'sale' for confirmed payment)")
        print(f"  Amount: Rs {order.get('amount_total', 0)}")
        print(f"  Date: {order.get('date_order', 'N/A')}")
        
        # Get customer
        partner = order.get('partner_id', [None, ''])[1] if isinstance(order.get('partner_id'), list) else 'N/A'
        partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
        
        if partner_id:
            partner_details = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['name', 'email', 'phone']}
            )[0]
            print(f"\nCustomer Details:")
            print(f"  Name: {partner_details.get('name', 'N/A')}")
            print(f"  Email: {partner_details.get('email', 'N/A')} (email should be sent here)")
            print(f"  Phone: {partner_details.get('phone', 'N/A')}")
        
        # Get products
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', 35474)]],
            {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit']}
        )
        
        print(f"\nProducts in Order:")
        for line in order_lines:
            product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
            print(f"  - {product_name}")
            if 'disc' in product_name.lower():
                print(f"    [DISC] This is a DISC product - should trigger DISC API")
        
        print("\n" + "=" * 80)
        print("DIAGNOSIS:")
        print("=" * 80)
        
        if order.get('state') == 'draft':
            print("\n[ISSUE] Order is still in 'draft' state!")
            print("  [*] Payment might not have been completed")
            print("  [*] Webhook might not have been triggered")
            print("  [*] Order needs to be confirmed in Odoo")
        else:
            print(f"\n[OK] Order state is: {order.get('state')}")
        
        print("\n[CHECKLIST] To fix the issue:")
        print("  1. Verify payment was actually completed in Razorpay")
        print("  2. Check if webhook was called (check Flask server logs)")
        print("  3. Verify Razorpay payment description contains order ID '35474' or 'SO-05224'")
        print("  4. Check if order state changed to 'sale' after payment")
        print("  5. Verify webhook endpoint is accessible: http://your-server/razorpay-webhook")
        
        print("\n[TEST] To test manually:")
        print(f"  curl \"http://localhost:5000/test-odoo?order_id=35474\"")
        print("  This should retrieve products and show what would happen")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_order_35474()

