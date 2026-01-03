# Simple Vercel Fix - Removed Complex Structure

## Problem
Vercel was having issues with the api/ folder structure and handler format.

## Solution
Simplified to use main.py directly with vercel.json routing.

## Changes Made

### 1. vercel.json - Simplified
- Routes all requests to main.py
- No complex api/ folder structure needed
- Vercel handles Flask apps automatically

### 2. main.py - Added handler export
- Exports `handler = app` when imported (for Vercel)
- Runs normally when executed directly

### 3. Removed Complex api/ Files
- No longer needed with simplified approach
- Vercel can use main.py directly

## Deployment

1. **Commit changes:**
   ```bash
   git add vercel.json main.py
   git commit -m "Simplify Vercel deployment - use main.py directly"
   git push
   ```

2. **Vercel will auto-deploy**

3. **Test:**
   ```bash
   python test_webhook_windows.py
   ```

## Expected Result

- ✅ Build succeeds
- ✅ No handler errors
- ✅ Webhook works
- ✅ Logs appear in Vercel

## File Structure

```
your-repo/
├── vercel.json      (routes to main.py)
├── main.py          (Flask app with handler export)
├── requirements.txt
└── ...other files
```

No api/ folder needed!

