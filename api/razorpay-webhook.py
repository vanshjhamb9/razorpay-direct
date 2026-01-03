"""
Vercel serverless function for /razorpay-webhook
Completely standalone - no Flask dependency
"""

import sys
import os
import json
import logging
import requests
import xmlrpc.client
import re
from datetime import datetime
import smtplib
from email.message import EmailMessage
import secrets
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Environment variables
ODOO_URL = os.environ.get("ODOO_URL", "https://bodhih.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "bodhih")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "siddharthan@bodhih.com")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "-KsZAxbX2!Fn36g")
ODOO_XMLRPC_URL = f"{ODOO_URL}/xmlrpc/2/object"

DISC_API_URL = os.environ.get("DISC_API_URL", "https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih")
DISC_CREDENTIAL = os.environ.get("DISC_CREDENTIAL", "vezHgzd1EueI3clvF/1kNnMyCITD9UwC")

HARRASON_API_URL = os.environ.get("HARRASON_API_URL", "")
HARRASON_CREDENTIAL = os.environ.get("HARRASON_CREDENTIAL", "")

SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "info@inowix.in")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "jxrmhihcvqlqojqa")
FROM_NAME = os.environ.get("FROM_NAME", "Bodhi Training Solutions")
REPLY_TO_EMAIL = os.environ.get("REPLY_TO_EMAIL", "support@bodhih.com")

