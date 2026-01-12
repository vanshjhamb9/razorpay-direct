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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

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
        logger.info(f"-> DISC API Call: {DISC_API_URL}")
        logger.info(f"-> Request: Name={name}, Email={email}, Type={report_type}")
        logger.info(f"-> Request Payload: {json.dumps(payload, indent=2)}")
        r = requests.post(DISC_API_URL, json=payload, timeout=20)
        logger.info(f"-> Response Status: {r.status_code}")
        logger.info(f"-> Full Response Text: {r.text}")
        if r.status_code == 200:
            result = r.json()
            logger.info(f"-> Response JSON: {json.dumps(result, indent=2)}")
            if result.get("success") and result.get("respondentDetails"):
                link = result["respondentDetails"][0].get("link")
                respondent_id = result["respondentDetails"][0].get("respondentId")
                logger.info(f"[OK] DISC SUCCESS -> Link: {link}")
                if respondent_id:
                    logger.info(f"[OK] DISC SUCCESS -> Respondent ID: {respondent_id}")
                return link
            else:
                error = result.get('errorMessage', 'Unknown error')
                logger.error(f"[FAIL] DISC FAILED -> Error: {error}")
        else:
            logger.error(f"[FAIL] DISC HTTP ERROR {r.status_code}: {r.text[:500]}")
        return None
    except Exception as e:
        logger.error(f"[ERROR] DISC ERROR -> {type(e).__name__}: {e}")
        import traceback
        logger.error(f"-> Traceback: {traceback.format_exc()}")
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

