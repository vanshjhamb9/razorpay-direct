"""
Find orders with Harrison/Harrason products for testing
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def find_harrison_orders():
    """Find orders with Harrison products"""
    print("=" * 80)
    print("Finding Orders with Harrison/Harrason Products")
    print("=" * 80)
    
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        
        print("[OK] Connected to Odoo\n")
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Get recent orders
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[]],
            {'limit': 50, 'order': 'id desc'}
        )
        
        if not order_ids:
            print("[WARN] No orders found")
            return
        
        print(f"[OK] Checking {len(order_ids)} recent orders for Harrison products...\n")
        
        harrison_orders = []
        
        for order_id in order_ids:
            # Get order lines
            order_lines = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order.line', 'search_read',
                [[('order_id', '=', order_id)]],
                {
                    'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit'],
                    'limit': 10
                }
            )
            
            # Check if any product contains harrison/harrason
            has_harrison = False
            harrison_products = []
            
            for line in order_lines:
                product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', '')
                line_name = line.get('name', '')
                combined_text = f"{product_name} {line_name}".lower()
                
                if any(kw in combined_text for kw in ['harrison', 'harrason', 'harison', 'harisson']):
                    has_harrison = True
                    harrison_products.append({
                        'product_name': product_name,
                        'line_name': line_name,
                        'quantity': line.get('product_uom_qty', 0),
                        'price': line.get('price_unit', 0)
                    })
            
            if has_harrison:
                # Get order details
                order = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order', 'read',
                    [[order_id]],
                    {'fields': ['name', 'date_order', 'amount_total', 'state', 'partner_id']}
                )[0]
                
                # Get customer
                partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
                customer_name = "N/A"
                customer_email = "N/A"
                
                if partner_id:
                    partner = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'res.partner', 'read',
                        [[partner_id]],
                        {'fields': ['name', 'email']}
                    )[0]
                    customer_name = partner.get('name', 'N/A')
                    customer_email = partner.get('email', 'N/A')
                
                harrison_orders.append({
                    'id': order_id,
                    'name': order.get('name', 'N/A'),
                    'date': order.get('date_order', 'N/A'),
                    'state': order.get('state', 'N/A'),
                    'amount': order.get('amount_total', 0),
                    'customer': customer_name,
                    'email': customer_email,
                    'products': harrison_products
                })
        
        if harrison_orders:
            print(f"[OK] Found {len(harrison_orders)} order(s) with Harrison products:\n")
            print("=" * 80)
            
            for order in harrison_orders:
                print(f"\nOrder ID: {order['id']}")
                print(f"  Name: {order['name']}")
                print(f"  Date: {order['date']}")
                print(f"  State: {order['state']}")
                print(f"  Amount: Rs {order['amount']}")
                print(f"  Customer: {order['customer']}")
                print(f"  Email: {order['email']}")
                print(f"  Harrison Products ({len(order['products'])}):")
                for product in order['products']:
                    print(f"    - {product['product_name']} (Qty: {product['quantity']}, Price: Rs {product['price']})")
            
            # Suggest first order for testing
            if harrison_orders:
                test_order = harrison_orders[0]
                print("\n" + "=" * 80)
                print("Test with this order:")
                print(f"  curl \"http://localhost:5000/test-odoo?order_id={test_order['id']}\"")
                print(f"  python test_harrison_webhook.py {test_order['id']}")
                print("=" * 80)
        else:
            print("[WARN] No orders with Harrison products found")
            print("\nTo test Harrison integration:")
            print("1. Create a test order in Odoo with a Harrison product")
            print("2. Ensure product name contains 'harrison' or 'harrason'")
            print("3. Run this script again to find the order")
    
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    find_harrison_orders()