def get_odoo_products_by_order_id(order_id):
    """Query Odoo database to get products sold in a sale order"""
    if not order_id or not ODOO_URL or not ODOO_DB:
        logger.info("Cannot query Odoo - missing order_id or Odoo credentials")
        return None
    
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        logger.info(f"Connecting to Odoo: {ODOO_URL}")
        
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            logger.info("Odoo authentication failed")
            return None
        
        logger.info(f"Odoo authenticated successfully (UID: {uid})")
        
        order_id_int = None
        try:
            order_id_int = int(order_id)
        except ValueError:
            pass
        
        sale_order_domain = []
        if order_id_int:
            sale_order_domain = [('id', '=', order_id_int)]
        else:
            sale_order_domain = [('name', '=', str(order_id))]
        
        sale_order_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'sale.order', 'search',
            [sale_order_domain],
            {'limit': 1}
        )
        
        if not sale_order_ids:
            logger.info(f"Sale order not found in Odoo for order_id: {order_id}")
            return None
        
        sale_order_id = sale_order_ids[0]
        logger.info(f"Found sale order in Odoo: ID {sale_order_id}")
        
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
            logger.info(f"No order lines found for sale order {sale_order_id}")
            return None
        
        logger.info(f"Found {len(order_lines)} product(s) in Odoo order:")
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
            logger.info(f"  - Product: {product_info['product_name']} (ID: {product_info['product_id']})")
        
        return {
            'sale_order_id': sale_order_id,
            'products': products
        }
        
    except Exception as e:
        logger.error(f"Odoo query error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def determine_product_type_from_odoo(product_name, product_line_name):
    """Determine if product is DISC or Harrison"""
    if not product_name and not product_line_name:
        return "disc"
    
    combined_text = f"{product_name} {product_line_name}".lower()
    
    harrison_keywords = ['harrison', 'harrason', 'harison', 'harisson']
    for keyword in harrison_keywords:
        if keyword in combined_text:
            logger.info(f"Product identified as HARRISON: {product_name}")
            return "harrison"
    
    if 'disc' in combined_text:
        logger.info(f"Product identified as DISC: {product_name}")
        return "disc"
    
    logger.info(f"Product type unclear, defaulting to DISC: {product_name}")
    return "disc"

def extract_report_type(description):
    """Extract DISC type from product description"""
    if not description:
        return "Basic"
    
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

def register_on_disc_asia(name, display_name, email, gender, report_type):
    """Register user on DISC Asia+ API"""
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
        logger.info(f"DISC API Call: {DISC_API_URL}")
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        logger.info(f"Response Status: {r.status_code}")
        
        if r.status_code != 200:
            logger.info(f"DISC HTTP ERROR {r.status_code}: {r.text[:300]}")
            return None
        
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            link = result["respondentDetails"][0].get("link")
            logger.info(f"DISC SUCCESS -> Link: {link}")
            return link
        else:
            error = result.get('errorMessage', 'Unknown error')
            logger.info(f"DISC FAILED -> {error}")
            return None
    except Exception as e:
        logger.error(f"DISC ERROR -> {type(e).__name__}: {e}")
        return None

def register_on_harrason(name, display_name, email, gender, report_type):
    """Register user on Harrason API"""
    from datetime import timezone
    if not HARRASON_API_URL or not HARRASON_CREDENTIAL:
        logger.info("HARRASON API not configured - skipping")
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
            logger.info(f"HARRASON SUCCESS -> {report_type} | Link: {link}")
            return link
        else:
            logger.info(f"HARRASON FAILED -> {result.get('errorMessage')}")
            return None
    except Exception as e:
        logger.error(f"HARRASON EXCEPTION -> {e}")
        return None

def generate_password():
    """Generate random password"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

def send_email(name, email, amount, payment_id, report_type, assessment_link, password):
    """Send email to customer"""
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
        <p><strong>Amount Paid:</strong> Rs {amount:,.2f}<br>
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
        logger.info(f"EMAIL SENT -> {email}")
    except Exception as e:
        logger.error(f"EMAIL FAILED -> {e}")

def process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, payment_id, description):
    """Process registration and email for a single user"""
    assessment_link = None
    api_type = None
    
    if 'harrason' in product_type or 'harrason' in product_name.lower():
        api_type = "HARRASON"
        assessment_link = register_on_harrason(name, display_name, email, gender, report_type)
    elif 'disc' in product_type or 'disc' in product_name.lower() or not product_type:
        api_type = "DISC ASIA+"
        assessment_link = register_on_disc_asia(name, display_name, email, gender, report_type)
    else:
        logger.info(f"UNKNOWN PRODUCT TYPE: {product_type} - defaulting to DISC Asia+")
        api_type = "DISC ASIA+"
        assessment_link = register_on_disc_asia(name, display_name, email, gender, report_type)
    
    if assessment_link:
        password = generate_password()
        send_email(name, user_email, amount, payment_id, report_type, assessment_link, password)
        logger.info(f"{name}: {api_type} Account Created + Email Sent to {user_email}")
    else:
        logger.info(f"{name}: {api_type} REGISTRATION FAILED - No email sent")

def handler(request):
    """
    Vercel serverless function handler
    Completely standalone - no Flask dependency
    """
    logger.info("=" * 80)
    logger.info("WEBHOOK HANDLER CALLED")
    logger.info("=" * 80)
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Get request body
        body = b''
        if hasattr(request, 'body'):
            body = request.body or b''
        elif hasattr(request, 'get_json'):
            try:
                data = request.get_json(force=True) or {}
            except:
                body = getattr(request, 'data', b'') or b''
                data = {}
        else:
            body = getattr(request, 'data', b'') or b''
            data = {}
        
        # Parse JSON if we have body
        if body and not data:
            if isinstance(body, bytes):
                body_str = body.decode('utf-8')
            else:
                body_str = str(body)
            try:
                data = json.loads(body_str)
            except:
                logger.error(f"Failed to parse JSON: {body_str[:200]}")
                data = {}
        
        logger.info(f"Event: {data.get('event', 'N/A')}")
        logger.info(f"Data received: {bool(data)}")
        
        # Check if it's payment.captured event
        if not data or data.get('event') != 'payment.captured':
            logger.info("Event is not payment.captured - returning OK")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'ok'
            }
        
        # Extract payment data
        p = data['payload']['payment']['entity']
        notes = p.get('notes', {})
        description = p.get('description', '')
        amount = p['amount'] / 100
        order_id = p.get('order_id', '')
        
        logger.info("=" * 80)
        logger.info("NEW PAYMENT FROM ODOO WEBSITE - BODHIH.COM")
        logger.info("=" * 80)
        logger.info(f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        logger.info(f"Amount: Rs {amount:,.2f}")
        logger.info(f"Payment ID: {p['id']}")
        logger.info(f"Order ID: {order_id}")
        logger.info(f"Description: {description}")
        
        # Extract Odoo order identifier
        odoo_order_identifier = None
        
        if description:
            so_match = re.search(r'SO-[\d-]+', description, re.IGNORECASE)
            if so_match:
                odoo_order_identifier = so_match.group(0)
                logger.info(f"Extracted Odoo order identifier: {odoo_order_identifier}")
            elif description.strip().isdigit():
                odoo_order_identifier = description.strip()
                logger.info(f"Using description as Odoo order ID: {odoo_order_identifier}")
        
        if isinstance(notes, dict) and not odoo_order_identifier:
            odoo_order_identifier = notes.get('sale_order_id') or notes.get('order_id') or notes.get('odoo_order_id')
            if odoo_order_identifier:
                logger.info(f"Found Odoo order identifier in notes: {odoo_order_identifier}")
        
        # Query Odoo if we have an identifier
        odoo_order_info = None
        if odoo_order_identifier:
            logger.info(f"Querying Odoo database for order: {odoo_order_identifier}")
            odoo_order_info = get_odoo_products_by_order_id(odoo_order_identifier)
            if odoo_order_info:
                logger.info(f"Successfully retrieved {len(odoo_order_info.get('products', []))} product(s) from Odoo")
            else:
                logger.info("Could not retrieve products from Odoo")
        
        # Process products from Odoo
        if odoo_order_info and odoo_order_info.get('products'):
            logger.info("PROCESSING PRODUCTS FROM ODOO DATABASE")
            products = odoo_order_info['products']
            
            # Get customer info
            if isinstance(notes, list) and len(notes) > 0:
                # Multiple users
                for idx, user_data in enumerate(notes):
                    if isinstance(user_data, dict):
                        name = user_data.get('name', 'Customer')
                        email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                        user_email = user_data.get('user_email', email)
                        gender = user_data.get('gender', 'Male')
                        
                        product = products[idx] if idx < len(products) else products[0]
                        product_name = product.get('product_name', product.get('line_name', ''))
                        product_type = determine_product_type_from_odoo(
                            product.get('product_name', ''),
                            product.get('line_name', '')
                        )
                        report_type = extract_report_type(product_name)
                        
                        logger.info(f"Processing User: {name} ({user_email})")
                        logger.info(f"Product: {product_name} | Type: {product_type.upper()}")
                        process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
            else:
                # Single user
                name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
                email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
                user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
                gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
                
                logger.info(f"Customer Name: {name}")
                logger.info(f"Email: {email}")
                logger.info(f"Products Found: {len(products)}")
                
                # Process each product
                for product in products:
                    product_name = product.get('product_name', product.get('line_name', ''))
                    product_type = determine_product_type_from_odoo(
                        product.get('product_name', ''),
                        product.get('line_name', '')
                    )
                    report_type = extract_report_type(product_name)
                    
                    logger.info(f"Processing Product: {product_name}")
                    logger.info(f"Type: {product_type.upper()} | Report: {report_type}")
                    process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
        
        logger.info("=" * 80)
        logger.info("Webhook processing completed successfully")
        logger.info("=" * 80)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'OK'
        }
        
    except Exception as e:
        logger.error(f"ERROR processing webhook: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Error: {str(e)}'
        }
