"""
Vercel serverless function for /razorpay-webhook
Callable class handler - works as both class and function
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
        f.write(json.dumps({"sessionId":"debug-session","runId":"run4","hypothesisId":"A","location":"api/razorpay-webhook.py:20","message":"Module loading - callable class","data":{"python_version":sys.version},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
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
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "assessments@bodhih.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "L[E0xV7bE1,Y")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.bodhih.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
FROM_NAME = os.environ.get("FROM_NAME", "Bodhi Training Solutions")
REPLY_TO_EMAIL = os.environ.get("REPLY_TO_EMAIL", "support@bodhih.com")

# Helper functions (abbreviated for space - same logic as before)
def get_odoo_products_by_order_id(order_id):
    if not order_id or not ODOO_URL or not ODOO_DB:
        return None
    try:
        models = xmlrpc.client.ServerProxy(ODOO_XMLRPC_URL)
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            return None
        order_id_int = int(order_id) if order_id.strip().isdigit() else None
        sale_order_domain = [('id', '=', order_id_int)] if order_id_int else [('name', '=', str(order_id))]
        sale_order_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'sale.order', 'search', [sale_order_domain], {'limit': 1})
        if not sale_order_ids:
            return None
        order_lines = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'sale.order.line', 'search_read', [[('order_id', '=', sale_order_ids[0])]], {'fields': ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal', 'name'], 'limit': 100})
        if not order_lines:
            return None
        products = [{'product_id': line.get('product_id', [None])[0] if isinstance(line.get('product_id'), list) else None, 'product_name': line.get('product_id', [None, ''])[1] if isinstance(line.get('product_id'), list) and len(line.get('product_id', [])) > 1 else line.get('name', ''), 'quantity': line.get('product_uom_qty', 0), 'price_unit': line.get('price_unit', 0), 'price_subtotal': line.get('price_subtotal', 0), 'line_name': line.get('name', '')} for line in order_lines]
        return {'sale_order_id': sale_order_ids[0], 'products': products}
    except Exception as e:
        logger.error(f"Odoo error: {e}")
        return None

def determine_product_type_from_odoo(product_name, product_line_name):
    combined_text = f"{product_name} {product_line_name}".lower()
    if any(k in combined_text for k in ['harrison', 'harrason', 'harison', 'harisson']):
        return "harrison"
    if any(k in combined_text for k in ['disc', 'diSC', 'DISC']):
        return "disc"
    return "disc"

def extract_report_type(description):
    if not description:
        return "Basic"
    valid_types = ["Career entry level", "Team Build", "Communication", "Managerial", "Advanced", "Student", "Career", "Sales", "Basic", "Full"]
    desc_lower = description.lower()
    for disc_type in valid_types:
        if disc_type.lower() in desc_lower:
            return disc_type
    return "Basic"

def generate_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

def register_on_disc_asia(name, display_name, email, gender, report_type):
    payload = {"credentials": {"encryptedPassword": DISC_CREDENTIAL}, "respondentDetails": [{"name": name, "displayName": display_name, "gender": gender.title(), "eMailAddress": email, "type": report_type}], "transactionDetails": {"transactionId": 1, "transactionDate": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'), "isSuccessful": True}}
    try:
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        if r.status_code == 200:
            result = r.json()
            if result.get("success") and result.get("respondentDetails"):
                return result["respondentDetails"][0].get("link")
        return None
    except:
        return None

def register_on_harrason(name, display_name, email, gender, report_type):
    if not HARRASON_API_URL or not HARRASON_CREDENTIAL:
        return None
    payload = {"credentials": {"encryptedPassword": HARRASON_CREDENTIAL}, "respondentDetails": [{"name": name, "displayName": display_name, "gender": gender.title(), "eMailAddress": email, "type": report_type}], "transactionDetails": {"transactionId": 1, "transactionDate": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'), "isSuccessful": True}}
    try:
        r = requests.post(HARRASON_API_URL, json=payload, timeout=20)
        result = r.json()
        if result.get("success") and result.get("respondentDetails"):
            return result["respondentDetails"][0].get("link")
        return None
    except:
        return None

def send_email(name, email, amount, payment_id, report_type, assessment_link, password):
    msg = EmailMessage()
    msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Reply-To'] = REPLY_TO_EMAIL
    msg['Subject'] = f"Your {report_type} Assessment is Ready!"
    html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;"><h2 style="color:#2c3e50;text-align:center;">Payment Confirmed!</h2><p>Dear <strong>{name}</strong>,</p><p>Thank you for purchasing:</p><h3 style="background:#e3f2fd;padding:15px;border-radius:8px;text-align:center;">{report_type} Assessment</h3><p><strong>Amount Paid:</strong> ₹{amount:,.2f}<br><strong>Payment ID:</strong> {payment_id}</p><h3>Your Assessment Access</h3><p><strong>Login Email:</strong> {email}<br><strong>Password:</strong> <code style="background:#eee;padding:8px;font-size:15px;">{password}</code></p><div style="text-align:center;margin:30px 0;"><a href="{assessment_link}" style="background:#1976d2;color:white;padding:16px 32px;text-decoration:none;border-radius:8px;font-size:18px;">Start Your Assessment Now</a></div><p style="background:#fff3cd;padding:15px;border-radius:8px;">This link is unique to you. Keep this email safe.</p><p style="font-size:12px;color:#777;text-align:center;">Need help? Reply to this email.<br>Bodhi Training Solutions | www.bodhih.com</p></body></html>"""
    msg.set_content("HTML email required.")
    msg.add_alternative(html, subtype='html')
    try:
        logger.info(f"-> Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        logger.info(f"-> Using email: {SMTP_EMAIL}")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        logger.info(f"EMAIL SENT -> {email}")
    except Exception as e:
        logger.error(f"EMAIL FAILED -> {e}")
        import traceback
        logger.error(f"-> Traceback: {traceback.format_exc()}")

def process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, payment_id, description):
    assessment_link = register_on_harrason(name, display_name, email, gender, report_type) if ('harrason' in product_type or 'harrason' in product_name.lower()) else register_on_disc_asia(name, display_name, email, gender, report_type)
    if assessment_link:
        password = generate_password()
        send_email(name, user_email, amount, payment_id, report_type, assessment_link, password)
        logger.info(f"[OK] {name}: Account Created + Email Sent")

