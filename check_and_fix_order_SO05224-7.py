"""
Check and Fix Order SO-05224-7
This script will:
1. Check if order exists in Odoo
2. Simulate webhook to process the payment
3. Verify email is sent
"""

import requests
import json
import xmlrpc.client
import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Configuration
BASE_URL = os.environ.get("BASE_URL", "https://bodhih.vercel.app")
WEBHOOK_URL = f"{BASE_URL}/razorpay-webhook"

ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

ORDER_NAME = "SO-05224-7"
AMOUNT = 14.16  # From the image

def check_order_in_odoo(order_name):
    """Check if order exists in Odoo and get details"""
    print("\n" + "=" * 80)
    print("STEP 1: Checking Order in Odoo")
    print("=" * 80)
    print(f"Order Name: {order_name}")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            print("[FAIL] Odoo authentication failed")
            return None
        
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        
        # Try to find order by name (SO-05224-7)
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [[('name', '=', order_name)]],
            {'limit': 1}
        )
        
        if not order_ids:
            print(f"[WARN] Order {order_name} not found in Odoo")
            # Try without the -7 suffix
            order_name_short = order_name.rsplit('-', 1)[0]  # SO-05224
            print(f"[INFO] Trying shortened name: {order_name_short}")
            
            order_ids = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'sale.order', 'search',
                [[('name', '=', order_name_short)]],
                {'limit': 1}
            )
            
            if not order_ids:
                print(f"[FAIL] Order {order_name_short} also not found")
                return None
            
            order_name = order_name_short
        
        order_id = order_ids[0]
        print(f"[OK] Found order: ID {order_id}, Name: {order_name}")
        
        # Get order details
        order = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'read',
            [[order_id]],
            {'fields': ['name', 'date_order', 'amount_total', 'state', 'partner_id', 'note']}
        )[0]
        
        print(f"\nOrder Details:")
        print(f"  ID: {order_id}")
        print(f"  Name: {order.get('name', 'N/A')}")
        print(f"  State: {order.get('state', 'N/A')} [WARNING: Check state]")
        print(f"  Amount: Rs {order.get('amount_total', 0)}")
        print(f"  Date: {order.get('date_order', 'N/A')}")
        
        # Get customer
        partner_id = order.get('partner_id', [None])[0] if isinstance(order.get('partner_id'), list) else None
        customer_name = order.get('partner_id', [None, ''])[1] if isinstance(order.get('partner_id'), list) else 'N/A'
        
        if partner_id:
            partner = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'res.partner', 'read',
                [[partner_id]],
                {'fields': ['name', 'email']}
            )[0]
            customer_email = partner.get('email', 'N/A')
            print(f"  Customer: {partner.get('name', 'N/A')}")
            print(f"  Email: {customer_email}")
        else:
            customer_email = None
            print(f"  Customer: {customer_name}")
        
        # Get products
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', order_id)]],
            {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit'], 'limit': 10}
        )
        
        products = []
        print(f"\nProducts ({len(order_lines)}):")
        for line in order_lines:
            product_name = line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) else line.get('name', 'N/A')
            products.append(product_name)
            print(f"  - {product_name}")
        
        return {
            'order_id': order_id,
            'order_name': order.get('name', order_name),
            'state': order.get('state', 'draft'),
            'customer_email': customer_email,
            'products': products,
            'amount': order.get('amount_total', 0)
        }
        
    except Exception as e:
        print(f"[ERROR] Error checking order: {type(e).__name__}: {e}")
        import traceback
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print("[ERROR] Could not print full error details (encoding issue)")
        return None

