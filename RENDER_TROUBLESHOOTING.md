# Render Deployment - Troubleshooting

## 🚨 Current Issues

**Status:** Service is live but endpoints returning errors:
- `/razorpay-webhook` → 500 Internal Server Error
- `/test-odoo` → 500 Internal Server Error  
- `/` → 404 Not Found

## 🔍 How to Check Logs

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click on your service: `razorpay-direct-80bm`
3. Click **"Logs"** tab
4. Look for error messages

## 🔧 Common Issues & Fixes

### Issue 1: Missing Environment Variables

**Symptom:** 500 errors, application crashes on startup

**Fix:**
1. Go to Render dashboard → Your service → **Environment** tab
2. Add all required environment variables:
   ```
   DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
   DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC
   SMTP_EMAIL=assessments@bodhih.com
   SMTP_PASSWORD=L[E0xV7bE1,Y
   SMTP_SERVER=mail.bodhih.com
   SMTP_PORT=465
   FROM_NAME=Bodhi Training Solutions
   REPLY_TO_EMAIL=support@bodhih.com
   ODOO_URL=https://bodhih.odoo.com
   ODOO_DB=bodhih
   ODOO_USERNAME=siddharthan@bodhih.com
   ODOO_PASSWORD=-KsZAxbX2!Fn36g
   RAZORPAY_KEY_ID=your_key_here
   RAZORPAY_KEY_SECRET=your_secret_here
   ```
3. Click **"Save Changes"**
4. Service will auto-redeploy

### Issue 2: Application Startup Error

**Symptom:** Service shows as "Live" but endpoints don't work

**Check:**
- Look at logs for Python errors
- Check if Flask app is starting correctly
- Verify gunicorn is running

### Issue 3: Route Not Found (404)

**Symptom:** Root path `/` returns 404

**Note:** This is expected - the root path returns 404 by design. The webhook endpoint should work.

## ✅ Quick Test Commands

**Test webhook (should return JSON):**
```powershell
curl https://razorpay-direct-80bm.onrender.com/razorpay-webhook
```

**Or in browser:**
```
https://razorpay-direct-80bm.onrender.com/razorpay-webhook
```

## 📋 Next Steps

1. **Check Render logs** for specific error messages
2. **Verify environment variables** are set
3. **Check if service is actually running** (not just "Live" status)
4. **Share error logs** if issues persist

## 🎯 Expected Behavior

Once fixed, you should see:
- ✅ `GET /razorpay-webhook` → `{"status": "webhook_endpoint_active", "method": "GET"}`
- ✅ `GET /test-odoo?order_id=35473` → JSON with product data
- ✅ Service logs showing Flask app startup

---

**Please check the Render logs and share any error messages you see!**
