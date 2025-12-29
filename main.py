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
import xmlrpc.client

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

DISC_API_URL       = os.environ.get("DISC_API_URL", "https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih")
DISC_CREDENTIAL    = os.environ.get("DISC_CREDENTIAL", "vezHgzd1EueI3clvF/1kNnMyCITD9UwC")

HARRASON_API_URL   = os.environ.get("HARRASON_API_URL", "")
HARRASON_CREDENTIAL = os.environ.get("HARRASON_CREDENTIAL", "")

SMTP_EMAIL         = os.environ.get("SMTP_EMAIL", "info@inowix.in")
SMTP_PASSWORD      = os.environ.get("SMTP_PASSWORD", "jxrmhihcvqlqojqa")
FROM_NAME          = os.environ.get("FROM_NAME", "Bodhi Training Solutions")
REPLY_TO_EMAIL     = os.environ.get("REPLY_TO_EMAIL", "support@bodhih.com")

RAZORPAY_KEY_ID    = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

# Odoo XML-RPC Configuration
ODOO_URL           = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB            = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME      = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD      = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL    = f"{ODOO_URL}/xmlrpc/2/object"


def get_odoo_products_by_order_id(order_id):
    """Query Odoo database to get products sold in a sale order"""
    if not order_id or not ODOO_URL or not ODOO_DB:
        logging.info(f"[WARN] Cannot query Odoo - missing order_id or Odoo credentials")
        return None
    
    try:
        # Connect to Odoo XML-RPC
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        logging.info(f"-> Connecting to Odoo: {ODOO_URL}")
        logging.info(f"-> Database: {ODOO_DB}, User: {ODOO_USERNAME}")
        
        # Authenticate
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            logging.info(f"[FAIL] Odoo authentication failed")
            return None
        
        logging.info(f"[OK] Odoo authenticated successfully (UID: {uid})")
        
        # Query sale.order.line by order_id
        # First, try to find sale.order by name or id
        # The order_id might be a sale order ID or name
        order_id_int = None
        try:
            order_id_int = int(order_id)
        except ValueError:
            pass
        
        # Search for sale order
        sale_order_domain = []
        if order_id_int:
            sale_order_domain = [('id', '=', order_id_int)]
        else:
            # Try to find by name (e.g., "SO-05200-5")
            sale_order_domain = [('name', '=', str(order_id))]
        
        sale_order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [sale_order_domain],
            {'limit': 1}
        )
        
        if not sale_order_ids:
            logging.info(f"[WARN] Sale order not found in Odoo for order_id: {order_id}")
            return None
        
        sale_order_id = sale_order_ids[0]
        logging.info(f"[OK] Found sale order in Odoo: ID {sale_order_id}")
        
        # Get sale.order.line items for this order
        order_lines = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order.line', 'search_read',
            [[('order_id', '=', sale_order_id)]],
            {
                'fields': ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal', 'name'],
                'limit': 100
            }
        )
        
        if not order_lines:
            logging.info(f"[WARN] No order lines found for sale order {sale_order_id}")
            return None
        
        logging.info(f"[OK] Found {len(order_lines)} product(s) in Odoo order:")
        products = []
        for line in order_lines:
            product_info = {
                'product_id': line.get('product_id', [None])[0] if isinstance(line.get('product_id'), list) else None,
                'product_name': line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) and len(line.get('product_id', [])) > 1 else line.get('name', ''),
                'quantity': line.get('product_uom_qty', 0),
                'price_unit': line.get('price_unit', 0),
                'price_subtotal': line.get('price_subtotal', 0),
                'line_name': line.get('name', '')
            }
            products.append(product_info)
            logging.info(f"  - Product: {product_info['product_name']} (ID: {product_info['product_id']})")
            logging.info(f"    Quantity: {product_info['quantity']}, Price: {product_info['price_unit']}")
        
        return {
            'sale_order_id': sale_order_id,
            'products': products
        }
        
    except Exception as e:
        logging.info(f"[ERROR] Odoo query error: {type(e).__name__}: {e}")
        import traceback
        logging.info(f"-> Traceback: {traceback.format_exc()}")
        return None