def trigger_webhook_manually(order_name, customer_email=None):
    """Manually trigger webhook for this order"""
    print("\n" + "=" * 80)
    print("STEP 2: Triggering Webhook Manually")
    print("=" * 80)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Order: {order_name}")
    
    # Create webhook payload
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": f"pay_manual_{order_name.replace('-', '_')}",
                    "amount": int(AMOUNT * 100),  # Convert to paise
                    "order_id": f"order_manual_{order_name}",
                    "description": order_name,  # Order name in description
                    "contact": "+919876543210",
                    "email": customer_email or "assessments@bodhih.com",
                    "status": "captured",
                    "method": "card",
                    "currency": "INR",
                    "notes": {
                        "name": "Customer",
                        "user_email": customer_email or "assessments@bodhih.com",
                        "gender": "Male",
                        "order_id": order_name
                    }
                }
            }
        }
    }
    
    print(f"\nSending webhook payload:")
    print(json.dumps(payload, indent=2)[:500])
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n[OK] Webhook triggered successfully!")
            print("\nWhat happened:")
            print("  1. Webhook sent to server")
            print("  2. Server should query Odoo for products")
            print("  3. Server should call DISC API")
            print("  4. Server should send email")
            print("  5. Server should update Odoo order status")
            print("\n[INFO] Check:")
            print("  - Server logs for detailed processing")
            print("  - Email inbox for assessment email")
            print("  - Odoo order status (should change to 'sale')")
            return True
        else:
            print(f"\n[FAIL] Webhook returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error triggering webhook: {type(e).__name__}: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def check_razorpay_webhook_status():
    """Check if Razorpay webhook was called"""
    print("\n" + "=" * 80)
    print("STEP 3: Diagnosing Webhook Issue")
    print("=" * 80)
    
    print("\nPossible reasons webhook wasn't called:")
    print("  1. [WARNING] Webhook URL not configured in Razorpay")
    print("  2. [WARNING] payment.captured event not enabled")
    print("  3. [WARNING] Webhook delivery failed (timeout/error)")
    print("  4. [WARNING] Order ID not in payment description")
    
    print("\nHow to check Razorpay webhook:")
    print("  1. Go to Razorpay Dashboard")
    print("  2. Settings -> Webhooks")
    print("  3. Check webhook URL: https://bodhih.vercel.app/razorpay-webhook")
    print("  4. Verify 'payment.captured' event is enabled")
    print("  5. Check webhook delivery logs for this payment")
    
    print("\nHow to check Vercel logs:")
    print("  1. Go to Vercel Dashboard")
    print("  2. Select your project")
    print("  3. Go to 'Logs' or 'Functions' tab")
    print("  4. Look for 'WEBHOOK ENDPOINT HIT' or 'WEBHOOK RECEIVED'")
    print("  5. Check for errors or warnings")

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("CHECK AND FIX ORDER SO-05224-7")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    
    # Step 1: Check order in Odoo
    order_info = check_order_in_odoo(ORDER_NAME)
    
    if not order_info:
        print("\n[FAIL] Cannot proceed - order not found in Odoo")
        print("\nPossible reasons:")
        print("  1. Order ID/Name is incorrect")
        print("  2. Order was created in different Odoo database")
        print("  3. Order was deleted")
        return
    
    # Step 2: Diagnose
    check_razorpay_webhook_status()
    
    # Step 3: Ask user if they want to trigger webhook manually
    print("\n" + "=" * 80)
    response = input("\nDo you want to trigger webhook manually to process this order? (y/n): ")
    
    if response.lower() == 'y':
        customer_email = order_info.get('customer_email') or input("\nEnter customer email (or press Enter for default): ").strip()
        if not customer_email:
            customer_email = "assessments@bodhih.com"
        
        print(f"\nUsing email: {customer_email}")
        success = trigger_webhook_manually(order_info['order_name'], customer_email)
        
        if success:
            print("\n" + "=" * 80)
            print("NEXT STEPS:")
            print("=" * 80)
            print("1. Wait 1-2 minutes")
            print("2. Check email inbox:", customer_email)
            print("3. Check Odoo order status (should be 'sale' now)")
            print("4. Check Vercel logs for detailed processing")
        else:
            print("\n[FAIL] Could not trigger webhook. Check server logs for errors.")
    else:
        print("\n[INFO] Skipping manual webhook trigger")
        print("\nTo trigger manually later, run:")
        print(f"  python check_and_fix_order_SO05224-7.py")
        print("\nOr check Razorpay webhook configuration:")

if __name__ == "__main__":
    main()
