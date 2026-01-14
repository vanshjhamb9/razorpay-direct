#!/usr/bin/env python3
"""
Test SMTP connection locally with detailed logging
"""
import smtplib
import os
import sys
from email.message import EmailMessage
import json
from datetime import datetime

# Log path for debug mode
LOG_PATH = r"c:\Users\asus\OneDrive\Desktop\Oddo auto\.cursor\debug.log"

def write_log(location, message, data, hypothesis_id=None):
    """Write debug log in NDJSON format"""
    log_entry = {
        "sessionId": "debug-session",
        "runId": "smtp-test",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Failed to write log: {e}")

def test_smtp_connection(smtp_server, smtp_port, smtp_email, smtp_password, use_ssl=True):
    """Test SMTP connection with detailed logging"""
    location = f"test_smtp_local.py:test_smtp_connection"
    
    write_log(location, "Starting SMTP connection test", {
        "server": smtp_server,
        "port": smtp_port,
        "email": smtp_email,
        "use_ssl": use_ssl
    }, "A")
    
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {smtp_server}:{smtp_port} (SSL: {use_ssl})")
        print(f"Email: {smtp_email}")
        print(f"{'='*60}")
        
        # Test 1: DNS Resolution
        write_log(location, "Testing DNS resolution", {"host": smtp_server}, "B")
        import socket
        try:
            ip = socket.gethostbyname(smtp_server)
            print(f"✓ DNS resolved: {smtp_server} -> {ip}")
            write_log(location, "DNS resolution successful", {"ip": ip}, "B")
        except socket.gaierror as e:
            print(f"✗ DNS resolution failed: {e}")
            write_log(location, "DNS resolution failed", {"error": str(e)}, "B")
            return False
        
        # Test 2: Port Connectivity
        write_log(location, "Testing port connectivity", {"host": smtp_server, "port": smtp_port}, "C")
        try:
            sock = socket.create_connection((smtp_server, smtp_port), timeout=10)
            sock.close()
            print(f"✓ Port {smtp_port} is reachable")
            write_log(location, "Port connectivity successful", {"port": smtp_port}, "C")
        except (socket.timeout, OSError) as e:
            print(f"✗ Port {smtp_port} not reachable: {e}")
            write_log(location, "Port connectivity failed", {"error": str(e), "port": smtp_port}, "C")
            return False
        
        # Test 3: SMTP Connection
        write_log(location, "Attempting SMTP connection", {"method": "SMTP_SSL" if use_ssl else "SMTP_STARTTLS"}, "D")
        if use_ssl:
            print(f"Connecting with SMTP_SSL...")
            s = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            write_log(location, "SMTP_SSL connection established", {}, "D")
        else:
            print(f"Connecting with SMTP (will use STARTTLS)...")
            s = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            write_log(location, "SMTP connection established", {}, "D")
            print("Starting TLS...")
            s.starttls()
            write_log(location, "STARTTLS successful", {}, "D")
        
        print("✓ SMTP connection successful")
        
        # Test 4: Authentication
        write_log(location, "Attempting SMTP authentication", {"email": smtp_email}, "E")
        print(f"Authenticating as {smtp_email}...")
        s.login(smtp_email, smtp_password)
        print("✓ Authentication successful")
        write_log(location, "SMTP authentication successful", {}, "E")
        
        # Test 5: Send Test Email
        write_log(location, "Attempting to send test email", {"to": smtp_email}, "F")
        print(f"Sending test email to {smtp_email}...")
        msg = EmailMessage()
        msg['From'] = smtp_email
        msg['To'] = smtp_email
        msg['Subject'] = "SMTP Test - Local"
        msg.set_content("This is a test email from local SMTP test script.")
        s.send_message(msg)
        print("✓ Test email sent successfully")
        write_log(location, "Test email sent successfully", {}, "F")
        
        s.quit()
        write_log(location, "SMTP test completed successfully", {}, "A")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        write_log(location, "SMTP authentication failed", {"error": str(e)}, "E")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        write_log(location, "SMTP error", {"error": str(e)}, "D")
        return False
    except (TimeoutError, OSError) as e:
        print(f"✗ Connection error: {e}")
        write_log(location, "Connection error", {"error": str(e), "error_type": type(e).__name__}, "C")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        write_log(location, "Unexpected error", {"error": str(e), "error_type": type(e).__name__}, "A")
        import traceback
        write_log(location, "Traceback", {"traceback": traceback.format_exc()}, "A")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("SMTP Connection Test - Local")
    print("="*60)
    
    # Clear previous logs
    if os.path.exists(LOG_PATH):
        try:
            os.remove(LOG_PATH)
            print(f"Cleared previous logs: {LOG_PATH}")
        except Exception as e:
            print(f"Warning: Could not clear logs: {e}")
    
    # Test configurations
    tests = [
        {
            "name": "Inowix (Gmail) - Port 587 (STARTTLS)",
            "server": "smtp.gmail.com",
            "port": 587,
            "email": "info@inowix.in",
            "password": input("Enter Gmail App Password for info@inowix.in: ").strip(),
            "use_ssl": False
        },
        {
            "name": "Inowix (Gmail) - Port 465 (SSL)",
            "server": "smtp.gmail.com",
            "port": 465,
            "email": "info@inowix.in",
            "password": input("Enter Gmail App Password for info@inowix.in (again): ").strip(),
            "use_ssl": True
        },
        {
            "name": "Bodhih - Port 587 (STARTTLS)",
            "server": "mail.bodhih.com",
            "port": 587,
            "email": "assessments@bodhih.com",
            "password": input("Enter password for assessments@bodhih.com: ").strip(),
            "use_ssl": False
        },
        {
            "name": "Bodhih - Port 465 (SSL)",
            "server": "mail.bodhih.com",
            "port": 465,
            "email": "assessments@bodhih.com",
            "password": input("Enter password for assessments@bodhih.com (again): ").strip(),
            "use_ssl": True
        }
    ]
    
    results = []
    for test in tests:
        print(f"\n\n{'#'*60}")
        print(f"Test: {test['name']}")
        print(f"{'#'*60}")
        success = test_smtp_connection(
            test['server'],
            test['port'],
            test['email'],
            test['password'],
            test['use_ssl']
        )
        results.append({
            "name": test['name'],
            "success": success
        })
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{status}: {result['name']}")
    
    print(f"\nDetailed logs saved to: {LOG_PATH}")
    print("\nDone!")

if __name__ == "__main__":
    main()
