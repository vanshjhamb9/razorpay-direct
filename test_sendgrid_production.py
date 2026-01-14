"""
Test SendGrid email sending with production-like email content
This simulates the exact email that would be sent after a Razorpay payment
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from main import FROM_NAME, SMTP_EMAIL, REPLY_TO_EMAIL, SENDGRID_FROM_EMAIL, write_debug_log

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def main():
    location = "test_sendgrid_production.py:main"

    # Read API key from environment
    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY", "").strip()
    
    # Remove any spaces that might have been added accidentally
    if sendgrid_api_key.startswith("="):
        sendgrid_api_key = sendgrid_api_key[1:].strip()

    if not sendgrid_api_key:
        print("[ERROR] SENDGRID_API_KEY is not set in environment.")
        write_debug_log(location, "SendGrid API key missing", {}, "G")
        return

    # Log that we have the key (but not the key itself)
    write_debug_log(location, "SendGrid API key found", {
        "key_length": len(sendgrid_api_key),
        "key_starts_with": sendgrid_api_key[:5] if len(sendgrid_api_key) >= 5 else "short"
    }, "G")

    to_email = os.environ.get("SENDGRID_TEST_EMAIL", "vanshjhamb9@gmail.com")
    
    # Simulate production email content
    name = "Test User"
    amount = 1.18
    payment_id = "test_pay_123"
    report_type = "Communication"
    display_product = "Communication Report - DISC"
    assessment_link = "https://discasiaplus.org/test"
    password = "TestPass123"

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

    subject = f"Your {display_product} is Ready!"

    # Use the same format as production
    # IMPORTANT: Use SENDGRID_FROM_EMAIL which must be verified in SendGrid dashboard
    from_email_str = f"{FROM_NAME} <{SENDGRID_FROM_EMAIL}>"
    
    write_debug_log(location, "Creating production-like email", {
        "from": from_email_str,
        "to": to_email,
        "subject": subject,
        "reply_to": REPLY_TO_EMAIL
    }, "G")

    try:
        # Create Mail object with HTML content
        message = Mail(
            from_email=from_email_str,
            to_emails=to_email,
            subject=subject,
            html_content=html.strip()  # Strip whitespace to ensure clean HTML
        )
        message.reply_to = REPLY_TO_EMAIL
        
        # Verify HTML was set - SendGrid Mail object stores content internally
        # We'll trust that html_content parameter works (SendGrid API accepts it)
        write_debug_log(location, "Mail object created", {
            "html_provided_length": len(html),
            "subject": subject,
            "from": from_email_str,
            "to": to_email
        }, "G")
        
        write_debug_log(location, "Sending email via SendGrid", {
            "from": from_email_str,
            "to": to_email,
            "subject": subject
        }, "G")
        
        # Log the message object details (without sensitive data)
        write_debug_log(location, "Mail object details", {
            "from_email": str(message.from_email) if hasattr(message, 'from_email') else None,
            "to_emails": str(message.to_emails) if hasattr(message, 'to_emails') else None,
            "subject": str(message.subject) if hasattr(message, 'subject') else None,
            "has_html": bool(message.html_content) if hasattr(message, 'html_content') else False,
            "html_length": len(message.html_content) if hasattr(message, 'html_content') and message.html_content else 0
        }, "G")
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        status_code = response.status_code
        response_headers = dict(response.headers) if hasattr(response, 'headers') else None
        response_body = ""
        if hasattr(response, 'body'):
            try:
                response_body = response.body.decode('utf-8') if isinstance(response.body, bytes) else str(response.body)
            except:
                response_body = str(response.body)[:500]
        
        # Log full response details
        write_debug_log(location, "SendGrid response received", {
            "status_code": status_code,
            "headers": response_headers,
            "body": response_body[:1000] if response_body else None,
            "response_type": type(response).__name__
        }, "G")
        
        # Extract message ID from headers if available
        message_id = None
        if response_headers and 'X-Message-Id' in response_headers:
            message_id = response_headers['X-Message-Id']
        
        if status_code in [200, 202]:
            print(f"[SUCCESS] SendGrid accepted email. Status code: {status_code}")
            print(f"[INFO] Recipient: {to_email}")
            print(f"[INFO] Subject: '{subject}'")
            print(f"[INFO] From: {from_email_str}")
            if message_id:
                print(f"[INFO] SendGrid Message ID: {message_id}")
                print(f"[INFO] Track delivery at: https://app.sendgrid.com/email_activity?message_id={message_id}")
            print(f"[INFO] Check your inbox (and spam/junk folder) for the email")
            print(f"[INFO] SendGrid response body: {response_body[:200] if response_body else 'No body'}")
            print(f"[INFO] Response headers: {list(response_headers.keys()) if response_headers else 'None'}")
            write_debug_log(location, "Email accepted by SendGrid", {
                "to": to_email,
                "status_code": status_code,
                "message_id": message_id,
                "response_body": response_body[:500] if response_body else None,
                "response_headers_keys": list(response_headers.keys()) if response_headers else None
            }, "G")
        else:
            print(f"[ERROR] SendGrid returned status {status_code}")
            print(f"[ERROR] Response body: {response_body[:500]}")
            write_debug_log(location, "SendGrid returned error status", {
                "status_code": status_code,
                "body": response_body[:500]
            }, "G")
            
    except Exception as e:
        error_detail = str(e)
        error_type = type(e).__name__
        
        # Try to extract more details from the exception
        error_info = {"error": error_detail, "error_type": error_type}
        if hasattr(e, 'body'):
            try:
                error_body = e.body.decode('utf-8') if isinstance(e.body, bytes) else str(e.body)
                error_info["body"] = error_body[:500]
            except:
                error_info["body"] = str(e.body)[:500]
        if hasattr(e, 'headers'):
            error_info["headers"] = dict(e.headers)
        
        print(f"[ERROR] SendGrid test failed: {error_detail}")
        if "body" in error_info:
            print(f"[ERROR] Error body: {error_info['body']}")
        import traceback
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        write_debug_log(location, "SendGrid exception", error_info, "G")


if __name__ == "__main__":
    main()
