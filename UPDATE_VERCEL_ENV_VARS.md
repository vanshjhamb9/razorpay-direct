# Update Vercel Environment Variables - URGENT FIX

## Problem
Email is failing because Vercel environment variables still have old SMTP settings:
- **Current (WRONG)**: `SMTP_EMAIL=info@inowix.in` ❌
- **Should be**: `SMTP_EMAIL=assessments@bodhih.com` ✅

## Solution: Update Vercel Environment Variables

### Step 1: Go to Vercel Dashboard
1. Go to: https://vercel.com/dashboard
2. Login to your account
3. Select project: **bodhih** (or your project name)

### Step 2: Navigate to Environment Variables
1. Click on your project
2. Go to **Settings** (top menu)
3. Click **Environment Variables** (left sidebar)

### Step 3: Update SMTP Variables

Update these variables:

#### Required Changes:

1. **SMTP_EMAIL**
   - **Current**: `info@inowix.in` ❌
   - **Change to**: `assessments@bodhih.com` ✅

2. **SMTP_PASSWORD**
   - **Current**: `jxrmhihcvqlqojqa` (old password)
   - **Change to**: `L[E0xV7bE1,Y` ✅

3. **SMTP_SERVER** (NEW - Add if doesn't exist)
   - **Value**: `mail.bodhih.com`

4. **SMTP_PORT** (NEW - Add if doesn't exist)
   - **Value**: `465`

### Step 4: How to Edit Environment Variables

For each variable:

1. Find the variable in the list (e.g., `SMTP_EMAIL`)
2. Click **Edit** or **...** (three dots) → **Edit**
3. Change the value to the new one
4. Select **Environment**: Make sure it's set for **Production** (and optionally Preview/Development)
5. Click **Save**

Or **Delete and Re-add**:

1. Find the variable
2. Click **Delete** to remove old one
3. Click **Add New** to add new variable with correct value

### Step 5: Required Environment Variables (Complete List)

Make sure all these are set:

```bash
# SMTP Configuration (CRITICAL - UPDATE THESE)
SMTP_EMAIL=assessments@bodhih.com
SMTP_PASSWORD=L[E0xV7bE1,Y
SMTP_SERVER=mail.bodhih.com
SMTP_PORT=465
FROM_NAME=Bodhi Training Solutions
REPLY_TO_EMAIL=support@bodhih.com

# Odoo Configuration
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=siddharthan@bodhih.com
ODOO_PASSWORD=-KsZAxbX2!Fn36g

# DISC API
DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC

# Razorpay API (optional - for fetching order details)
RAZORPAY_KEY_ID=<your_razorpay_key_id>
RAZORPAY_KEY_SECRET=<your_razorpay_key_secret>
```

### Step 6: Redeploy After Updating

After updating environment variables:

1. **Option A: Automatic Redeploy**
   - Vercel will automatically redeploy when env vars change
   - Wait 1-2 minutes for redeploy

2. **Option B: Manual Redeploy**
   - Go to **Deployments** tab
   - Click **...** (three dots) on latest deployment
   - Click **Redeploy**

### Step 7: Verify Environment Variables

After redeploy, check logs:

1. Go to **Deployments** → Latest deployment
2. Click **Logs** or **View Logs**
3. Look for startup logs that show:
   ```
   -> Using email: assessments@bodhih.com  ✅
   ```
   Instead of:
   ```
   -> Using email: info@inowix.in  ❌
   ```

## Quick Fix Summary

**What to Update in Vercel:**
1. `SMTP_EMAIL` → Change from `info@inowix.in` to `assessments@bodhih.com`
2. `SMTP_PASSWORD` → Change to `L[E0xV7bE1,Y`
3. `SMTP_SERVER` → Add/Update to `mail.bodhih.com`
4. `SMTP_PORT` → Add/Update to `465`

**After updating:**
- Wait for redeploy (1-2 minutes)
- Test with new purchase
- Check email inbox

## Why This Happens

Vercel environment variables **override** code defaults. Even though we set defaults in code:
```python
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "assessments@bodhih.com")
```

If `SMTP_EMAIL` exists in Vercel environment variables, it uses that value instead of the default.

## Current Status

- ✅ Webhook is receiving `order.paid` events
- ✅ Processing orders correctly
- ✅ DISC API calls successful
- ❌ Email failing due to wrong SMTP credentials in Vercel env vars

## After Fix

Once environment variables are updated:
- ✅ Emails will send successfully
- ✅ Customers will receive assessment emails
- ✅ Order status will update in Odoo
