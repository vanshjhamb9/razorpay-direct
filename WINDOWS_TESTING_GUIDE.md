# Windows Testing Guide

## ✅ Webhook Test Script Created

I've created `test_webhook_windows.py` which works on Windows.

## 🚀 How to Test

### Option 1: Run Python Script (Recommended)
```bash
python test_webhook_windows.py
```

### Option 2: Run Batch File
```bash
test_webhook_simple.bat
```

### Option 3: PowerShell (Alternative)
```powershell
$body = @{
    event = "payment.captured"
    test = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://bodhih.vercel.app/razorpay-webhook" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

## 📋 Current Status

✅ **Webhook endpoint is accessible** (200 OK response)
❓ **Logs not showing in Vercel** (needs configuration files deployed)

## 🔍 What to Check Now

1. **Verify files are deployed:**
   - `vercel.json` in root
   - `api/index.py` in api/ folder
   - Updated `main.py`

2. **Check Vercel Dashboard:**
   - Latest deployment includes new files
   - Build completed successfully
   - No errors in build logs

3. **Test and check logs:**
   - Run `python test_webhook_windows.py`
   - Immediately check Vercel logs
   - Look for "WEBHOOK ENDPOINT HIT"

## 🎯 Expected Result

After files are deployed, you should see in Vercel logs:

```
WEBHOOK ENDPOINT HIT
Method: POST
Path: /razorpay-webhook
WEBHOOK RECEIVED
Event: payment.captured
```

## 📞 If Still No Logs

1. **Redeploy manually in Vercel**
2. **Check build logs for errors**
3. **Verify all files are committed**
4. **Check Vercel function configuration**


