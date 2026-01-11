"""
Simple Email Test Script
Tests if SMTP configuration is working and emails can be sent
"""

import smtplib
from email.message import EmailMessage
import os

# SMTP Configuration
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "assessments@bodhih.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "L[E0xV7bE1,Y")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.bodhih.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
FROM_NAME = os.environ.get("FROM_NAME", "Bodhi Training Solutions")

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

def test_send_email(to_email=None):
    """Test sending an email"""
    if not to_email:
        to_email = SMTP_EMAIL  # Send to self by default
    
    print("\n" + "=" * 80)
    print("TEST 2: Send Test Email")
    print("=" * 80)
    print(f"From: {FROM_NAME} <{SMTP_EMAIL}>")
    print(f"To: {to_email}")
    print()
    
    try:
        msg = EmailMessage()
        msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = "Test Email - Automation System"
        
        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;">
            <h2 style="color:#2c3e50;text-align:center;">Test Email Successful!</h2>
            <p>This is a test email from the automation system.</p>
            <p>If you received this email, SMTP configuration is working correctly.</p>
            <hr>
            <p><strong>Test Details:</strong></p>
            <ul>
                <li>SMTP Server: {SMTP_SERVER}:{SMTP_PORT}</li>
                <li>From Email: {SMTP_EMAIL}</li>
                <li>Timestamp: Test email</li>
            </ul>
            <p style="font-size:12px;color:#777;text-align:center;">
                This is a test email from the Bodhi Training Solutions automation system.
            </p>
        </body>
        </html>
        """
        
        msg.set_content("This is a test email from the automation system.")
        msg.add_alternative(html, subtype='html')
        
        print("Sending email...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        
        print(f"[OK] Test email sent successfully to {to_email}!")
        print("[INFO] Check your inbox for the test email")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error sending email: {type(e).__name__}: {e}")
        import traceback
        try:
            print(traceback.format_exc())
        except:
            print("[ERROR] Could not print full error details")
        return False

def test_send_assessment_email(to_email=None):
    """Test sending a sample assessment email (like the real one)"""
    if not to_email:
        to_email = SMTP_EMAIL
    
    print("\n" + "=" * 80)
    print("TEST 3: Send Sample Assessment Email")
    print("=" * 80)
    print(f"To: {to_email}")
    print()
    
    # Sample data (like what would come from webhook)
    name = "Test Customer"
    amount = 14.16
    payment_id = "pay_test_123"
    report_type = "Sales"
    product_name = "Sales Report - DISC"
    assessment_link = "https://discreport.discasiaplus.org/login?token=TEST_TOKEN"
    password = "TestPassword123"
    
    try:
        msg = EmailMessage()
        msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Reply-To'] = "support@bodhih.com"
        msg['Subject'] = f"Your {product_name} is Ready!"
        
        display_product = product_name
        
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
            <p><strong>Login Email:</strong> {to_email}<br>
               <strong>Password:</strong> <code style="background:#eee;padding:8px;font-size:15px;">{password}</code></p>

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
        print("[INFO] Check your inbox - email should show 'Sales Report - DISC' (not 'Basic Assessment')")
        print("[INFO] Email should be from: assessments@bodhih.com")
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
    print("EMAIL TESTING")
    print("=" * 80)
    print("\nTesting SMTP configuration and email sending...")
    print()
    
    # Get email address from user
    test_email = input("Enter email address to send test emails to (press Enter for default): ").strip()
    if not test_email:
        test_email = SMTP_EMAIL
        print(f"Using default: {test_email}")
    
    results = {}
    
    # Test 1: SMTP Connection
    results['connection'] = test_smtp_connection()
    
    if not results['connection']:
        print("\n[FAIL] SMTP connection failed. Cannot proceed with email tests.")
        return
    
    # Test 2: Send Simple Test Email
    results['test_email'] = test_send_email(test_email)
    
    # Test 3: Send Assessment Email
    results['assessment_email'] = test_send_assessment_email(test_email)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  {test_name:20} : {'[OK]' if result else '[FAIL]'} {status}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    
    if all(results.values()):
        print("[OK] All tests passed!")
        print(f"[INFO] Check inbox: {test_email}")
        print("  1. You should receive 2 emails:")
        print("     - Test Email")
        print("     - Sample Assessment Email (shows 'Sales Report - DISC')")
        print("  2. Verify email shows correct product name (not 'Basic Assessment')")
        print("  3. Verify email is from: assessments@bodhih.com")
    else:
        print("[FAIL] Some tests failed. Check error messages above.")
        print("[INFO] Verify SMTP credentials and server configuration")

if __name__ == "__main__":
    main()
