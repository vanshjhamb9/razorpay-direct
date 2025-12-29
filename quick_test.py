"""
Quick test script - tests Odoo connection and shows available orders
Run this first to find order IDs for testing
"""

import os
import sys

# Try to import from main.py
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main import get_odoo_products_by_order_id, ODOO_URL, ODOO_DB
    import xmlrpc.client
except ImportError as e:
    print(f"Error importing: {e}")
    print("Make sure main.py is in the same directory")
    sys.exit(1)

def quick_test():
    """Quick test to find orders and test one"""
    print("=" * 80)
    print("QUICK ODOO CONNECTION TEST")
    print("=" * 80)
    print(f"Odoo URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print()
    
    try:
        # Connect and authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com"), 
                                  os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g"), {})
        
        if not uid:
            print("[FAIL] Authentication failed!")
            return
        
        print("[OK] Connected to Odoo")
        
        # Get recent orders
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        order_ids = models.execute_kw(
            ODOO_DB, uid, os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g"),
            'sale.order', 'search',
            [[]],
            {'limit': 5, 'order': 'id desc'}
        )
        
        if not order_ids:
            print("[WARN] No orders found")
            return
        
        print(f"\n[OK] Found {len(order_ids)} recent order(s):\n")
        
        orders = models.execute_kw(
            ODOO_DB, uid, os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g"),
            'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'amount_total', 'state']}
        )
        
        for order in orders:
            print(f"  ID: {order['id']:6} | Name: {order.get('name', 'N/A'):15} | "
                  f"Amount: Rs {order.get('amount_total', 0):8.2f} | State: {order.get('state', 'N/A')}")
        
        # Test first order
        if order_ids:
            test_order_id = order_ids[0]
            print(f"\n-> Testing order ID: {test_order_id}")
            print("-" * 80)
            
            result = get_odoo_products_by_order_id(str(test_order_id))
            
            if result:
                print(f"\n[OK] Success! Found {len(result.get('products', []))} product(s)")
                for product in result.get('products', []):
                    print(f"  - {product.get('product_name', 'N/A')}")
            else:
                print("\n[FAIL] Failed to retrieve products")
        
        print("\n" + "=" * 80)
        print("To test a specific order, use:")
        print(f"  python test_odoo_connection.py {order_ids[0] if order_ids else 'ORDER_ID'}")
        print(f"  curl 'http://localhost:5000/test-odoo?order_id={order_ids[0] if order_ids else 'ORDER_ID'}'")
        print("=" * 80)
        
    except Exception as e:
        print(f"[ERROR] Error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    quick_test()

