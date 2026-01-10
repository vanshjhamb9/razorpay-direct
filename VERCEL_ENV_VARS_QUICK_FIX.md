# QUICK FIX: Update Vercel Environment Variables

## The Problem
Your Vercel environment variables still have the **old SMTP email** (`info@inowix.in`) instead of the new one (`assessments@bodhih.com`).

## The Fix (2 Minutes)

### Go to Vercel Dashboard
1. Visit: https://vercel.com/dashboard
2. Select your project: **bodhih**
3. Go to: **Settings** → **Environment Variables**

### Update These 4 Variables:

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `SMTP_EMAIL` | `info@inowix.in` ❌ | `assessments@bodhih.com` ✅ |
| `SMTP_PASSWORD` | `jxrmhihcvqlqojqa` | `L[E0xV7bE1,Y` ✅ |
| `SMTP_SERVER` | (may not exist) | `mail.bodhih.com` ✅ |
| `SMTP_PORT` | (may not exist) | `465` ✅ |

### Steps:
1. **Find** each variable in the list
2. **Edit** it (or Delete and Add New if easier)
3. **Set Environment** to: Production (and optionally Preview/Development)
4. **Save**

### After Updating:
- Wait 1-2 minutes for auto-redeploy
- Test with new purchase
- Check email inbox

## Why Emails Are Failing

From your logs:
```
-> Using email: info@inowix.in  ❌ WRONG!
EMAIL FAILED -> (535, b'Incorrect authentication data')
```

This means Vercel is using the old email address from environment variables, not the new default in code.

## Verification

After redeploy, check logs - you should see:
```
-> Using email: assessments@bodhih.com  ✅ CORRECT!
EMAIL SENT -> vanshjhamb9@gmail.com
```
