# Render Deployment Guide - Complete Steps

## ✅ What We've Done

1. **Created `render.yaml`** - Render configuration file
2. **Updated `requirements.txt`** - Added `gunicorn` for production server
3. **Updated `main.py`** - Removed Vercel-specific comments
4. **Verified Flask app structure** - Ready for Render deployment

## 🚀 Step-by-Step Deployment on Render

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up or log in (you can use GitHub to sign in)

### Step 2: Connect Your Repository

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select your repository: `razorpay-direct` (or your repo name)
4. Click **"Connect"**

### Step 3: Configure the Service

**Basic Settings:**
- **Name:** `bodhih-webhook` (or any name you prefer)
- **Region:** Choose closest to your users (e.g., `Singapore` or `Mumbai`)
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave empty (root of repo)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn main:app`

**OR Use render.yaml (Recommended):**
- Render will automatically detect `render.yaml` and use those settings
- Just click **"Apply"** after connecting the repo

### Step 4: Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC
HARRASON_API_URL=
HARRASON_CREDENTIAL=
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
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

**Important:** Replace `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` with your actual Razorpay credentials.

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start the service with `gunicorn main:app`
3. Wait for deployment to complete (usually 2-3 minutes)

### Step 6: Get Your Webhook URL

After deployment:
1. Render will provide a URL like: `https://bodhih-webhook.onrender.com`
2. Your webhook endpoint will be: `https://bodhih-webhook.onrender.com/razorpay-webhook`
3. Copy this URL

### Step 7: Update Razorpay Webhook URL

1. Go to Razorpay Dashboard: https://dashboard.razorpay.com
2. Navigate to **Settings** → **Webhooks**
3. Update your webhook URL to: `https://bodhih-webhook.onrender.com/razorpay-webhook`
4. Save changes

### Step 8: Test the Deployment

**Test Webhook Endpoint:**
```powershell
Invoke-WebRequest -Uri "https://bodhih-webhook.onrender.com/razorpay-webhook" -Method GET
```

**Expected Response:**
```json
{"status": "webhook_endpoint_active", "method": "GET"}
```

**Test Odoo Connection:**
```powershell
Invoke-WebRequest -Uri "https://bodhih-webhook.onrender.com/test-odoo?order_id=35473" -Method GET
```

## 📋 Render vs Vercel Differences

| Feature | Vercel | Render |
|---------|--------|--------|
| **Structure** | Requires `api/` folder | Uses `main.py` directly |
| **Handler** | Function handler | Flask app (WSGI) |
| **Server** | Serverless functions | Persistent web service |
| **Configuration** | `vercel.json` | `render.yaml` |
| **WSGI Server** | Built-in | Gunicorn (explicit) |

## ✅ Advantages of Render

1. **No Handler Detection Issues** - Uses standard Flask/WSGI
2. **Persistent Service** - Always running (no cold starts)
3. **Better for Webhooks** - More reliable for long-running processes
4. **Easier Debugging** - Standard Flask app structure
5. **Free Tier Available** - Good for testing

## 🔍 Monitoring & Logs

**View Logs:**
1. Go to Render dashboard
2. Click on your service
3. Click **"Logs"** tab
4. Real-time logs will appear

**Check Service Status:**
- Green = Running
- Yellow = Deploying
- Red = Error

## 🚨 Troubleshooting

**If deployment fails:**
1. Check **Logs** tab for error messages
2. Verify all environment variables are set
3. Check `requirements.txt` has all dependencies
4. Ensure `gunicorn` is in requirements.txt

**If webhook doesn't work:**
1. Check Render logs for incoming requests
2. Verify Razorpay webhook URL is correct
3. Test with GET request first
4. Check environment variables are set correctly

## 📝 Next Steps After Deployment

1. ✅ Test webhook endpoint
2. ✅ Make a test payment on Odoo site
3. ✅ Check Render logs for webhook processing
4. ✅ Verify email is sent to customer
5. ✅ Check Odoo order status is updated

## 🎯 Summary

**Files Changed:**
- ✅ `render.yaml` - Created
- ✅ `requirements.txt` - Added gunicorn
- ✅ `main.py` - Removed Vercel comments

**No Changes Needed:**
- ✅ Flask routes work as-is
- ✅ Environment variables work as-is
- ✅ All functionality preserved

**Deployment Time:** ~5 minutes

---

**Ready to deploy! Follow the steps above and your webhook will be live on Render!** 🚀
