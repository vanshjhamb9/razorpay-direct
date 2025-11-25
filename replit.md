# Razorpay Webhook Payment Automation for Bodhih.com

## Overview
This Flask-based webhook server automates the payment processing workflow for Bodhih Training Solutions. When a customer makes a payment through Razorpay (integrated with Odoo), the webhook:

1. Receives payment confirmation from Razorpay
2. Extracts customer and product details
3. Routes to the appropriate assessment API based on product type:
   - **DISC Asia+** for DISC assessments
   - **Harrason** for Harrason assessments
4. Registers the customer on the assessment platform
5. Sends a confirmation email with login credentials and assessment link

## Recent Changes (November 25, 2025)
- **Added Product-Based Routing**: The webhook now extracts product details (product_id, product_name, product_type) from the Razorpay notes field
- **Harrason API Integration**: Added support for Harrason assessment API alongside DISC Asia+
- **Enhanced Logging**: Improved logging to show all product details, order info, payment method, and raw payload snippet
- **Security Improvements**: Moved hardcoded credentials to environment variables/secrets
- **Flexible Routing Logic**: Automatically routes to DISC or Harrason based on product name/type keywords

## Project Architecture

### Main Components
- **main.py**: Flask webhook server with the following endpoints:
  - `/razorpay-webhook` (POST): Receives Razorpay payment.captured events
  
### API Integrations
1. **DISC Asia+ API**: For DISC personality assessments
2. **Harrason API**: For Harrason assessments (configurable)
3. **Gmail SMTP**: For sending confirmation emails

### Product Routing Logic
The webhook determines which API to use based on:
- `product_type` field in Razorpay notes
- `product_name` field in Razorpay notes
- Keywords in product name: "disc" → DISC Asia+, "harrason" → Harrason
- Default: DISC Asia+ (if no match)

## Configuration

### Required Secrets
Set these in the Replit Secrets tab:
- `DISC_CREDENTIAL`: DISC Asia+ API credential
- `SMTP_EMAIL`: Gmail address for sending emails
- `SMTP_PASSWORD`: Gmail app password

### Optional Environment Variables
- `HARRASON_API_URL`: Harrason API endpoint (if using Harrason)
- `HARRASON_CREDENTIAL`: Harrason API credential (if using Harrason)
- `DISC_API_URL`: Override DISC API URL (defaults to production)
- `FROM_NAME`: Email sender name (default: "Bodhi Training Solutions")
- `REPLY_TO_EMAIL`: Reply-to email (default: support@bodhih.com)

## Razorpay Webhook Setup

### Webhook URL
Configure in Razorpay Dashboard:
```
https://your-replit-url.repl.co/razorpay-webhook
```

### Required Event
- `payment.captured`

### Passing Product Details from Odoo
To enable product-based routing, include these fields in the Razorpay `notes` parameter:
```python
notes = {
    "product_id": "123",           # Product ID from Odoo
    "product_name": "DISC Assessment",  # Product name
    "product_type": "disc",        # "disc" or "harrason"
    "name": "Customer Name",
    "user_email": "customer@email.com",
    "gender": "Male"               # or "Female"
}
```

## Testing
You can test the webhook locally by sending a POST request with a sample Razorpay payload to `/razorpay-webhook`.

## Deployment
This application is configured to run on Replit with automatic deployment. The webhook server runs on port 5000 and is publicly accessible for receiving Razorpay webhooks.

## User Preferences
- Language: Python 3.11
- Framework: Flask (lightweight webhook server)
- Deployment: Replit (with autoscale deployment target)
