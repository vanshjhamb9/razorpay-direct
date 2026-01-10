"""
Simple Email Test - No user input required
Tests SMTP and sends test emails automatically
"""

import smtplib
from email.message import EmailMessage
import os
import sys

# SMTP Configuration
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "assessments@bodhih.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "L[E0xV7bE1,Y")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.bodhih.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
FROM_NAME = os.environ.get("FROM_NAME", "Bodhi Training Solutions")

# Get email from command line argument or use default
TEST_EMAIL = sys.argv[1] if len(sys.argv) > 1 else SMTP_EMAIL

def test_smtp_connection():
    """Test SMTP connection"""
    print("=" * 80)
    print("TEST 1: SMTP Connection")
    print("=" * 80)
    print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"Email: {SMTP_EMAIL}")
    print()
    
    try:
        print("Connecting to SMTP server...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            print("[OK] Connected to SMTP server")
            
            print("Authenticating...")
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            print("[OK] SMTP authentication successful")
            
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[FAIL] SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"[FAIL] Could not connect to SMTP server: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return False

def test_send_assessment_email(to_email):
    """Test sending a sample assessment email (like the real one)"""
    print("\n" + "=" * 80)
    print("TEST 2: Send Sample Assessment Email")
    print("=" * 80)
    print(f"From: {FROM_NAME} <{SMTP_EMAIL}>")
    print(f"To: {to_email}")
    print()
    
    # Sample data (like what would come from webhook)
    name = "Test Customer"
    amount = 14.16
    payment_id = "pay_test_123"
    report_type = "Sales"
    product_name = "Sales Report - DISC"  # This should show in email (not "Basic Assessment")
    assessment_link = "https://discreport.discasiaplus.org/login?token=TEST_TOKEN"
    password = "TestPassword123"
    
    try:
        msg = EmailMessage()
        msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Reply-To'] = "support@bodhih.com"
        msg['Subject'] = f"Your {product_name} is Ready!"
        
        display_product = product_name  # This is what will show in email
        
        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;">
            <h2 style="color:#2c3e50;text-align:center;">Payment Confirmed!</h2>
            <p>Dear <strong>{name}</strong>,</p>
            <p>Thank you for purchasing:</p>
            <h3 style="background:#e3f2fd;padding:15px;border-radius:8px;text-align:center;">
                {display_product}
            </h3>
            <p><strong>Amount Paid:</strong> ₹{amount:,.2f}<br>
               <strong>Payment ID:</strong> {payment_id}</p>

            <h3>Your Assessment Access</h3>
            <p style="margin-bottom:10px;"><strong>Login Email:</strong> {to_email}</p>
            <p style="margin-top:10px;margin-bottom:20px;"><strong>Password:</strong> <code style="background:#eee;padding:8px;font-size:15px;">{password}</code></p>

            <div style="text-align:center;margin:30px 0;">
                <a href="{assessment_link}" style="background:#1976d2;color:white;padding:16px 32px;text-decoration:none;border-radius:8px;font-size:18px;">
                    Start Your Assessment Now
                </a>
            </div>

            <p style="background:#fff3cd;padding:15px;border-radius:8px;">
                This link is unique to you. Keep this email safe.
            </p>

            <p style="font-size:12px;color:#777;text-align:center;">
                Need help? Reply to this email.<br>
                Bodhi Training Solutions | www.bodhih.com
            </p>
        </body>
        </html>
        """
        
        msg.set_content("HTML email required.")
        msg.add_alternative(html, subtype='html')
        
        print("Sending assessment email...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        
        print(f"[OK] Assessment email sent successfully to {to_email}!")
        print()
        print("=" * 80)
        print("EMAIL DETAILS TO VERIFY:")
        print("=" * 80)
        print(f"  From: {FROM_NAME} <{SMTP_EMAIL}>")
        print(f"  To: {to_email}")
        print(f"  Subject: Your {product_name} is Ready!")
        print(f"  Product shown in email: {display_product}")
        print()
        print("[IMPORTANT] Verify in your inbox:")
        print(f"  1. Email shows '{product_name}' (NOT 'Basic Assessment')")
        print(f"  2. Email is from: {SMTP_EMAIL}")
        print(f"  3. Email contains assessment link")
        print()
        return True
        
    except Exception as e:
        print(f"[FAIL] Error sending email: {type(e).__name__}: {e}")
        import traceback
        try:
            print(traceback.format_exc())
        except:
            print("[ERROR] Could not print full error details")
        return False

def main():
    """Main test function"""
    print("\n" + "=" * 80)
    print("EMAIL TEST - Automated")
    print("=" * 80)
    print(f"\nTest email will be sent to: {TEST_EMAIL}")
    print("(You can specify different email: python test_email_simple.py your@email.com)")
    print()
    
    results = {}
    
    # Test 1: SMTP Connection
    results['connection'] = test_smtp_connection()
    
    if not results['connection']:
        print("\n" + "=" * 80)
        print("[FAIL] SMTP connection failed. Cannot proceed with email test.")
        print("=" * 80)
        print("\nPossible issues:")
        print("  1. SMTP server is down or not accessible")
        print("  2. SMTP credentials are incorrect")
        print("  3. Firewall blocking connection")
        print("\nCheck:")
        print(f"  - SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"  - SMTP Email: {SMTP_EMAIL}")
        print(f"  - SMTP Password: {'*' * len(SMTP_PASSWORD)}")
        return
    
    # Test 2: Send Assessment Email
    results['email'] = test_send_assessment_email(TEST_EMAIL)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if results['connection']:
        print("  SMTP Connection  : [OK] PASSED")
    else:
        print("  SMTP Connection  : [FAIL] FAILED")
    
    if results.get('email'):
        print("  Send Email       : [OK] PASSED")
        print()
        print("=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"\nEmail was sent successfully to: {TEST_EMAIL}")
        print("\nNext steps:")
        print("  1. Check your email inbox (and spam folder)")
        print(f"  2. Verify email shows: 'Sales Report - DISC' (NOT 'Basic Assessment')")
        print(f"  3. Verify email is from: {SMTP_EMAIL}")
        print("  4. If email is correct, webhook emails will work the same way")
    else:
        print("  Send Email       : [FAIL] FAILED")
        print()
        print("=" * 80)
        print("FAILED")
        print("=" * 80)
        print("\nEmail sending failed. Check error messages above.")

if __name__ == "__main__":
    main()
