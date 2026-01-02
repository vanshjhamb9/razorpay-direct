"""
Monitor live payment processing
Helps track what's happening during a real payment
"""

import time
import requests
from datetime import datetime

BASE_URL = "https://bodhih.vercel.app"

def check_endpoint_status():
    """Check if server is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/test-odoo?order_id=35456", timeout=5)
        if response.status_code == 200:
            print("[OK] Server is accessible")
            return True
        else:
            print(f"[WARN] Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot reach server: {e}")
        return False

def monitor_payment_flow():
    """Guide for monitoring payment flow"""
    print("=" * 80)
    print("LIVE PAYMENT MONITORING GUIDE")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check server status
    print("1. Checking server status...")
    if check_endpoint_status():
        print("   [OK] Server is ready for payments")
    else:
        print("   [WARN] Server might have issues")
    
    print("\n" + "=" * 80)
    print("MONITORING CHECKLIST")
    print("=" * 80)
    
    print("\n[BEFORE PAYMENT]:")
    print("  [ ] Open Vercel logs: https://vercel.com/dashboard")
    print("  [ ] Have test order ready (Order ID: 35456 or new order)")
    print("  [ ] Note customer email address")
    print("  [ ] Prepare to make payment")
    
    print("\n[DURING PAYMENT]:")
    print("  [ ] Make payment on Odoo website")
    print("  [ ] Complete Razorpay payment")
    print("  [ ] Note payment ID from confirmation")
    print("  [ ] Watch Vercel logs immediately")
    
    print("\n[AFTER PAYMENT - CHECK LOGS FOR]:")
    print("  [ ] 'WEBHOOK RECEIVED' message")
    print("  [ ] 'Event: payment.captured'")
    print("  [ ] 'Querying Odoo database for order: [order_id]'")
    print("  [ ] 'Successfully retrieved X product(s) from Odoo'")
    print("  [ ] 'Processing Product: [product_name]'")
    print("  [ ] 'Type: DISC' or 'Type: HARRISON'")
    print("  [ ] 'DISC/HARRISON SUCCESS → Link: [url]'")
    print("  [ ] 'EMAIL SENT → [email]'")
    
    print("\n[VERIFY EMAIL]:")
    print("  [ ] Check customer email inbox")
    print("  [ ] Look for email from 'Bodhi Training Solutions'")
    print("  [ ] Subject: 'Your [Report Type] Assessment is Ready!'")
    print("  [ ] Contains assessment link")
    print("  [ ] Contains login credentials")
    print("  [ ] Assessment link works when clicked")
    
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    
    print("\n[ISSUE] If webhook not received:")
    print("  1. Check Razorpay Dashboard -> Webhooks -> Delivery Logs")
    print("  2. Verify webhook URL: https://bodhih.vercel.app/razorpay-webhook")
    print("  3. Ensure 'payment.captured' event is enabled")
    
    print("\n[ISSUE] If order not found:")
    print("  1. Check payment description contains order ID")
    print("  2. Verify order exists in Odoo")
    print("  3. Check order ID format (numeric or SO-XXXXX)")
    
    print("\n[ISSUE] If email not sent:")
    print("  1. Check SMTP settings in Vercel")
    print("  2. Verify customer email is correct")
    print("  3. Check spam folder")
    print("  4. Review email logs in Vercel")
    
    print("\n" + "=" * 80)
    print("QUICK COMMANDS")
    print("=" * 80)
    print("\nTest endpoint:")
    print(f"  curl \"{BASE_URL}/test-odoo?order_id=35456\"")
    print("\nTest webhook manually:")
    print("  python test_deployed_webhook.py 35456")
    print("\nCheck Vercel logs:")
    print("  https://vercel.com/dashboard → Your Project → Logs")
    print("\nCheck Razorpay webhooks:")
    print("  Razorpay Dashboard → Settings → Webhooks → Delivery Logs")
    print("=" * 80)

if __name__ == "__main__":
    monitor_payment_flow()

