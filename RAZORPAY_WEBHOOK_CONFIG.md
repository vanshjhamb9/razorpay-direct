# Razorpay Webhook Configuration - CORRECT SETTINGS

## ⚠️ CRITICAL: Webhook URL

### ✅ CORRECT Webhook URL:
```
https://bodhih.vercel.app/razorpay-webhook
```

### ❌ WRONG Webhook URLs (DO NOT USE):
```
https://bodhih.odoo.com/xmlrpc/2/object  ❌ This is Odoo API, not webhook!
https://bodhih.odoo.com/razorpay-webhook  ❌ Odoo doesn't have this endpoint
http://bodhih.vercel.app/razorpay-webhook  ❌ Must use HTTPS
```

## 📋 Razorpay Webhook Settings

### Step-by-Step Configuration:

1. **Log in to Razorpay Dashboard**
   - Go to: https://dashboard.razorpay.com/

2. **Navigate to Webhooks**
   - Click **Settings** (gear icon)
   - Click **Webhooks** in left menu

3. **Add/Edit Webhook**
   - Click **"Add New Webhook"** or edit existing
   - **Webhook URL**: `https://bodhih.vercel.app/razorpay-webhook`
   - **Events**: Enable `payment.captured` ✅
   - **Secret**: (Optional but recommended)
   - Click **Save**

4. **Verify Configuration**
   - Webhook URL should be exactly: `https://bodhih.vercel.app/razorpay-webhook`
   - Status should show as "Active"
   - `payment.captured` event should be enabled

## 🔍 How to Verify Webhook is Correct

### Test 1: Check Webhook URL
- In Razorpay Dashboard → Webhooks
- Verify URL is: `https://bodhih.vercel.app/razorpay-webhook`
- Should NOT be Odoo URL

### Test 2: Send Test Webhook
- In Razorpay Dashboard → Webhooks
- Click on your webhook
- Click **"Send Test Webhook"**
- Check Vercel logs for receipt

### Test 3: Check Delivery Logs
- In Razorpay Dashboard → Webhooks → Delivery Logs
- Should show successful deliveries (200 status)
- Click on an event to see details

## 🎯 Complete Webhook Flow

```
1. Customer makes payment on Odoo website
   ↓
2. Razorpay processes payment
   ↓
3. Razorpay sends webhook to: https://bodhih.vercel.app/razorpay-webhook
   ↓
4. Vercel receives webhook
   ↓
5. Flask app processes webhook
   ↓
6. Queries Odoo database
   ↓
7. Creates account on DISC/Harrison API
   ↓
8. Sends email to customer
```

## ✅ Verification Checklist

- [ ] Webhook URL in Razorpay is: `https://bodhih.vercel.app/razorpay-webhook`
- [ ] Webhook is Active in Razorpay
- [ ] `payment.captured` event is enabled
- [ ] Test webhook sent successfully
- [ ] Vercel logs show webhook received
- [ ] Real payment triggers processing

## 🚨 Common Mistakes

1. **Using Odoo URL instead of Vercel URL** ❌
   - Wrong: `https://bodhih.odoo.com/xmlrpc/2/object`
   - Correct: `https://bodhih.vercel.app/razorpay-webhook`

2. **Using HTTP instead of HTTPS** ❌
   - Wrong: `http://bodhih.vercel.app/razorpay-webhook`
   - Correct: `https://bodhih.vercel.app/razorpay-webhook`

3. **Missing /razorpay-webhook path** ❌
   - Wrong: `https://bodhih.vercel.app`
   - Correct: `https://bodhih.vercel.app/razorpay-webhook`

4. **Event not enabled** ❌
   - Must enable `payment.captured` event
   - Other events won't trigger processing

## 📞 If Still Not Working

1. **Double-check webhook URL** in Razorpay
2. **Verify Vercel deployment** is live
3. **Check Razorpay delivery logs** for errors
4. **Test manually** with `python test_webhook_windows.py`
5. **Check Vercel logs** immediately after test

## 🎉 Success Indicators

You'll know it's working when:

- ✅ Razorpay shows webhook delivered (200)
- ✅ Vercel logs show "WEBHOOK RECEIVED"
- ✅ Vercel logs show "Event: payment.captured"
- ✅ Vercel logs show Odoo query
- ✅ Vercel logs show API call
- ✅ Vercel logs show email sent
- ✅ Customer receives email


