"""
Test script for Odoo XML-RPC Integration
This script tests the connection to Odoo and queries for products
"""

import os
import sys
import xmlrpc.client
import json
from datetime import datetime

# Load environment variables (if using .env file)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Odoo Configuration
ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def test_odoo_connection():
    """Test basic connection to Odoo"""
    print("=" * 80)
    print("TEST 1: Odoo Connection & Authentication")
    print("=" * 80)
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        print(f"[->] Connecting to: {ODOO_URL}")
        print(f"[->] Database: {ODOO_DB}")
        print(f"[->] Username: {ODOO_USERNAME}")
        
        # Test version
        version = common.version()
        print(f"[OK] Odoo Version: {version.get('server_version', 'Unknown')}")
        
        # Authenticate
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if uid:
            print(f"[OK] Authentication successful! User ID: {uid}")
            return uid
        else:
            print("[FAIL] Authentication failed! Check credentials.")
            return None
            
    except Exception as e:
        print(f"[ERROR] Connection error: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def test_list_sale_orders(uid, limit=5):
    """Test listing recent sale orders"""
    print("\n" + "=" * 80)
    print("TEST 2: List Recent Sale Orders")
    print("=" * 80)
    
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Get recent sale orders
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[]],
            {'limit': limit, 'order': 'id desc'}
        )
        
        if not order_ids:
            print("[WARN] No sale orders found in database")
            return []
        
        print(f"[OK] Found {len(order_ids)} sale order(s)")
        
        # Get order details
        orders = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order']}
        )
        
        print("\nRecent Sale Orders:")
        for order in orders:
            print(f"  - ID: {order['id']} | Name: {order.get('name', 'N/A')} | "
                  f"Amount: Rs {order.get('amount_total', 0)} | State: {order.get('state', 'N/A')}")
        
        return orders
        
    except Exception as e:
        print(f"[ERROR] Error listing orders: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def test_get_order_products(uid, order_id):
    """Test getting products from a specific sale order"""
    print("\n" + "=" * 80)
    print(f"TEST 3: Get Products from Sale Order ID: {order_id}")
    print("=" * 80)
    
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Check if order exists
        order_exists = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[('id', '=', order_id)]],
            {'limit': 1}
        )
        
        if not order_exists:
            print(f"[FAIL] Sale order {order_id} not found")
            return None
        
        print(f"[OK] Sale order {order_id} found")
        
        # Get order lines (products)
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', order_id)]],
            {
                'fields': ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal', 'name'],
                'limit': 100
            }
        )
        
        if not order_lines:
            print("[WARN] No products found in this order")
            return None
        
        print(f"[OK] Found {len(order_lines)} product(s):\n")
        
        products = []
        for line in order_lines:
            product_id = line.get('product_id', [None])[0] if isinstance(line.get('product_id'), list) else None
            product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) and len(line.get('product_id', [])) > 1 else line.get('name', '')
            
            product_info = {
                'product_id': product_id,
                'product_name': product_name,
                'line_name': line.get('name', ''),
                'quantity': line.get('product_uom_qty', 0),
                'price_unit': line.get('price_unit', 0),
                'price_subtotal': line.get('price_subtotal', 0)
            }
            products.append(product_info)
            
            print(f"  Product ID: {product_id}")
            print(f"  Product Name: {product_name}")
            print(f"  Line Name: {line.get('name', 'N/A')}")
            print(f"  Quantity: {line.get('product_uom_qty', 0)}")
            print(f"  Unit Price: Rs {line.get('price_unit', 0)}")
            print(f"  Subtotal: Rs {line.get('price_subtotal', 0)}")
            
            # Determine product type
            combined_text = f"{product_name} {line.get('name', '')}".lower()
            if any(kw in combined_text for kw in ['harrison', 'harrason', 'harison']):
                product_type = "HARRISON"
            elif 'disc' in combined_text:
                product_type = "DISC"
            else:
                product_type = "UNKNOWN (defaults to DISC)"
            
            print(f"  [->] Detected Type: {product_type}")
            print()
        
        return products
        
    except Exception as e:
        print(f"[ERROR] Error getting products: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def test_search_order_by_name(uid, order_name):
    """Test searching for order by name (e.g., SO-05200-5)"""
    print("\n" + "=" * 80)
    print(f"TEST 4: Search Sale Order by Name: {order_name}")
    print("=" * 80)
    
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[('name', '=', order_name)]],
            {'limit': 1}
        )
        
        if not order_ids:
            print(f"[FAIL] Sale order '{order_name}' not found")
            return None
        
        order_id = order_ids[0]
        print(f"[OK] Found sale order: ID {order_id}")
        
        # Get products
        return test_get_order_products(uid, order_id)
        
    except Exception as e:
        print(f"[ERROR] Error searching order: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return None

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("ODOO XML-RPC INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Connection
    uid = test_odoo_connection()
    if not uid:
        print("\n[FAIL] Cannot proceed - connection failed!")
        return
    
    # Test 2: List orders
    orders = test_list_sale_orders(uid, limit=5)
    
    # Test 3: Get products from a specific order (if provided)
    if len(sys.argv) > 1:
        order_input = sys.argv[1]
        try:
            # Try as integer ID
            order_id = int(order_input)
            test_get_order_products(uid, order_id)
        except ValueError:
            # Try as order name
            test_search_order_by_name(uid, order_input)
    elif orders:
        # Test with first order found
        print("\n" + "=" * 80)
        print("TEST 5: Testing with First Order Found")
        print("=" * 80)
        test_get_order_products(uid, orders[0]['id'])
    
    print("\n" + "=" * 80)
    print("[OK] All tests completed!")
    print("=" * 80)
    print("\nUsage:")
    print("  python test_odoo_connection.py              # Test with first order found")
    print("  python test_odoo_connection.py 35473       # Test with order ID")
    print("  python test_odoo_connection.py SO-05200-5   # Test with order name")

if __name__ == "__main__":
    main()

