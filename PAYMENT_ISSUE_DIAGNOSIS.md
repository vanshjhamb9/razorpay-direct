# Payment Issue Diagnosis - Order 35474

## Issue Found

**Order 35474** (SO-05224) was created but **no email was sent** to the customer.

## Order Details

- **Order ID**: 35474
- **Order Name**: SO-05224
- **Date**: 2025-12-27 20:12:24
- **Amount**: Rs 5.00
- **State**: `draft` ⚠️ **This is the problem!**
- **Customer**: Vansh Jhamb
- **Email**: vanshjhamb9@gmail.com
- **Product**: Test - DISC Asia+ Basic Report (DISC product)

## Root Cause

The order is still in **`draft`** state, which means:

1. **Payment might not have been completed** - The payment transaction might not have been captured
2. **Webhook was not triggered** - Razorpay webhook only triggers on `payment.captured` event
3. **Order not confirmed** - Order needs to be in `sale` state for confirmed payment

## Why Email Wasn't Sent

The webhook endpoint `/razorpay-webhook` only processes payments when:
- Event type is `payment.captured`
- Payment status is `captured`

If the order is still in `draft`, the payment likely:
- Wasn't completed
- Failed
- Is pending
- Webhook wasn't called

## How to Fix

### Option 1: Check Razorpay Dashboard

1. Go to Razorpay Dashboard
2. Check if payment for order 35474 was actually captured
3. Look for webhook logs to see if webhook was called
4. Verify webhook URL is configured correctly

### Option 2: Check Flask Server Logs

Check your Flask server logs for:
- Any webhook calls around the time of purchase (2025-12-27 20:12:24)
- Any errors or warnings
- Look for lines containing "payment.captured" or "35474"

### Option 3: Verify Webhook Configuration

Ensure Razorpay webhook is configured with:
- **Webhook URL**: `http://your-server-url/razorpay-webhook`
- **Events**: `payment.captured` must be enabled
- **Secret**: If using webhook signature verification, ensure it's configured

### Option 4: Test Webhook Manually

You can test if the webhook works by simulating a payment:

```bash
# Use test_odoo_webhook.py with order 35474
python test_odoo_webhook.py
```

Update the payload to include:
- Order ID: 35474 or SO-05224
- Customer email: vanshjhamb9@gmail.com
- Customer name: Vansh Jhamb

## Expected Behavior

When payment is completed successfully:

1. **Razorpay sends webhook** → `/razorpay-webhook`
2. **Webhook extracts order ID** from description/notes
3. **Queries Odoo** for products in order 35474
4. **Finds DISC product** → Routes to DISC Asia+ API
5. **Creates account** on DISC API
6. **Sends email** to vanshjhamb9@gmail.com with assessment link

## Current Status

- ✅ Order exists in Odoo
- ✅ Product is correct (DISC product)
- ✅ Customer email is available
- ❌ Order is in `draft` state (should be `sale`)
- ❌ Payment might not be captured
- ❌ Webhook might not have been called

## Next Steps

1. **Check Razorpay Dashboard** for payment status
2. **Check Flask logs** for webhook calls
3. **Verify webhook URL** is accessible from internet
4. **Test webhook manually** with order 35474
5. **If payment was successful**, manually trigger the webhook or confirm the order in Odoo

## Manual Test

To test what would happen if payment was captured:

```bash
curl "http://localhost:5000/test-odoo?order_id=35474"
```

This will show:
- Products retrieved from Odoo
- Product type detection (DISC)
- What API would be called

## If Payment Was Actually Completed

If the payment was completed but webhook wasn't called:

1. **Manually confirm order in Odoo** (change state from `draft` to `sale`)
2. **Manually trigger webhook** using test script
3. **Or resend webhook from Razorpay** (if dashboard allows)

