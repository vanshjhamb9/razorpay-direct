# Next Steps - Production Setup

## ✅ What's Done

- [x] Odoo XML-RPC integration working
- [x] Product detection (DISC/Harrison) working
- [x] Webhook endpoint deployed and tested
- [x] Server accessible at https://bodhih.vercel.app/
- [x] All critical endpoints verified

## 🎯 Immediate Next Steps

### Step 1: Configure Razorpay Webhook (CRITICAL)

**Action Required:**
1. Log in to Razorpay Dashboard
2. Go to **Settings** → **Webhooks**
3. Add/Update webhook:
   - **Webhook URL**: `https://bodhih.vercel.app/razorpay-webhook`
   - **Events**: Enable `payment.captured`
   - **Secret**: (Optional, but recommended for production)
4. Save the configuration

**Verification:**
- Razorpay will send a test webhook
- Check Vercel logs to confirm it was received

### Step 2: Verify Environment Variables in Vercel

**Check these are set in Vercel Dashboard:**

```bash
# Odoo Configuration
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=siddharthan@bodhih.com
ODOO_PASSWORD=-KsZAxbX2!Fn36g

# DISC API
DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC

# Harrison API (if using)
HARRASON_API_URL=<your_harrison_api_url>
HARRASON_CREDENTIAL=<your_harrison_credential>

# Email Configuration
SMTP_EMAIL=info@inowix.in
SMTP_PASSWORD=jxrmhihcvqlqojqa
FROM_NAME=Bodhi Training Solutions
REPLY_TO_EMAIL=support@bodhih.com
```

**How to Check:**
1. Go to Vercel Dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Verify all variables are set

### Step 3: Test with Real Payment

**Option A: Small Test Payment**
1. Make a small test purchase (₹5) on your Odoo website
2. Complete the payment
3. Monitor Vercel logs for:
   - Webhook received
   - Odoo query executed
   - Product detected
   - API called
   - Email sent

**Option B: Simulate Payment (Safer for Testing)**
```bash
python test_deployed_webhook.py 35456 vanshjhamb9@gmail.com "Vansh Jhamb"
```

### Step 4: Verify Email Delivery

**Check:**
- Customer receives email with assessment link
- Email contains correct login credentials
- Assessment link works
- Email is from correct sender (Bodhi Training Solutions)

**If email not received:**
- Check SMTP credentials in Vercel
- Verify email address is correct
- Check spam folder
- Review Vercel logs for email errors

### Step 5: Monitor First Real Payment

**When a real payment comes through:**

1. **Check Vercel Logs:**
   - Look for "WEBHOOK RECEIVED"
   - Verify "payment.captured" event
   - Check Odoo query results
   - Verify product detection

2. **Verify Processing:**
   - Order ID extracted correctly
   - Products retrieved from Odoo
   - Correct API called (DISC or Harrison)
   - Email sent successfully

3. **Check Customer:**
   - Customer received email
   - Assessment link works
   - Can access assessment

## 🔧 Configuration Checklist

### Razorpay Configuration
- [ ] Webhook URL set to: `https://bodhih.vercel.app/razorpay-webhook`
- [ ] `payment.captured` event enabled
- [ ] Webhook secret configured (optional but recommended)
- [ ] Test webhook sent and received

### Odoo Configuration
- [ ] Payment description contains order ID or name
- [ ] Orders have products assigned
- [ ] Customer emails are correct in orders

### Vercel Configuration
- [ ] All environment variables set
- [ ] Server is deployed and running
- [ ] Logs are accessible
- [ ] Domain is correct

## 📊 Monitoring Setup

### What to Monitor

1. **Vercel Logs:**
   - Webhook calls
   - Odoo connection status
   - API call results
   - Email sending status

2. **Razorpay Dashboard:**
   - Webhook delivery status
   - Payment success rate
   - Failed webhook deliveries

3. **Odoo:**
   - Order status changes
   - Product availability
   - Customer information accuracy

## 🚨 Troubleshooting

### If Webhook Not Working

1. **Check Razorpay:**
   - Webhook URL is correct
   - Event is enabled
   - Check webhook delivery logs

2. **Check Vercel:**
   - Server is running
   - Logs show webhook received
   - No errors in logs

3. **Test Manually:**
   ```bash
   python test_deployed_webhook.py 35456
   ```

### If Email Not Sending

1. **Check SMTP Settings:**
   - Credentials are correct
   - SMTP server accessible
   - Port 465 (SSL) is open

2. **Check Logs:**
   - Look for "EMAIL SENT" or "EMAIL FAILED"
   - Check error messages

### If Product Not Detected

1. **Check Product Name:**
   - Contains "disc" or "harrison"
   - Case doesn't matter
   - Check Odoo product name

2. **Check Logs:**
   - Product name retrieved from Odoo
   - Detection logic executed
   - Type determined correctly

## 📝 Documentation

### For Your Team

1. **Webhook URL:** `https://bodhih.vercel.app/razorpay-webhook`
2. **Test Endpoint:** `https://bodhih.vercel.app/test-odoo?order_id=ORDER_ID`
3. **Support Email:** support@bodhih.com

### For Customers

- Assessment emails are sent automatically
- Check spam folder if not received
- Contact support@bodhih.com for issues

## 🎉 Success Criteria

You'll know everything is working when:

- [ ] Real payment triggers webhook
- [ ] Odoo query retrieves products
- [ ] Product type detected correctly
- [ ] API account created successfully
- [ ] Customer receives email
- [ ] Customer can access assessment

## 📞 Support

If issues arise:
1. Check Vercel logs first
2. Review Razorpay webhook logs
3. Test endpoints manually
4. Verify environment variables
5. Check Odoo order details

---

## Quick Reference

**Test Webhook:**
```bash
python test_deployed_webhook.py 35456
```

**Test Endpoint:**
```bash
curl "https://bodhih.vercel.app/test-odoo?order_id=35456"
```

**Check Logs:**
- Vercel Dashboard → Your Project → Logs

**Webhook URL:**
```
https://bodhih.vercel.app/razorpay-webhook
```