def get_order_details(order_id):
    """Fetch order details from Razorpay API to get product information"""
    if not order_id or not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        logging.info(f"[WARN] Cannot fetch order - missing order_id or API credentials")
        return None
    
    try:
        url = f"https://api.razorpay.com/v1/orders/{order_id}"
        auth = (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        logging.info(f"-> Calling Razorpay API: {url}")
        
        response = requests.get(url, auth=auth, timeout=10)
        logging.info(f"-> Razorpay API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            order = response.json()
            logging.info(f"-> Full Order Data from Razorpay:")
            logging.info(json.dumps(order, indent=2)[:1000])
            
            logging.info(f"[OK] Order Details Extracted:")
            logging.info(f"  - Description: {order.get('description', 'N/A')}")
            logging.info(f"  - Amount: {order.get('amount', 'N/A')}")
            logging.info(f"  - Notes: {order.get('notes', {})}")
            logging.info(f"  - Customer ID: {order.get('customer_id', 'N/A')}")
            
            return order
        else:
            logging.info(f"[FAIL] Order fetch failed: HTTP {response.status_code}")
            logging.info(f"-> Response: {response.text[:500]}")
            return None
    except Exception as e:
        logging.info(f"[ERROR] Order fetch error: {type(e).__name__}: {e}")
        return None

def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))


def extract_report_type(description):
    """Extract DISC type from product description - must match DISC API standards"""
    if not description:
        return "Basic"
    
    # Valid DISC types (check longer ones first to avoid partial matches)
    valid_types = [
        "Career entry level",
        "Team Build",
        "Communication",
        "Managerial",
        "Advanced",
        "Student",
        "Career",
        "Sales",
        "Basic",
        "Full"
    ]
    
    desc_lower = description.lower()
    for disc_type in valid_types:
        if disc_type.lower() in desc_lower:
            return disc_type
    
    return "Basic"

def determine_product_type_from_odoo(product_name, product_line_name):
    """Determine if product is DISC or Harrison based on Odoo product information"""
    if not product_name and not product_line_name:
        return "disc"  # Default to DISC
    
    # Combine product name and line name for checking
    combined_text = f"{product_name} {product_line_name}".lower()
    
    # Check for Harrison/Harrason keywords (various spellings)
    harrison_keywords = ['harrison', 'harrason', 'harison', 'harisson']
    for keyword in harrison_keywords:
        if keyword in combined_text:
            logging.info(f"[OK] Product identified as HARRISON: {product_name}")
            return "harrison"
    
    # Check for DISC keywords
    disc_keywords = ['disc', 'diSC', 'DISC']
    for keyword in disc_keywords:
        if keyword in combined_text:
            logging.info(f"[OK] Product identified as DISC: {product_name}")
            return "disc"
    
    # Default to DISC if unclear
    logging.info(f"[WARN] Product type unclear, defaulting to DISC: {product_name}")
    return "disc"

def register_on_disc_asia(name, display_name, email, gender, report_type):
    from datetime import timezone
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
            "transactionId": 1,
            "transactionDate": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            "isSuccessful": True
        }
    }

    try:
        logging.info(f"-> DISC API Call: {DISC_API_URL}")
        logging.info(f"-> Credential: {len(DISC_CREDENTIAL)} chars | {DISC_CREDENTIAL[:20]}...")
        logging.info(f"-> Request: Name={name}, Email={email}, Type={report_type}")
        
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        logging.info(f"-> Response Status: {r.status_code}")
        logging.info(f"-> Response Text: {r.text[:200]}")
        
        if r.status_code != 200:
            logging.info(f"[FAIL] DISC HTTP ERROR {r.status_code}: {r.text[:300]}")
            return None
            
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            link = result["respondentDetails"][0].get("link")
            logging.info(f"[OK] DISC SUCCESS -> Link: {link}")
            return link
        else:
            error = result.get('errorMessage', 'Unknown error')
            logging.info(f"[FAIL] DISC FAILED -> {error}")
            return None
    except Exception as e:
        logging.info(f"[ERROR] DISC ERROR -> {type(e).__name__}: {e}")
        return None

def register_on_harrason(name, display_name, email, gender, report_type):
    from datetime import timezone
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
            "transactionId": 1,
            "transactionDate": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
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
        logging.info(f"EMAIL SENT -> {email}")
    except Exception as e:
        logging.info(f"EMAIL FAILED -> {e}")

def process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, payment_id, description):
    """Process registration and email for a single user"""
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
        send_email(name, user_email, amount, payment_id, report_type, assessment_link, password)
        logging.info(f"[OK] {name}: {api_type} Account Created + Email Sent to {user_email}")
    else:
        logging.info(f"[FAIL] {name}: {api_type} REGISTRATION FAILED - No email sent")

