"""
Vercel serverless function for /razorpay-webhook
Standalone implementation - NO Flask imports
"""

import json
import sys
import os
import logging
import requests
import xmlrpc.client
import re
from datetime import datetime, timezone
import smtplib
from email.message import EmailMessage
import secrets
import string

# #region agent log
log_path = r'c:\Users\asus\OneDrive\Desktop\Oddo auto\.cursor\debug.log'
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"api/razorpay-webhook.py:20","message":"Module loading started","data":{"python_version":sys.version},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"api/razorpay-webhook.py:35","message":"Logger configured","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

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

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"api/razorpay-webhook.py:60","message":"Environment variables loaded","data":{"odoo_url":ODOO_URL,"has_disc_cred":bool(DISC_CREDENTIAL)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

# Copy all necessary functions from main.py (standalone, no Flask)
def get_odoo_products_by_order_id(order_id):
    """Query Odoo database to get products sold in a sale order"""
    if not order_id or not ODOO_URL or not ODOO_DB:
        logger.info(f"[WARN] Cannot query Odoo - missing order_id or Odoo credentials")
        return None
    
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        logger.info(f"-> Connecting to Odoo: {ODOO_URL}")
        
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        
        if not uid:
            logger.info(f"[FAIL] Odoo authentication failed")
            return None
        
        logger.info(f"[OK] Odoo authenticated successfully (UID: {uid})")
        
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
            logger.info(f"[WARN] Sale order not found in Odoo for order_id: {order_id}")
            return None
        
        sale_order_id = sale_order_ids[0]
        logger.info(f"[OK] Found sale order in Odoo: ID {sale_order_id}")
        
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
            logger.info(f"[WARN] No order lines found for sale order {sale_order_id}")
            return None
        
        logger.info(f"[OK] Found {len(order_lines)} product(s) in Odoo order:")
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
        
        return {
            'sale_order_id': sale_order_id,
            'products': products
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Odoo query error: {type(e).__name__}: {e}")
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
            logger.info(f"[OK] Product identified as HARRISON: {product_name}")
            return "harrison"
    
    disc_keywords = ['disc', 'diSC', 'DISC']
    for keyword in disc_keywords:
        if keyword in combined_text:
            logger.info(f"[OK] Product identified as DISC: {product_name}")
            return "disc"
    
    logger.info(f"[WARN] Product type unclear, defaulting to DISC: {product_name}")
    return "disc"

def extract_report_type(description):
    """Extract DISC type from product description"""
    if not description:
        return "Basic"
    
    valid_types = [
        "Career entry level", "Team Build", "Communication", "Managerial",
        "Advanced", "Student", "Career", "Sales", "Basic", "Full"
    ]
    
    desc_lower = description.lower()
    for disc_type in valid_types:
        if disc_type.lower() in desc_lower:
            return disc_type
    
    return "Basic"

def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

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
            "transactionId": 1,
            "transactionDate": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
            "isSuccessful": True
        }
    }

    try:
        logger.info(f"-> DISC API Call: {DISC_API_URL}")
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        logger.info(f"-> Response Status: {r.status_code}")
        
        if r.status_code != 200:
            logger.info(f"[FAIL] DISC HTTP ERROR {r.status_code}: {r.text[:300]}")
            return None
            
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            link = result["respondentDetails"][0].get("link")
            logger.info(f"[OK] DISC SUCCESS -> Link: {link}")
            return link
        else:
            error = result.get('errorMessage', 'Unknown error')
            logger.info(f"[FAIL] DISC FAILED -> {error}")
            return None
    except Exception as e:
        logger.error(f"[ERROR] DISC ERROR -> {type(e).__name__}: {e}")
        return None

def register_on_harrason(name, display_name, email, gender, report_type):
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
        logger.info(f"[OK] {name}: {api_type} Account Created + Email Sent to {user_email}")
    else:
        logger.error(f"[FAIL] {name}: {api_type} REGISTRATION FAILED - No email sent")

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"api/razorpay-webhook.py:280","message":"Helper functions defined","data":{"functions":["get_odoo_products_by_order_id","determine_product_type_from_odoo","extract_report_type","register_on_disc_asia","send_email","process_single_user"]},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

