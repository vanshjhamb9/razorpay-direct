# Quick Fix Instructions - Webhook Not Receiving Requests

## 🚨 Problem
Razorpay shows webhook success (200) but Vercel logs show nothing. Requests aren't reaching the Flask app.

## ✅ Solution - 3 Files to Add/Update

### File 1: vercel.json (NEW - Add to root directory)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/razorpay-webhook",
      "dest": "main.py"
    },
    {
      "src": "/test-odoo",
      "dest": "main.py"
    },
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### File 2: api/index.py (NEW - Create api/ folder first)

```python
"""
Vercel serverless function entry point
"""
from main import app

# Export the Flask app for Vercel
handler = app
```

### File 3: main.py (ALREADY UPDATED)
- Enhanced webhook logging
- Added catch-all route
- Already done ✅

## 📋 Steps to Fix

### Step 1: Add Files
1. Create `vercel.json` in root directory
2. Create `api/` folder
3. Create `api/index.py` inside api folder
4. Copy the code above into each file

### Step 2: Commit and Push
```bash
git add vercel.json api/index.py main.py
git commit -m "Fix Vercel webhook routing"
git push
```

### Step 3: Vercel Auto-Deploys
- Vercel will detect changes
- Auto-deploy will start
- Wait for deployment to complete

### Step 4: Test
1. Make a test payment
2. Check Vercel logs
3. Should now see webhook requests!

## 🔍 What to Look For in Logs

After fix, you should see:
```
WEBHOOK ENDPOINT HIT
Method: POST
Path: /razorpay-webhook
WEBHOOK RECEIVED
Event: payment.captured
```

## ⚠️ Important Notes

1. **api/index.py** must be in `api/` folder (not root)
2. **vercel.json** must be in root directory
3. **Redeploy** after adding files
4. **Check build logs** in Vercel for errors

## 🧪 Test After Fix

```bash
# Test endpoint
curl "https://bodhih.vercel.app/test-odoo?order_id=35456"

# Test webhook manually
curl -X POST https://bodhih.vercel.app/razorpay-webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "payment.captured", "test": true}'
```

Both should show logs in Vercel!