def send_email(name, email, amount, payment_id, report_type, assessment_link, password, product_name=None):
    msg = EmailMessage()
    msg['From'] = f"{FROM_NAME} <{SMTP_EMAIL}>"
    msg['To'] = email
    msg['Reply-To'] = REPLY_TO_EMAIL
    display_product = product_name if product_name else f"{report_type} Assessment"
    msg['Subject'] = f"Your {display_product} is Ready!"
    html = f"""<html><body style="font-family:Arial,sans-serif;max-width:600px;margin:30px auto;padding:20px;background:#f9f9f9;border-radius:10px;"><h2 style="color:#2c3e50;text-align:center;">Payment Confirmed!</h2><p>Dear <strong>{name}</strong>,</p><p>Thank you for purchasing:</p><h3 style="background:#e3f2fd;padding:15px;border-radius:8px;text-align:center;">{display_product}</h3><p><strong>Amount Paid:</strong> ₹{amount:,.2f}<br><strong>Payment ID:</strong> {payment_id}</p><h3>Your Assessment Access</h3><p style="margin-bottom:10px;"><strong>Login Email:</strong> {email}</p><p style="margin-top:10px;margin-bottom:20px;"><strong>Password:</strong> <code style="background:#eee;padding:8px;font-size:15px;">{password}</code></p><div style="text-align:center;margin:30px 0;"><a href="{assessment_link}" style="background:#1976d2;color:white;padding:16px 32px;text-decoration:none;border-radius:8px;font-size:18px;">Start Your Assessment Now</a></div><p style="background:#fff3cd;padding:15px;border-radius:8px;">This link is unique to you. Keep this email safe.</p><p style="font-size:12px;color:#777;text-align:center;">Need help? Reply to this email.<br>Bodhi Training Solutions | www.bodhih.com</p></body></html>"""
    msg.set_content("HTML email required.")
    msg.add_alternative(html, subtype='html')
    try:
        logger.info(f"-> Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        logger.info(f"-> Using email: {SMTP_EMAIL}")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
            s.login(SMTP_EMAIL, SMTP_PASSWORD)
            s.send_message(msg)
        logger.info(f"EMAIL SENT -> {email} (Product: {display_product})")
    except Exception as e:
        logger.error(f"EMAIL FAILED -> {e}")
        import traceback
        logger.error(f"-> Traceback: {traceback.format_exc()}")

def process_single_user(name, display_name, email, user_email, gender, product_name, product_type, report_type, amount, payment_id, description):
    assessment_link = register_on_harrason(name, display_name, email, gender, report_type) if ('harrason' in product_type or 'harrason' in product_name.lower()) else register_on_disc_asia(name, display_name, email, gender, report_type)
    if assessment_link:
        password = generate_password()
        send_email(name, user_email, amount, payment_id, report_type, assessment_link, password, product_name=product_name)
        logger.info(f"[OK] {name}: Account Created + Email Sent (Product: {product_name}, Report Type: {report_type})")

def handler(request):
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
        event_type = data.get('event', '')
        if not data or event_type not in ['payment.captured', 'order.paid']:
            logger.info(f"[SKIP] Event is '{event_type}' - only processing 'payment.captured' or 'order.paid' events")
            return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'ok'}
        if 'payload' in data and 'payment' in data['payload'] and 'entity' in data['payload']['payment']:
            p = data['payload']['payment']['entity']
            logger.info(f"[OK] Processing event: {event_type}")
        else:
            logger.info(f"[SKIP] Payment entity not found in payload for event: {event_type}")
            return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'ok'}
        if p.get('status') != 'captured' or not p.get('captured', False):
            logger.info(f"[SKIP] Payment not captured - status: {p.get('status')}, captured: {p.get('captured')}")
            return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'ok'}
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
                        product_name = product.get('product_name') or product.get('line_name') or 'Assessment Report'
                        if product_name.startswith('SO-'):
                            product_name = product.get('line_name') or 'Assessment Report'
                        product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                        report_type = extract_report_type(product_name)
                        logger.info(f"-> Processing User: {name} ({user_email})")
                        logger.info(f"  Product: {product_name} | Type: {product_type.upper()} | Report: {report_type}")
                        process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
            else:
                name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
                email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
                user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
                gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
                for product in products:
                    product_name = product.get('product_name') or product.get('line_name') or 'Assessment Report'
                    if product_name.startswith('SO-'):
                        product_name = product.get('line_name') or 'Assessment Report'
                    product_type = determine_product_type_from_odoo(product.get('product_name', ''), product.get('line_name', ''))
                    report_type = extract_report_type(product_name)
                    logger.info(f"\n-> Processing Product: {product_name}")
                    logger.info(f"  Type: {product_type.upper()} | Report: {report_type}")
                    process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
        else:
            if isinstance(notes, list) and len(notes) > 0:
                for user_data in notes:
                    if isinstance(user_data, dict):
                        name = user_data.get('name', 'Customer')
                        email = user_data.get('email', p.get('email', 'no-email@bodhih.com'))
                        user_email = user_data.get('user_email', email)
                        gender = user_data.get('gender', 'Male')
                        user_product_name = user_data.get('product_name', 'Assessment Report')
                        if user_product_name.startswith('SO-'):
                            user_product_name = 'Assessment Report'
                        product_type = user_data.get('product_type', '').lower()
                        report_type = extract_report_type(user_product_name or 'Assessment Report')
                        logger.info(f"\n-> Processing User: {name} ({user_email})")
                        logger.info(f"  Product: {user_product_name} | Report Type: {report_type}")
                        process_single_user(name, name, email, user_email, gender, user_product_name, product_type, report_type, amount, p['id'], description)
            else:
                name = notes.get('name', p.get('contact', 'Customer')) if isinstance(notes, dict) else 'Customer'
                email = (notes.get('user_email') if isinstance(notes, dict) else None) or p.get('email', 'no-email@bodhih.com')
                user_email = (notes.get('user_email') if isinstance(notes, dict) else None) or email
                gender = notes.get('gender', 'Male') if isinstance(notes, dict) else 'Male'
                product_type = (notes.get('product_type', '') if isinstance(notes, dict) else '').lower()
                product_name = 'Assessment Report' if description.startswith('SO-') else (description or 'Assessment Report')
                report_type = extract_report_type(product_name)
                logger.info(f"Customer Name  : {name}")
                logger.info(f"Email          : {email}")
                logger.info(f"Product Name   : {product_name or '—'}")
                logger.info(f"Report Type    : {report_type}")
                process_single_user(name, name, email, user_email, gender, product_name, product_type, report_type, amount, p['id'], description)
        return {'statusCode': 200, 'headers': {'Content-Type': 'text/plain'}, 'body': 'OK'}
    except Exception as e:
        logger.error(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'statusCode': 500, 'headers': {'Content-Type': 'text/plain'}, 'body': f'Error: {str(e)}'}
