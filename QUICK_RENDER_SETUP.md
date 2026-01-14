# Quick Render Setup - 5 Minute Guide

## ✅ Files Ready

- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Includes gunicorn
- ✅ `main.py` - Updated for Render
- ✅ All code ready to deploy

## 🚀 Quick Deployment Steps

### 1. Go to Render
Visit: https://render.com and sign in (use GitHub)

### 2. Create New Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repo: `razorpay-direct`
- Render will auto-detect `render.yaml`

### 3. Set Environment Variables
In Render dashboard → **Environment** tab, add these:

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

### 4. Deploy
- Click **"Create Web Service"**
- Wait 2-3 minutes
- Get your URL: `https://your-app.onrender.com`

### 5. Update Razorpay Webhook
- Go to Razorpay Dashboard → Settings → Webhooks
- Set URL: `https://your-app.onrender.com/razorpay-webhook`
- Save

### 6. Test
```powershell
Invoke-WebRequest -Uri "https://your-app.onrender.com/razorpay-webhook" -Method GET
```

**Expected:** `{"status": "webhook_endpoint_active", "method": "GET"}`

## ✅ Done!

Your webhook is now live on Render! 🎉