# Simple function handler - Vercel might accept this if it's exported correctly
def handler(request):
    """
    Vercel serverless function handler
    Hypothesis: Simple function format works if exported correctly
    """
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run4","hypothesisId":"A","location":"api/razorpay-webhook.py:handler","message":"Handler function called","data":{"request_type":type(request).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    logger.info("=" * 80)
    logger.info("WEBHOOK HANDLER CALLED")
    logger.info("=" * 80)
    
    try:
        method = getattr(request, 'method', 'POST')
        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'ok'}
        if method == 'GET':
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps({"status": "webhook_endpoint_active", "method": "GET"})}
        
        body = getattr(request, 'body', getattr(request, 'data', b'')) or b''
        data = json.loads(body.decode('utf-8') if isinstance(body, bytes) else str(body)) if body else {}
        
        if not data or data.get('event') != 'payment.captured':
            return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'ok'}
        
        p = data['payload']['payment']['entity']
        notes = p.get('notes', {})
        description = p.get('description', '')
        amount = p['amount'] / 100
        
        odoo_order_identifier = None
        if description:
            so_match = re.search(r'SO-[\d-]+', description, re.IGNORECASE)
            odoo_order_identifier = so_match.group(0) if so_match else (description.strip() if description.strip().isdigit() else None)
        if isinstance(notes, dict) and not odoo_order_identifier:
            odoo_order_identifier = notes.get('sale_order_id') or notes.get('order_id') or notes.get('odoo_order_id')
        
        odoo_order_info = get_odoo_products_by_order_id(odoo_order_identifier) if odoo_order_identifier else None
        
        if odoo_order_info and odoo_order_info.get('products'):
            products = odoo_order_info['products']
            if isinstance(notes, list) and len(notes) > 0:
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
        
        return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'OK'}
    except Exception as e:
        logger.error(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'statusCode': 500, 'headers': {'Content-Type': 'text/plain'}, 'body': f'Error: {str(e)}'}

# #region agent log
try:
    with open(log_path, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run4","hypothesisId":"H","location":"api/razorpay-webhook.py:end","message":"Module loaded, handler function defined","data":{"handler_type":type(handler).__name__,"is_function":callable(handler)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

logger.info(f"Handler type: {type(handler)}")
logger.info(f"Is callable: {callable(handler)}")
