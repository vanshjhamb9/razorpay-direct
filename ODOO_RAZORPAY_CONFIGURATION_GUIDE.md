# Odoo + Razorpay Integration Guide for Bodhih.com

## Overview
This guide explains how to configure Razorpay in Odoo 18.4 to automatically pass product details to the webhook. **No Odoo code changes needed!**

## How It Works

```
Customer Makes Payment → Razorpay Captures Payment → Sends to Webhook
                                                        ↓
Webhook reads product details from Razorpay notes → Routes to DISC or Harrason → Sends email
```

## Configuration Steps

### Step 1: Go to Razorpay Payment Gateway Settings
1. In Odoo, go to **Accounting** → **Configuration** → **Payment Methods**
2. Find **Razorpay** payment method
3. Click to edit it

### Step 2: Add Custom Payment Metadata
In the payment gateway configuration, add these fields to the **Notes/Metadata** section:

```python
# Add to Razorpay notes when creating payment
{
    "product_id": "PRODUCT_ID",
    "product_name": "PRODUCT_NAME", 
    "product_type": "disc",  # or "harrason"
    "name": "CUSTOMER_NAME",
    "user_email": "CUSTOMER_EMAIL",
    "gender": "Male"  # or "Female"
}
```

### Step 3: Map Odoo Fields to Razorpay Notes

You need to configure Razorpay to extract these values from the Sale Order:

- **product_id**: From `order_line[0].product_id.id`
- **product_name**: From `order_line[0].product_id.name`
- **product_type**: Determine based on product name:
  - If product name contains "DISC" → set to "disc"
  - If product name contains "Harrason" → set to "harrason"
- **name**: From `partner_id.name`
- **user_email**: From `partner_id.email`
- **gender**: From custom field (or skip to use Razorpay's auto-detection)

### Step 4: Example Product Setup in Odoo

Make sure your products are named clearly:

**For DISC Assessment:**
- Product Name: `DISC Asia+ Basic Report`
- Product Name: `DISC Asia+ Advanced Self-Awareness Report`

**For Harrason Assessment:**
- Product Name: `Harrason Leadership Assessment`
- Product Name: `Harrason Team Dynamics Report`

The webhook will automatically detect "disc" or "harrason" keywords.

### Step 5: Test the Integration

Create a test sale order with:
- Product: DISC Assessment
- Customer: Test customer email
- Payment: Complete the Razorpay payment

**Check the webhook logs** to verify:
```
NEW PAYMENT FROM ODOO WEBSITE — BODHIH.COM
Product Name: DISC Asia+ Basic Report
Product Type: disc
Router to: DISC ASIA+
```

## Webhook URL

Configure Razorpay webhook to send to:
```
https://your-replit-url.repl.co/razorpay-webhook
```

Events to listen for:
- `payment.captured` (when payment is successfully completed)

## Troubleshooting

### Payment Received but No Email Sent
- Check webhook logs for errors
- Verify DISC_CREDENTIAL and SMTP credentials are set
- Verify product name contains "disc" or "harrason" keywords

### Wrong Assessment Type Detected
- Check product name in Odoo - add clear keywords ("DISC" or "Harrason")
- Verify product_type in Razorpay notes is correct

### Customer Email Missing
- Ensure customer contact has email address
- Verify "user_email" is passed in Razorpay notes

## Support
If you encounter issues, check the webhook logs in Replit for detailed error messages.
