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

HARRASON_API_URL   = os.environ.get("HARRASON_API_URL", "")
HARRASON_CREDENTIAL = os.environ.get("HARRASON_CREDENTIAL", "")

SMTP_EMAIL         = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD      = os.environ.get("SMTP_PASSWORD", "")
FROM_NAME          = os.environ.get("FROM_NAME", "Bodhi Training Solutions")
REPLY_TO_EMAIL     = os.environ.get("REPLY_TO_EMAIL", "support@bodhih.com")

ODOO_URL           = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB            = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME      = os.environ.get("ODOO_USERNAME", "")
ODOO_API_KEY       = os.environ.get("ODOO_API_KEY", "")

def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

def query_odoo_sale_order(order_name):
    """Query Odoo API to get sale order and product details"""
    if not ODOO_USERNAME or not ODOO_API_KEY:
        logging.info("Odoo API credentials not configured - skipping Odoo query")
        return None
    
    try:
        import xmlrpc.client
        
        # Odoo XML-RPC endpoints
        common_url = f"{ODOO_URL}/xmlrpc/2/common"
        object_url = f"{ODOO_URL}/xmlrpc/2/object"
        
        # Authenticate
        common = xmlrpc.client.ServerProxy(common_url)
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_API_KEY, {})
        
        if not uid:
            logging.info("Odoo authentication failed")
            return None
        
        # Search for sale order by name
        models = xmlrpc.client.ServerProxy(object_url)
        order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY,
            'sale.order', 'search',
            [[['name', '=', order_name]]]
        )
        
        if not order_ids:
            logging.info(f"Sale order {order_name} not found in Odoo")
            return None
        
        # Read sale order with order lines
        orders = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY,
            'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'partner_id', 'order_line']}
        )
        
        if not orders or not orders[0].get('order_line'):
            logging.info(f"Sale order {order_name} has no order lines")
            return None
        
        order = orders[0]
        
        # Read order lines to get product details
        line_ids = order['order_line']
        lines = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY,
            'sale.order.line', 'read',
            [line_ids],
            {'fields': ['product_id', 'name']}
        )
        
        if not lines:
            return None
        
        # Get first product
        first_line = lines[0]
        product_id = first_line['product_id'][0]
        
        # Read product details
        products = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY,
            'product.product', 'read',
            [[product_id]],
            {'fields': ['id', 'name', 'default_code', 'categ_id']}
        )
        
        if not products:
            return None
        
        product = products[0]
        
        # Read partner details
        partner_id = order['partner_id'][0]
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_API_KEY,
            'res.partner', 'read',
            [[partner_id]],
            {'fields': ['name', 'email', 'phone']}
        )
        
        partner = partners[0] if partners else {}
        
        logging.info(f"Odoo Query Success: Product={product['name']}, Partner={partner.get('name')}")
        
        return {
            'product_id': str(product['id']),
            'product_name': product['name'],
            'product_code': product.get('default_code', ''),
            'category': product.get('categ_id', [None, ''])[1] if product.get('categ_id') else '',
            'partner_name': partner.get('name', ''),
            'partner_email': partner.get('email', ''),
            'partner_phone': partner.get('phone', '')
        }
        
    except Exception as e:
        logging.info(f"Odoo API Error: {e}")
        return None

def determine_product_type_from_odoo(odoo_data):
    """Determine product type (disc/harrason) from Odoo product data"""
    if not odoo_data:
        return "disc"  # Default
    
    product_name = odoo_data.get('product_name', '').lower()
    product_code = odoo_data.get('product_code', '').lower()
    category = odoo_data.get('category', '').lower()
    
    # Check for Harrason keywords
    harrason_keywords = ['harrason', 'harrison']
    for keyword in harrason_keywords:
        if keyword in product_name or keyword in product_code or keyword in category:
            return 'harrason'
    
    # Check for DISC keywords
    disc_keywords = ['disc']
    for keyword in disc_keywords:
        if keyword in product_name or keyword in product_code or keyword in category:
            return 'disc'
    
    # Default to DISC
    return 'disc'

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

