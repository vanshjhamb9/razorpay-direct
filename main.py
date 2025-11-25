# main.py → FINAL AUTOMATION FOR BODHIH.COM (LIVE & PERFECT)
# Razorpay Payment → Extract Type from Product → Register on DISC Asia+ → Send Email

from flask import Flask, request
import requests
from datetime import datetime
import logging
import os
import smtplib
from email.message import EmailMessage
import secrets
import string
import json
import re
import sys

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

DISC_API_URL       = os.environ.get("DISC_API_URL", "https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih")
DISC_CREDENTIAL    = os.environ.get("DISC_CREDENTIAL", "")

SMTP_EMAIL         = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD      = os.environ.get("SMTP_PASSWORD", "")
FROM_NAME          = os.environ.get("FROM_NAME", "Bodhi Training Solutions")
REPLY_TO_EMAIL     = os.environ.get("REPLY_TO_EMAIL", "support@bodhih.com")

def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

def extract_report_type(description):
    """Extract type from product name like 'Self-Awareness Advanced Report' → 'Self-Awareness Advanced'"""
    if not description:
        return "Basic"
    
    # Remove common words
    text = description.replace("DISC", "").replace("Report", "").replace("report", "")
    # Get everything before "Report"
    match = re.search(r"(.+?)(?:\s+Report|$)", description, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
        return cleaned if cleaned else "Basic"
    return "Basic"

def register_on_disc_asia(name, display_name, email, gender, report_type):
    payload = {
        "credentials": {"encryptedPassword": DISC_CREDENTIAL},
        "respondentDetails": [{
            "name": name,
            "displayName": display_name,
            "gender": gender.title(),
            "eMailAddress": email,
            "type": report_type
        }],
        "transactionDetails": {
            "transactionId": 0,
            "transactionDate": datetime.now().isoformat(),
            "isSuccessful": True
        }
    }

    try:
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            link = result["respondentDetails"][0].get("link")
            logging.info(f"DISC SUCCESS → {report_type} | Link: {link}")
            return link
        else:
            logging.info(f"DISC FAILED → {result.get('errorMessage')}")
            return None
    except Exception as e:
        logging.info(f"DISC EXCEPTION → {e}")
        return None

def send_email(name, email, amount, payment_id, report_type, disc_link, password):
    msg = EmailMessage()
    msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Reply-To'] = REPLY_TO_EMAIL
    msg['Subject'] = f"Your {report_type} DISC Report is Ready!"

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;">
        <h2 style="color:#2c3e50;text-align:center;">Payment Confirmed!</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>Thank you for purchasing:</p>
        <h3 style="background:#e3f2fd;padding:15px;border-radius:8px;text-align:center;">
            {report_type} Report
        </h3>
        <p><strong>Amount Paid:</strong> ₹{amount:,.2f}<br>
           <strong>Payment ID:</strong> {payment_id}</p>

        <h3>Your DISC Assessment Access</h3>
        <p><strong>Login Email:</strong> {email}<br>
           <strong>Password:</strong> <code style="background:#eee;padding:8px;font-size:15px;">{password}</code></p>

        <div style="text-align:center;margin:30px 0;">
            <a href="{disc_link}" style="background:#1976d2;color:white;padding:16px 32px;text-decoration:none;border-radius:8px;font-size:18px;">
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

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        logging.info(f"EMAIL SENT → {email}")
    except Exception as e:
        logging.info(f"EMAIL FAILED → {e}")

@app.route('/razorpay-webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True) or {}
    if not data or data.get('event') != 'payment.captured':
        return "ok", 200

    p = data['payload']['payment']['entity']
    notes = p.get('notes', {})

    # Extract data
    name         = notes.get('name', p.get('customer_name', 'Customer'))
    display_name = name  # Same as name
    email        = p.get('email') or notes.get('user_email', 'no-email@bodhih.com')
    gender       = notes.get('gender', 'Male')
    description  = p.get('description', '')
    amount       = p['amount'] / 100

    # Extract report type from product name
    report_type = extract_report_type(description)

    logging.info("\n" + "═" * 95)
    logging.info("FULL AUTOMATION LIVE — BODHIH.COM")
    logging.info("═" * 95)
    logging.info(f"Time         : {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    logging.info(f"Name         : {name}")
    logging.info(f"Email        : {email}")
    logging.info(f"Product      : {description}")
    logging.info(f"Report Type  : {report_type}")
    logging.info(f"Amount       : ₹{amount:,.2f}")
    logging.info(f"Payment ID   : {p['id']}")

    # Register on DISC Asia+
    disc_link = register_on_disc_asia(name, display_name, email, gender, report_type)

    if disc_link:
        password = generate_password()
        send_email(name, email, amount, p['id'], report_type, disc_link, password)
        logging.info("SUCCESS: DISC Account Created + Email Sent")
    else:
        logging.info("DISC REGISTRATION FAILED — No email sent")

    logging.info("═" * 95 + "\n")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))