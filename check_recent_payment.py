"""
Check recent orders and payments to debug the issue
"""

import os
import sys
import xmlrpc.client
from datetime import datetime, timedelta

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

def check_recent_orders():
    """Check recent sale orders"""
    print("=" * 80)
    print("Checking Recent Orders in Odoo")
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
        
        # Get very recent orders (last 10)
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[]],
            {'limit': 10, 'order': 'id desc'}
        )
        
        if not order_ids:
            print("[WARN] No orders found")
            return
        
        print(f"[OK] Found {len(order_ids)} recent order(s)\n")
        
        # Get order details
        orders = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'date_order', 'amount_total', 'state', 'partner_id']}
        )
        
        print("Recent Orders:")
        print("-" * 80)
        for order in orders:
            print(f"\nOrder ID: {order['id']}")
            print(f"  Name: {order.get('name', 'N/A')}")
            print(f"  Date: {order.get('date_order', 'N/A')}")
            print(f"  Amount: Rs {order.get('amount_total', 0)}")
            print(f"  State: {order.get('state', 'N/A')}")
            
            # Get customer
            partner = order.get('partner_id', [None, ''])[1] if isinstance(order.get('partner_id'), list) else 'N/A'
            print(f"  Customer: {partner}")
            
            # Try to find payment transactions for this order
            try:
                payment_ids = models.execute_kw(
                    ODOO_DB, uid, ODOO_PASSWORD,
                    'payment.transaction', 'search',
                    [[('sale_order_ids', '=', order['id'])]],
                    {'limit': 5}
                )
                if payment_ids:
                    print(f"  Payment Transactions: {len(payment_ids)}")
                    payments = models.execute_kw(
                        ODOO_DB, uid, ODOO_PASSWORD,
                        'payment.transaction', 'read',
                        [payment_ids],
                        {'fields': ['state', 'acquirer_id', 'reference', 'razorpay_order_id', 'razorpay_payment_id']}
                    )
                    for payment in payments:
                        print(f"    - State: {payment.get('state', 'N/A')}")
                        print(f"      Reference: {payment.get('reference', 'N/A')}")
                        if payment.get('razorpay_order_id'):
                            print(f"      Razorpay Order ID: {payment.get('razorpay_order_id')}")
                        if payment.get('razorpay_payment_id'):
                            print(f"      Razorpay Payment ID: {payment.get('razorpay_payment_id')}")
                else:
                    print(f"  Payment Transactions: None")
            except Exception as e:
                print(f"  Payment Transactions: Could not retrieve ({type(e).__name__})")
            
            # Get products
            order_lines = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order.line', 'search_read',
                [[('order_id', '=', order['id'])]],
                {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit']}
            )
            
            if order_lines:
                print(f"  Products ({len(order_lines)}):")
                for line in order_lines:
                    product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
                    print(f"    - {product_name} (Qty: {line.get('product_uom_qty', 0)})")
            else:
                print(f"  Products: None")
        
        print("\n" + "=" * 80)
        print("Most Recent Order Details:")
        print("=" * 80)
        
        if orders:
            latest_order = orders[0]
            print(f"\nOrder ID: {latest_order['id']}")
            print(f"Name: {latest_order.get('name', 'N/A')}")
            print(f"State: {latest_order.get('state', 'N/A')}")
            
            # Check if this order has the DISC product
            order_lines = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order.line', 'search_read',
                [[('order_id', '=', latest_order['id'])]],
                {'fields': ['product_id', 'name']}
            )
            
            if order_lines:
                print(f"\nProducts in this order:")
                for line in order_lines:
                    product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
                    print(f"  - {product_name}")
                    
                    # Check if it's the DISC product
                    if 'disc' in product_name.lower():
                        print(f"\n[OK] Found DISC product in order {latest_order['id']}")
                        print(f"\nTo test webhook, the Razorpay payment description should contain:")
                        print(f"  - Order ID: {latest_order['id']}")
                        print(f"  - Or Order Name: {latest_order.get('name', 'N/A')}")
    
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_recent_orders()