def register_on_harrason(name, display_name, email, gender, report_type):
    if not HARRASON_API_URL or not HARRASON_CREDENTIAL:
        logging.info("HARRASON API not configured - skipping")
        return None
    
    payload = {
        "credentials": {"encryptedPassword": HARRASON_CREDENTIAL},
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
        r = requests.post(HARRASON_API_URL, json=payload, timeout=20)
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            link = result["respondentDetails"][0].get("link")
            logging.info(f"HARRASON SUCCESS → {report_type} | Link: {link}")
            return link
        else:
            logging.info(f"HARRASON FAILED → {result.get('errorMessage')}")
            return None
    except Exception as e:
        logging.info(f"HARRASON EXCEPTION → {e}")
        return None

def send_email(name, email, amount, payment_id, report_type, assessment_link, password):
    msg = EmailMessage()
    msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Reply-To'] = REPLY_TO_EMAIL
    msg['Subject'] = f"Your {report_type} Assessment is Ready!"

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;">
        <h2 style="color:#2c3e50;text-align:center;">Payment Confirmed!</h2>
        <p>Dear <strong>{name}</strong>,</p>
        <p>Thank you for purchasing:</p>
        <h3 style="background:#e3f2fd;padding:15px;border-radius:8px;text-align:center;">
            {report_type} Assessment
        </h3>
        <p><strong>Amount Paid:</strong> ₹{amount:,.2f}<br>
           <strong>Payment ID:</strong> {payment_id}</p>

        <h3>Your Assessment Access</h3>
        <p><strong>Login Email:</strong> {email}<br>
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

    # Extract customer data
    name         = notes.get('name', p.get('contact', 'Customer'))
    display_name = name
    email        = p.get('email') or notes.get('user_email', 'no-email@bodhih.com')
    gender       = notes.get('gender', 'Male')
    description  = p.get('description', '')
    amount       = p['amount'] / 100
    order_id     = p.get('order_id', '')
    payment_method = p.get('method', '').upper()
    
    # Extract product details from notes OR query Odoo
    product_id   = notes.get('product_id', '')
    product_name = notes.get('product_name', '')
    product_type = notes.get('product_type', '').lower()
    
    # If product details not in notes, query Odoo using description (SO number)
    odoo_data = None
    if not product_name and description:
        logging.info(f"Product details not in notes - querying Odoo for SO: {description}")
        odoo_data = query_odoo_sale_order(description)
        
        if odoo_data:
            product_id = odoo_data['product_id']
            product_name = odoo_data['product_name']
            product_type = determine_product_type_from_odoo(odoo_data)
            
            # Update customer info from Odoo if not in notes
            if not name or name == 'Customer':
                name = odoo_data.get('partner_name', name)
                display_name = name
            if not email or email == 'no-email@bodhih.com':
                email = odoo_data.get('partner_email', email)
        else:
            # Fallback to description
            product_name = description
    
    # Extract report type from product name
    report_type = extract_report_type(product_name or description)

    # Log payment details
    logging.info("\n" + "═" * 95)
    logging.info("NEW PAYMENT FROM ODOO WEBSITE — BODHIH.COM")
    logging.info("═" * 95)
    logging.info(f"Time           : {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    logging.info(f"Amount         : ₹{amount:,.2f}")
    logging.info(f"Payment ID     : {p['id']}")
    logging.info(f"Order ID       : {order_id}")
    logging.info(f"Customer Name  : {name}")
    logging.info(f"Email          : {email}")
    logging.info(f"Phone          : {p.get('contact', '—')}")
    logging.info(f"Payment Method : {payment_method}")
    logging.info(f"Card/Network   : {p.get('card', {}).get('network', '—') if p.get('card') else '—'}")
    logging.info(f"Description    : {description}")
    logging.info(f"Product ID     : {product_id or '—'}")
    logging.info(f"Product Name   : {product_name or '—'}")
    logging.info(f"Product Type   : {product_type or '—'}")
    logging.info(f"Report Type    : {report_type}")
    
    # Log raw payload snippet for debugging
    raw_payload = json.dumps(data, indent=2)
    logging.info(f"Full Raw Payload (first 800 chars):")
    logging.info(raw_payload[:800])

    # Route to appropriate API based on product type
    assessment_link = None
    api_type = None
    
    if 'harrason' in product_type or 'harrason' in product_name.lower():
        api_type = "HARRASON"
        assessment_link = register_on_harrason(name, display_name, email, gender, report_type)
    elif 'disc' in product_type or 'disc' in product_name.lower() or not product_type:
        api_type = "DISC ASIA+"
        assessment_link = register_on_disc_asia(name, display_name, email, gender, report_type)
    else:
        logging.info(f"UNKNOWN PRODUCT TYPE: {product_type} - defaulting to DISC Asia+")
        api_type = "DISC ASIA+"
        assessment_link = register_on_disc_asia(name, display_name, email, gender, report_type)

    # Send email if registration succeeded
    if assessment_link:
        password = generate_password()
        send_email(name, email, amount, p['id'], report_type, assessment_link, password)
        logging.info(f"SUCCESS: {api_type} Account Created + Email Sent")
    else:
        logging.info(f"{api_type} REGISTRATION FAILED — No email sent")

    logging.info("═" * 95 + "\n")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))