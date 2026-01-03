# Live Testing Guide - Real Payment Testing

## ✅ Prerequisites Completed

- [x] Server deployed at https://bodhih.vercel.app/
- [x] Razorpay webhook configured
- [x] All endpoints tested
- [x] Environment variables set

## 🧪 Live Testing Steps

### Step 1: Prepare for Test Payment

**Before making payment:**

1. **Open Vercel Logs** (in another tab/window)
   - Go to Vercel Dashboard
   - Select your project
   - Click on "Logs" tab
   - Keep it open to monitor in real-time

2. **Have Test Order Ready**
   - Use order 35456 (SO-05206) or create a new test order
   - Ensure order has a product (DISC or Harrison)
   - Note the customer email address

3. **Prepare Monitoring Tools**
   - Vercel logs open
   - Email inbox ready (customer email)
   - This guide open

### Step 2: Make Test Payment

**On Your Odoo Website:**

1. Go to your shop: https://bodhih.odoo.com/shop
2. Add a product to cart (preferably the DISC test product)
3. Proceed to checkout
4. Complete payment through Razorpay
5. **Note the payment ID** from Razorpay confirmation

**Important:**
- Use a small amount (₹5) for testing
- Use a real email you can check
- Complete the full payment flow

### Step 3: Monitor Webhook Processing

**In Vercel Logs, you should see:**

```
WEBHOOK RECEIVED
Event: payment.captured
Time: [timestamp]
Full Payload: {...}

═══════════════════════════════════════════════════════════════════════════════════════════════
NEW PAYMENT FROM ODOO WEBSITE — BODHIH.COM
═══════════════════════════════════════════════════════════════════════════════════════════════
Time           : [date and time]
Amount         : ₹5.00
Payment ID     : pay_xxxxx
Order ID       : order_xxxxx
Description    : [should contain Odoo order ID]
```

**Then:**
```
→ Querying Odoo database for order: [order_id]
[OK] Odoo authenticated successfully (UID: 2)
[OK] Found sale order in Odoo: ID [order_id]
[OK] Found X product(s) in Odoo order:
  - Product: [product name]
→ PROCESSING PRODUCTS FROM ODOO DATABASE
→ Processing Product: [product name]
  Type: DISC | Report: Basic
→ DISC API Call: https://discapi.discasiaplus.org/api/DISC/...
[OK] DISC SUCCESS → Link: https://...
[OK] EMAIL SENT → [customer_email]
```

### Step 4: Verify Each Step

#### ✅ Webhook Received
- [ ] Logs show "WEBHOOK RECEIVED"
- [ ] Event is "payment.captured"
- [ ] Payment details logged

#### ✅ Odoo Query
- [ ] Order ID extracted from description
- [ ] Odoo connection successful
- [ ] Order found in database
- [ ] Products retrieved

#### ✅ Product Detection
- [ ] Product type detected (DISC or HARRISON)
- [ ] Report type extracted correctly
- [ ] Correct API selected

#### ✅ API Registration
- [ ] DISC/Harrison API called
- [ ] Account created successfully
- [ ] Assessment link received

#### ✅ Email Sent
- [ ] Logs show "EMAIL SENT"
- [ ] Customer email address correct
- [ ] Email delivered to inbox
- [ ] Check spam folder if not in inbox

### Step 5: Verify Customer Experience

**Check Customer Email:**

1. **Email Received:**
   - Subject: "Your [Report Type] Assessment is Ready!"
   - From: Bodhi Training Solutions
   - Contains assessment link
   - Contains login credentials

2. **Assessment Link Works:**
   - Click the link in email
   - Assessment page loads
   - Can access assessment

3. **Login Credentials:**
   - Email: Customer's email
   - Password: Generated password (in email)

## 🔍 Troubleshooting Live Testing

### Issue: Webhook Not Received

**Symptoms:**
- No logs in Vercel
- Payment completed but nothing happens

**Check:**
1. Razorpay Dashboard → Webhooks → Delivery Logs
   - See if webhook was sent
   - Check delivery status
   - Look for error messages

2. Verify Webhook URL:
   - Should be: `https://bodhih.vercel.app/razorpay-webhook`
   - No trailing slash
   - HTTPS (not HTTP)