def handler(request):
    """
    Vercel serverless function handler
    Hypothesis A: Function handler format is correct
    """
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"api/razorpay-webhook.py:handler","message":"Handler function called","data":{"request_type":type(request).__name__,"has_method":hasattr(request,'method'),"has_body":hasattr(request,'body'),"has_path":hasattr(request,'path')},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    logger.info("=" * 80)
    logger.info("WEBHOOK HANDLER CALLED")
    logger.info("=" * 80)
    logger.info(f"Request type: {type(request)}")
    logger.info(f"Request attributes: {dir(request)}")
    
    try:
        # Get request method
        method = getattr(request, 'method', 'POST')
        logger.info(f"Method: {method}")
        
        # Handle OPTIONS for CORS
        if method == 'OPTIONS':
            logger.info("[CORS] OPTIONS request received")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'ok'
            }
        
        # Handle GET requests (for testing)
        if method == 'GET':
            logger.info("[GET] Webhook endpoint accessed via GET")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({"status": "webhook_endpoint_active", "method": "GET"})
            }
        
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
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"api/razorpay-webhook.py:handler","message":"Request body parsed","data":{"body_length":len(body),"has_data":bool(data)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # Parse JSON if we have body
        if body and not data:
            if isinstance(body, bytes):
                body_str = body.decode('utf-8')
            else:
                body_str = str(body)
            try:
                data = json.loads(body_str)
            except Exception as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Body: {body_str[:200]}")
                data = {}
        
        logger.info(f"Event: {data.get('event', 'N/A')}")
        
        # Check if it's payment.captured event
        if not data or data.get('event') != 'payment.captured':
            logger.info("Event is not payment.captured - returning OK")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/plain'},
                'body': 'ok'
            }
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"F","location":"api/razorpay-webhook.py:handler","message":"Payment processing started","data":{"event":"payment.captured"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # Process payment
        p = data['payload']['payment']['entity']
        notes = p.get('notes', {})
        description = p.get('description', '')
        amount = p['amount'] / 100
        order_id = p.get('order_id', '')
        
        logger.info(f"Processing payment: {p['id']}, Amount: {amount}")
        
        # Extract Odoo order identifier
        odoo_order_identifier = None
        if description:
            so_match = re.search(r'SO-[\d-]+', description, re.IGNORECASE)
            if so_match:
                odoo_order_identifier = so_match.group(0)
            elif description.strip().isdigit():
                odoo_order_identifier = description.strip()
        
        if isinstance(notes, dict) and not odoo_order_identifier:
            odoo_order_identifier = notes.get('sale_order_id') or notes.get('order_id') or notes.get('odoo_order_id')
        
        # Query Odoo
        odoo_order_info = None
        if odoo_order_identifier:
            logger.info(f"Querying Odoo for order: {odoo_order_identifier}")
            odoo_order_info = get_odoo_products_by_order_id(odoo_order_identifier)
        
        # Process products
        if odoo_order_info and odoo_order_info.get('products'):
            products = odoo_order_info['products']
            
            if isinstance(notes, list) and len(notes) > 0:
                # Multiple users
                for idx, user_data in enumerate(notes):
                    if isinstance(user_data, dict):
                        name = user_data.get('name', 'Customer')
                        email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                        user_email = user_data.get('user_email', email)
                        gender = user_data.get('gender', 'Male')
                        
                        product = products[idx] if idx < len(products) else products[0]
                        product_name = product.get('product_name', product.get('line_name', description))
                        product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                        report_type = extract_report_type(product_name)
                        
                        process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
            else:
                # Single user
                name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
                email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
                user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
                gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
                
                for product in products:
                    product_name = product.get('product_name', product.get('line_name', description))
                    product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                    report_type = extract_report_type(product_name)
                    
                    process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
        else:
            # Fallback to notes
            logger.info("FALLBACK: Using Razorpay/Notes data")
            if isinstance(notes, list) and len(notes) > 0:
                for user_data in notes:
                    if isinstance(user_data, dict):
                        name = user_data.get('name', 'Customer')
                        email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                        user_email = user_data.get('user_email', email)
                        gender = user_data.get('gender', 'Male')
                        user_product_name = user_data.get('product_name', description)
                        product_type = user_data.get('product_type', '').lower()
                        report_type = extract_report_type(user_product_name or description)
                        
                        process_single_user(name, name, email, user_email, gender, user_product_name, product_type, report_type, amount, p['id'], description)
            else:
                name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
                email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
                user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
                gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
                product_type = (notes.get('product_type', '') if isinstance(notes, dict) else '').lower()
                report_type = extract_report_type(description)
                
                process_single_user(name, name, email, user_email, gender, description, product_type, report_type, amount, p['id'], description)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': 'OK'
        }
        
    except Exception as e:
        logger.error(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"G","location":"api/razorpay-webhook.py:handler","message":"Exception caught","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Error: {str(e)}'
        }

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"H","location":"api/razorpay-webhook.py:end","message":"Module loaded, handler defined","data":{"handler_type":type(handler).__name__,"is_function":callable(handler),"handler_name":handler.__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

logger.info(f"Handler type: {type(handler)}")
logger.info(f"Handler is callable: {callable(handler)}")
logger.info(f"Handler name: {handler.__name__}")
