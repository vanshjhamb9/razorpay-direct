# Next Steps Action Plan - Fix Vercel Deployment Error

## Current Situation

✅ **Handler code is correct** - `api/razorpay-webhook.py` has proper structure  
❌ **Deployment fails** - Vercel handler detection error  
❌ **Webhook not working** - Can't receive Razorpay webhooks  
❌ **Emails not sending** - Because webhook endpoint never starts  

## Root Cause

The error happens when Vercel scans `api/index.py`, which imports `main.py` (Flask app). This triggers Vercel's handler detection code which fails with `TypeError: issubclass() arg 1 must be a class`.

## Action Plan

### Step 1: Isolate the Problem (Test with Only Webhook Handler)

**Goal:** Determine if `api/index.py` is causing the issue

**Actions:**
1. Temporarily disable `api/index.py` by renaming it
2. Update `vercel.json` to remove the catch-all route
3. Deploy and test if webhook handler works

**Expected Result:** If deployment succeeds, we know `api/index.py` is the problem

---

### Step 2: Fix the Import Issue

**If Step 1 succeeds, we have two options:**

#### Option A: Lazy Import (Recommended)
- Modify `api/index.py` to import Flask app only when handler is called
- Prevents Flask initialization during Vercel's handler detection scan

#### Option B: Remove Flask Import
- Make `api/index.py` return a simple 404 response
- Only webhook handler needs to work for now

---

### Step 3: Test Deployment

**After fixing:**
1. Deploy to Vercel
2. Check build logs - should succeed
3. Test webhook endpoint: `GET https://bodhih.vercel.app/razorpay-webhook`
4. Should return: `{"status": "webhook_endpoint_active", "method": "GET"}`

---

### Step 4: Test Full Flow

**Once deployment succeeds:**
1. Make a test payment on Odoo site
2. Check Vercel logs for webhook processing
3. Verify email is sent to customer
4. Check Odoo order status is updated

---

## Immediate Next Steps (Do This Now)

### Option 1: Quick Test (Recommended First)

1. **Temporarily disable `api/index.py`:**
   ```bash
   git mv api/index.py api/index.py.disabled
   ```

2. **Update `vercel.json` to remove catch-all route:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/**/*.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/razorpay-webhook",
         "dest": "/api/razorpay-webhook.py"
       },
       {
         "src": "/test-odoo",
         "dest": "/api/test-odoo.py"
       }
     ]
   }
   ```

3. **Deploy and test:**
   ```bash
   git add vercel.json
   git commit -m "Test: Remove api/index.py to isolate handler detection issue"
   git push
   ```

4. **Check Vercel deployment logs**
   - If it succeeds → `api/index.py` was the problem
   - If it still fails → Issue is elsewhere

### Option 2: Fix Import with Lazy Loading

Modify `api/index.py` to import Flask only when needed:

```python
def handler(request):
    """Lazy import to avoid handler detection issues"""
    # Import Flask app only when handler is called
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from main import app
    
    # Rest of handler code...
```

---

## Success Criteria

✅ **Deployment succeeds** - No TypeError in build logs  
✅ **Webhook endpoint responds** - GET request returns success  
✅ **Razorpay webhooks processed** - Payment events trigger processing  
✅ **Emails sent** - Customers receive assessment emails  
✅ **Odoo updated** - Order status changes to "sale"  

---

## If All Steps Fail

If the error persists after trying all options:

1. **Contact Vercel Support:**
   - Report the `TypeError: issubclass() arg 1 must be a class` error
   - Provide error traceback from build logs
   - Mention it happens during handler detection scan

2. **Alternative Deployment:**
   - Consider using a different platform (Railway, Render, etc.)
   - Or use Vercel's Node.js runtime with Python subprocess

---

## Priority Order

1. **HIGHEST:** Get webhook working (Step 1 - isolate problem)
2. **HIGH:** Fix deployment (Step 2 - fix import)
3. **MEDIUM:** Test full flow (Step 3 & 4)
4. **LOW:** Add back other routes if needed

---

## Quick Command Reference

```bash
# Test webhook endpoint
curl https://bodhih.vercel.app/razorpay-webhook

# Check deployment status
# (Check Vercel dashboard)

# View logs
# (Check Vercel dashboard → Functions → Logs)
```
