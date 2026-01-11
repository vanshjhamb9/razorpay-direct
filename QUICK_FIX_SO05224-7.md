# Quick Fix for Order SO-05224-7

## Problem
- Payment completed (got Razorpay confirmation)
- Order still showing "processing" in Odoo
- No assessment email received

## Quick Solution

### Option 1: Run Diagnostic Script (Recommended)

```bash
python check_and_fix_order_SO05224-7.py
```

This script will:
1. ✅ Check if order exists in Odoo
2. ✅ Get order details (products, customer email, state)
3. ✅ Trigger webhook manually to process the payment
4. ✅ Verify email is sent

### Option 2: Check Vercel Logs

1. Go to Vercel Dashboard: https://vercel.com
2. Select your project
3. Go to "Logs" or "Functions" tab
4. Look for:
   - `WEBHOOK ENDPOINT HIT`
   - `WEBHOOK RECEIVED`
   - `Event: payment.captured`
   - Any errors related to `SO-05224-7`

### Option 3: Check Razorpay Webhook Status

1. Go to Razorpay Dashboard: https://dashboard.razorpay.com
2. Navigate to: **Settings → Webhooks**
3. Check:
   - ✅ Webhook URL: `https://bodhih.vercel.app/razorpay-webhook`
   - ✅ Event `payment.captured` is enabled
   - ✅ Check webhook delivery logs for this payment
   - ✅ See if webhook was sent (and failed/succeeded)

### Option 4: Manually Trigger Webhook

If webhook wasn't called, you can trigger it manually:

```bash
python check_and_fix_order_SO05224-7.py
```

Then type `y` when prompted.

---

## Why This Happened

### Most Likely Causes:

1. **Webhook Not Configured in Razorpay**
   - Razorpay doesn't know where to send payment notifications
   - Fix: Configure webhook URL in Razorpay Dashboard

2. **Webhook Delivery Failed**
   - Razorpay tried to send webhook but it failed
   - Check Razorpay webhook logs for delivery errors
   - Fix: Verify webhook URL is accessible

3. **Order ID Format Mismatch**
   - Payment description might not contain `SO-05224-7`
   - Webhook can't find order in Odoo
   - Fix: Ensure Odoo sends order name in payment description

4. **Deployment Not Complete**
   - Latest code might not be deployed yet
   - Fix: Check Vercel deployment status, redeploy if needed

---

## What Should Happen

When webhook is triggered correctly:

1. ✅ Razorpay sends `payment.captured` event to webhook
2. ✅ Webhook extracts order ID from description: `SO-05224-7`
3. ✅ Webhook queries Odoo for products in this order
4. ✅ Webhook calls DISC API to create assessment
5. ✅ Webhook sends email with assessment link
6. ✅ Webhook updates Odoo order status to "sale"

---

## Verify Fix

After running the fix script:

1. **Check Email** (within 1-2 minutes):
   - Email should arrive at customer's email
   - Email should show correct product name (not "Basic Assessment")
   - Email should contain assessment link

2. **Check Odoo Order**:
   - Order state should change from "draft" to "sale"
   - Order should appear in customer's "Sales Orders"

3. **Check Server Logs** (Vercel):
   - Should see "WEBHOOK RECEIVED"
   - Should see "Processing Product: [product name]"
   - Should see "EMAIL SENT"
   - Should see "Odoo order status updated"

---

## Prevention

To prevent this in future:

1. **Verify Razorpay Webhook Configuration**
   - Webhook URL: `https://bodhih.vercel.app/razorpay-webhook`
   - Event: `payment.captured` enabled

2. **Ensure Odoo Sends Order ID in Payment**
   - Payment description should contain order name: `SO-05224-7`
   - Or order ID in notes

3. **Monitor Webhook Logs**
   - Check Vercel logs regularly
   - Check Razorpay webhook delivery logs

4. **Test After Deployment**
   - Make test purchase after deploying changes
   - Verify webhook processes correctly

---

## Need More Help?

1. Check Vercel logs for detailed error messages
2. Check Razorpay webhook delivery logs
3. Run diagnostic script: `python check_and_fix_order_SO05224-7.py`
4. Verify all environment variables are set correctly
