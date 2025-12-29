"""
Find an order that has products (order lines) for testing
"""

import os
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def find_orders_with_products():
    """Find orders that have products"""
    print("=" * 80)
    print("Finding Orders with Products")
    print("=" * 80)
    
    try:
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        
        print("[OK] Connected to Odoo")
        
        # Get models
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Get recent orders
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[]],
            {'limit': 20, 'order': 'id desc'}
        )
        
        if not order_ids:
            print("[WARN] No orders found")
            return
        
        print(f"\n[OK] Checking {len(order_ids)} recent orders for products...\n")
        
        orders_with_products = []
        
        for order_id in order_ids:
            # Check if order has order lines
            order_lines = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order.line', 'search',
                [[('order_id', '=', order_id)]],
                {'limit': 1}
            )
            
            if order_lines:
                # Get order details
                order = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order', 'read',
                    [[order_id]],
                    {'fields': ['name', 'amount_total', 'state']}
                )[0]
                
                # Get product details
                lines = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'sale.order.line', 'search_read',
                    [[('order_id', '=', order_id)]],
                    {
                        'fields': ['product_id', 'name', 'product_uom_qty'],
                        'limit': 5
                    }
                )
                
                orders_with_products.append({
                    'id': order_id,
                    'name': order.get('name', 'N/A'),
                    'state': order.get('state', 'N/A'),
                    'amount': order.get('amount_total', 0),
                    'products': lines
                })
        
        if orders_with_products:
            print(f"[OK] Found {len(orders_with_products)} order(s) with products:\n")
            for order in orders_with_products:
                print(f"Order ID: {order['id']}")
                print(f"  Name: {order['name']}")
                print(f"  State: {order['state']}")
                print(f"  Amount: Rs {order['amount']}")
                print(f"  Products ({len(order['products'])}):")
                for line in order['products']:
                    product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
                    print(f"    - {product_name}")
                print()
            
            # Suggest first order for testing
            test_order = orders_with_products[0]
            print("=" * 80)
            print("Test with this order:")
            print(f"  curl \"http://localhost:5000/test-odoo?order_id={test_order['id']}\"")
            print(f"  python test_odoo_connection.py {test_order['id']}")
            print("=" * 80)
        else:
            print("[WARN] No orders with products found in recent orders")
            print("\nYou may need to:")
            print("1. Create a test order in Odoo with products")
            print("2. Or wait for a real order with products to come through")
    
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    find_orders_with_products()