3. Check Event Enabled:
   - `payment.captured` must be enabled
   - Other events won't trigger processing

**Fix:**
- Update webhook URL if incorrect
- Enable `payment.captured` event
- Check Razorpay webhook logs for errors

### Issue: Order Not Found in Odoo

**Symptoms:**
- Logs show: "Sale order not found in Odoo"

**Check:**
1. Payment description contains order ID
   - Should have: "35456" or "SO-05206"
   - Check Razorpay payment details

2. Order exists in Odoo
   - Verify order ID is correct
   - Check order is not deleted

**Fix:**
- Ensure Odoo sends order ID in payment description
- Verify order exists in Odoo database

### Issue: Product Not Detected

**Symptoms:**
- Products retrieved but type unclear
- Wrong API called

**Check:**
1. Product name in Odoo
   - Should contain "disc" or "harrison"
   - Check exact spelling

2. Logs show product name
   - Verify name is correct
   - Check detection logic

**Fix:**
- Update product name in Odoo
- Ensure keywords are present

### Issue: Email Not Sent

**Symptoms:**
- API registration successful
- But no email received

**Check:**
1. SMTP Settings in Vercel
   - Email and password correct
   - SMTP server accessible

2. Logs show email status
   - "EMAIL SENT" or "EMAIL FAILED"
   - Check error messages

3. Customer Email
   - Email address is correct
   - Not blocked or invalid

**Fix:**
- Verify SMTP credentials
- Check email address
- Review email logs

### Issue: API Registration Failed

**Symptoms:**
- Logs show: "DISC/HARRISON REGISTRATION FAILED"

**Check:**
1. API Credentials
   - URL is correct
   - Credential is valid
   - API is accessible

2. API Response
   - Check logs for API response
   - Look for error messages

**Fix:**
- Verify API credentials in Vercel
- Check API endpoint is working
- Review API documentation

## 📊 Success Indicators

**Everything is working if you see:**

1. ✅ Webhook received in logs
2. ✅ Odoo query successful
3. ✅ Products retrieved
4. ✅ Product type detected correctly
5. ✅ API registration successful
6. ✅ Email sent successfully
7. ✅ Customer receives email
8. ✅ Assessment link works

## 🎯 Testing Checklist

### Before Payment
- [ ] Vercel logs open
- [ ] Test order ready
- [ ] Customer email noted
- [ ] Monitoring tools ready

### During Payment
- [ ] Complete payment flow
- [ ] Note payment ID
- [ ] Watch Vercel logs

### After Payment
- [ ] Webhook received (check logs)
- [ ] Odoo query successful
- [ ] Product detected correctly
- [ ] API called successfully
- [ ] Email sent
- [ ] Customer received email
- [ ] Assessment link works

## 📝 Test Results Template

**Date:** _______________
**Payment ID:** _______________
**Order ID:** _______________
**Customer Email:** _______________

**Results:**
- [ ] Webhook received
- [ ] Odoo query successful
- [ ] Product detected: _______________
- [ ] API called: _______________
- [ ] Email sent
- [ ] Customer received email
- [ ] Assessment link works

**Issues Found:**
- 

**Notes:**
- 

## 🚀 Next Steps After Successful Test

Once everything works:

1. **Document the flow** for your team
2. **Set up monitoring** for production
3. **Test with different products** (DISC and Harrison)
4. **Test with multiple users** if needed
5. **Monitor first few real payments** closely

## 📞 If Issues Persist

1. **Check Vercel Logs** - Most detailed information
2. **Check Razorpay Webhook Logs** - Delivery status
3. **Test Endpoint Manually:**
   ```bash
   python test_deployed_webhook.py [order_id]
   ```
4. **Verify Environment Variables** in Vercel
5. **Check Odoo Order Details** - Ensure everything is correct

---

## Quick Reference

**Webhook URL:** `https://bodhih.vercel.app/razorpay-webhook`

**Test Endpoint:** `https://bodhih.vercel.app/test-odoo?order_id=35456`

**Vercel Logs:** Dashboard → Project → Logs

**Razorpay Webhooks:** Dashboard → Settings → Webhooks → Delivery Logs




