#!/usr/bin/env python3
"""
Simple local test for SMTP email sending
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from main.py
from main import send_email, SMTP_SERVER, SMTP_PORT, SMTP_EMAIL

def test_email():
    """Test sending email locally"""
    print("\n" + "="*60)
    print("Testing SMTP Email Sending Locally")
    print("="*60)
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"SMTP Email: {SMTP_EMAIL}")
    print("="*60 + "\n")
    
    # Test email
    # Note: amount should be in rupees (not paise)
    # Razorpay sends amount in paise, so webhook converts: amount = p['amount'] / 100
    result = send_email(
        name="Test User",
        email="vanshjhamb9@gmail.com",  # Your test email
        amount=1.18,  # ₹1.18 (not 118 paise)
        payment_id="test_pay_123",
        report_type="Communication",
        assessment_link="https://discasiaplus.org/test",
        password="TestPass123",
        product_name="Communication Report - DISC"
    )
    
    if result:
        print("\n[SUCCESS] Email sent successfully!")
    else:
        print("\n[FAILED] Email sending failed. Check logs above.")
    
    print(f"\nDebug logs saved to: .cursor\\debug.log")
    return result

if __name__ == "__main__":
    test_email()
