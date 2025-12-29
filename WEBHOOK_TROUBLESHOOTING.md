# Webhook Troubleshooting Guide

## Issue: Payment Made But No Email Received

**Order SO-05206** (ID: 35456) - Payment confirmed but webhook not processing.

## Root Causes

### 1. Webhook Not Being Called by Razorpay

**Symptoms:**
- Payment successful in Razorpay
- No webhook calls in Flask logs
- Order exists in Odoo

**Possible Causes:**
- Webhook URL not configured in Razorpay
- Webhook URL not accessible from internet
- `payment.captured` event not enabled

**Solution:**
1. Check Razorpay Dashboard → Settings → Webhooks
2. Verify webhook URL: `http://your-server/razorpay-webhook`
3. Ensure `payment.captured` event is enabled
4. If running locally, use ngrok:
   ```bash
   ngrok http 5000
   # Use the ngrok URL in Razorpay webhook settings
   ```

### 2. Payment Description Missing Order ID

**Symptoms:**
- Webhook is called
- But can't find order in Odoo
- Logs show "Sale order not found"

**Solution:**
- Razorpay payment description must contain:
  - Order ID: `35456`
  - Or Order Name: `SO-05206`
- Check Razorpay payment details
- Configure Odoo to send order ID in payment description

### 3. Webhook Endpoint Not Accessible

**Symptoms:**
- Razorpay shows webhook delivery failed
- Connection timeout errors

**Solution:**
- Ensure Flask server is running
- Check firewall/port settings
- Use public URL (ngrok, cloud server, etc.)
- Test endpoint: `curl http://your-server/razorpay-webhook`

## Diagnostic Steps

### Step 1: Check Flask Logs

Look for:
```
WEBHOOK RECEIVED
Event: payment.captured
```

If you don't see this, webhook isn't being called.

### Step 2: Test Webhook Manually

```bash
python test_webhook_SO05206.py
```

This simulates the webhook to verify the flow works.

### Step 3: Check Order in Odoo

```bash
python check_order_SO05206.py
```

Verify order exists and has products.

### Step 4: Verify Webhook Configuration

1. **Razorpay Dashboard:**
   - Go to Settings → Webhooks
   - Check webhook URL
   - Verify `payment.captured` is enabled
   - Check webhook delivery logs

2. **Flask Server:**
   - Ensure server is running
   - Check if endpoint is accessible
   - Verify logs are showing

## Quick Fixes

### Fix 1: Add Better Logging

I've updated `main.py` to log ALL webhook calls, not just `payment.captured` events.

### Fix 2: Test Webhook Endpoint

```bash
python webhook_diagnostics.py
```

### Fix 3: Manual Webhook Test

```bash
python test_webhook_SO05206.py
```

## Expected Behavior

When webhook works correctly:

1. **Razorpay sends webhook** → `/razorpay-webhook`
2. **Flask logs show:**
   ```
   WEBHOOK RECEIVED
   Event: payment.captured
   NEW PAYMENT FROM ODOO WEBSITE
   → Querying Odoo database for order: 35456
   [OK] Successfully retrieved 1 product(s) from Odoo
   → Processing Product: Test - DISC Asia+ Basic Report
   [OK] DISC SUCCESS → Link: https://...
   [OK] EMAIL SENT → vanshjhamb9@gmail.com
   ```

## Next Steps

1. **Check Flask server logs** - Look for "WEBHOOK RECEIVED"
2. **Check Razorpay webhook logs** - See if webhook was sent
3. **Test webhook manually** - Run `test_webhook_SO05206.py`
4. **Verify webhook URL** - Ensure it's accessible from internet
5. **Check payment description** - Must contain order ID

## Files Created

- `check_order_SO05206.py` - Check order details
- `test_webhook_SO05206.py` - Test webhook for this order
- `webhook_diagnostics.py` - Diagnose webhook issues
- `WEBHOOK_TROUBLESHOOTING.md` - This guide

