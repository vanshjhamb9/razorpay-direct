# Verify Vercel Deployment - Webhook Logging Fix

## ✅ Webhook Endpoint is Working
- Status: 200 OK
- Endpoint is accessible
- But logs not showing in Vercel

## 🔍 This Means
The webhook is receiving requests, but Vercel serverless function configuration might not be deployed yet.

## 📋 Verification Checklist

### Step 1: Verify Files Are in Repository

Check these files exist:

1. **vercel.json** (in root directory)
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

2. **api/index.py** (in api/ folder)
   ```python
   from main import app
   handler = app
   ```

3. **main.py** (updated with enhanced logging)

### Step 2: Check Vercel Deployment

1. Go to Vercel Dashboard
2. Check **Deployments** tab
3. Look for latest deployment
4. Check if it includes:
   - vercel.json
   - api/index.py
   - Updated main.py

### Step 3: Check Vercel Build Logs

1. Click on latest deployment
2. Check **Build Logs**
3. Look for:
   - "Building..." messages
   - Python installation
   - Dependencies installation
   - Any errors

### Step 4: Check Vercel Function Logs

1. Go to **Logs** tab
2. Filter by:
   - **Function**: All functions
   - **Time**: Last hour
3. Look for ANY log entries

### Step 5: Test Again

After verifying files are deployed:

```bash
python test_webhook_windows.py
```

Then immediately check Vercel logs.

## 🚨 If Still No Logs

### Option 1: Manual Redeploy

1. Vercel Dashboard → Your Project
2. Go to **Deployments**
3. Click **"..."** on latest deployment
4. Click **"Redeploy"**
5. Wait for deployment to complete
6. Test again

### Option 2: Check Vercel Configuration

1. Go to **Settings** → **General**
2. Check **Build & Development Settings**
3. Verify:
   - Framework Preset: Other
   - Build Command: (empty or `pip install -r requirements.txt`)
   - Output Directory: (empty)
   - Install Command: (empty)

### Option 3: Check Function Logs Specifically

1. In Vercel Logs
2. Look for function invocations
3. Check if requests are being routed to functions
4. Look for any error messages

## 📊 What You Should See in Logs

After fix is deployed, when you run `test_webhook_windows.py`, you should see:

```
WEBHOOK ENDPOINT HIT
Method: POST
Path: /razorpay-webhook
URL: https://bodhih.vercel.app/razorpay-webhook
Headers: {...}
WEBHOOK RECEIVED
Event: payment.captured
Time: [timestamp]
Full Payload: {...}
```

## 🔧 Quick Fix Commands

### If using Git:
```bash
# Add files
git add vercel.json api/index.py main.py

# Commit
git commit -m "Fix Vercel webhook routing and logging"

# Push (triggers auto-deploy)
git push
```

### If using Vercel CLI:
```bash
vercel --prod
```

## ✅ Success Indicators

You'll know it's working when:

1. ✅ Vercel logs show "WEBHOOK ENDPOINT HIT"
2. ✅ Logs show request details (method, path, headers)
3. ✅ Logs show "WEBHOOK RECEIVED" with event details
4. ✅ Real payments trigger logs automatically

## 📝 Next Steps

1. **Verify files are in repository**
2. **Check Vercel deployment includes new files**
3. **Redeploy if needed**
4. **Test with `python test_webhook_windows.py`**
5. **Check Vercel logs immediately after test**
6. **Make real payment and verify logs appear**