@app.route('/razorpay-webhook', methods=['POST'])
def webhook():
    data = request.get_json(force=True) or {}
    
    # Log ALL webhook calls for debugging
    logging.info("\n" + "=" * 95)
    logging.info("WEBHOOK RECEIVED")
    logging.info("=" * 95)
    logging.info(f"Event: {data.get('event', 'N/A')}")
    logging.info(f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    logging.info(f"Full Payload: {json.dumps(data, indent=2)[:1000]}")
    
    if not data or data.get('event') != 'payment.captured':
        logging.info(f"[SKIP] Event is not 'payment.captured' - ignoring")
        return "ok", 200

    p = data['payload']['payment']['entity']
    notes = p.get('notes', {})
    description  = p.get('description', '')
    amount       = p['amount'] / 100
    order_id     = p.get('order_id', '')
    payment_method = p.get('method', '').upper()

    logging.info("\n" + "═" * 95)
    logging.info("NEW PAYMENT FROM ODOO WEBSITE — BODHIH.COM")
    logging.info("═" * 95)
    logging.info(f"Time           : {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    logging.info(f"Amount         : ₹{amount:,.2f}")
    logging.info(f"Payment ID     : {p['id']}")
    logging.info(f"Order ID       : {order_id}")
    logging.info(f"Phone          : {p.get('contact', '—')}")
    logging.info(f"Payment Method : {payment_method}")
    logging.info(f"Description    : {description}")
    
    # Query Odoo database to get product information
    odoo_order_info = None
    odoo_order_identifier = None
    
    # Try to extract Odoo order identifier from description or notes
    # Description might contain sale order name like "SO-05200-5" or order ID
    if description:
        # Check if description contains sale order pattern (SO-XXXXX-X)
        so_match = re.search(r'SO-[\d-]+', description, re.IGNORECASE)
        if so_match:
            odoo_order_identifier = so_match.group(0)
            logging.info(f"-> Extracted Odoo order identifier from description: {odoo_order_identifier}")
        # Or try to use description as-is if it looks like an order ID
        elif description.strip().isdigit():
            odoo_order_identifier = description.strip()
            logging.info(f"-> Using description as Odoo order ID: {odoo_order_identifier}")
    
    # Also check notes for order identifier
    if isinstance(notes, dict) and not odoo_order_identifier:
        odoo_order_identifier = notes.get('sale_order_id') or notes.get('order_id') or notes.get('odoo_order_id')
        if odoo_order_identifier:
            logging.info(f"-> Found Odoo order identifier in notes: {odoo_order_identifier}")
    
    # Query Odoo if we have an identifier
    if odoo_order_identifier:
        logging.info(f"\n-> Querying Odoo database for order: {odoo_order_identifier}")
        odoo_order_info = get_odoo_products_by_order_id(odoo_order_identifier)
        if odoo_order_info:
            logging.info(f"[OK] Successfully retrieved {len(odoo_order_info.get('products', []))} product(s) from Odoo")
        else:
            logging.info(f"[WARN] Could not retrieve products from Odoo, falling back to Razorpay/notes")
    
    # If no notes, try to fetch order details from Razorpay API
    if not notes or (isinstance(notes, dict) and not notes.get('name')):
        logging.info("-> No product info in notes, fetching from Razorpay Order API...")
        order_details = get_order_details(order_id)
        if order_details:
            order_description = order_details.get('description', description)
            logging.info(f"-> Order description from API: {order_description}")
            product_name = order_description
        else:
            product_name = description
    else:
        product_name = description
    
    # Log raw payload snippet for debugging
    raw_payload = json.dumps(data, indent=2)
    logging.info(f"Full Raw Payload (first 800 chars):")
    logging.info(raw_payload[:800])

    # Process products from Odoo if available
    if odoo_order_info and odoo_order_info.get('products'):
        logging.info(f"\n-> PROCESSING PRODUCTS FROM ODOO DATABASE")
        products = odoo_order_info['products']
        
        # Get customer info from notes or payment entity
        if isinstance(notes, list) and len(notes) > 0:
            # Multiple users - match products to users if possible
            logging.info(f"-> MULTIPLE USERS DETECTED: {len(notes)} users, {len(products)} products")
            for idx, user_data in enumerate(notes):
                if isinstance(user_data, dict):
                    name = user_data.get('name', 'Customer')
                    display_name = name
                    email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                    user_email = user_data.get('user_email', email)
                    gender = user_data.get('gender', 'Male')
                    
                    # Get product for this user (use index or first product)
                    product = products[idx] if idx < len(products) else products[0]
                    product_name = product.get('product_name', product.get('line_name', product_name))
                    product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                    report_type = extract_report_type(product_name)
                    
                    logging.info(f"\n-> Processing User: {name} ({user_email})")
                    logging.info(f"  Product: {product_name} | Type: {product_type.upper()}")
                    process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
        else:
            # Single user - process all products
            name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
            display_name = name
            email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
            user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
            gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
            
            logging.info(f"Customer Name  : {name}")
            logging.info(f"Email          : {email}")
            logging.info(f"Products Found : {len(products)}")
            
            # Process each product from Odoo
            for product in products:
                product_name = product.get('product_name', product.get('line_name', product_name))
                product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                report_type = extract_report_type(product_name)
                
                logging.info(f"\n-> Processing Product: {product_name}")
                logging.info(f"  Type: {product_type.upper()} | Report: {report_type}")
                process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
    
    # Fallback to original logic if Odoo query failed or no products found
    elif not odoo_order_info:
        logging.info(f"\n-> FALLBACK: Using Razorpay/Notes data (Odoo query unavailable)")
        
        # Check if notes is a list (multiple users) or dict (single user)
        if isinstance(notes, list) and len(notes) > 0:
            # Multiple users - process each one
            logging.info(f"\n-> MULTIPLE USERS DETECTED: {len(notes)} users to register")
            for user_data in notes:
                if isinstance(user_data, dict):
                    name = user_data.get('name', 'Customer')
                    display_name = name
                    email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                    user_email = user_data.get('user_email', email)
                    gender = user_data.get('gender', 'Male')
                    user_product_name = user_data.get('product_name', product_name)
                    product_type = user_data.get('product_type', '').lower()
                    report_type = extract_report_type(user_product_name or product_name)
                    
                    logging.info(f"\n-> Processing User: {name} ({user_email})")
                    process_single_user(name, display_name, email, user_email, gender, user_product_name, product_type, report_type, amount, p['id'], description)
        else:
            # Single user - original logic
            name         = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
            display_name = name
            email        = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
            user_email   = (notes.get('user_email') if isinstance(notes, dict) else None) or email
            gender       = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
            product_id   = notes.get('product_id', '') if isinstance(notes, dict) else ''
            product_type = (notes.get('product_type', '') if isinstance(notes, dict) else '').lower()
            report_type = extract_report_type(product_name)

            logging.info(f"Customer Name  : {name}")
            logging.info(f"Email          : {email}")
            logging.info(f"Product ID     : {product_id or '—'}")
            logging.info(f"Product Name   : {product_name or '—'}")
            logging.info(f"Report Type    : {report_type}")
            
            process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)

    logging.info("═" * 95 + "\n")
    return "OK", 200

@app.route('/test-odoo', methods=['GET'])
def test_odoo():
    """Test endpoint to verify Odoo connection and query products"""
    order_id = request.args.get('order_id', '')
    
    if not order_id:
        return {
            "error": "Missing order_id parameter",
            "usage": "/test-odoo?order_id=35473 or /test-odoo?order_id=SO-05200-5",
            "examples": [
                "/test-odoo?order_id=35473",
                "/test-odoo?order_id=SO-05200-5"
            ]
        }, 400
    
    logging.info("\n" + "═" * 95)
    logging.info("TEST ENDPOINT: Testing Odoo Connection")
    logging.info("═" * 95)
    logging.info(f"Order ID: {order_id}")
    
    result = get_odoo_products_by_order_id(order_id)
    
    if result:
        # Determine product types
        products_with_type = []
        for product in result.get('products', []):
            product_type = determine_product_type_from_odoo(
                product.get('product_name', ''),
                product.get('line_name', '')
            )
            products_with_type.append({
                **product,
                'detected_type': product_type.upper()
            })
        
        response = {
            "success": True,
            "sale_order_id": result.get('sale_order_id'),
            "products": products_with_type,
            "message": f"Successfully retrieved {len(products_with_type)} product(s) from Odoo"
        }
        logging.info(f"[OK] Test successful: {len(products_with_type)} products found")
        return response, 200
    else:
        response = {
            "success": False,
            "message": "Failed to retrieve products from Odoo. Check logs for details."
        }
        logging.info("[FAIL] Test failed: Could not retrieve products")
        return response, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))