# Email and DISC API Fixes Summary

## Issues Fixed

### 1. Email Showing Order ID Instead of Product Name ✅

**Problem:**
- Email was showing "SO-05231-3" (order ID) instead of the actual product name like "Sales Report" or "Communication Report"
- This happened because when Odoo product names were empty, the code fell back to using the `description` field, which contains the order ID

**Fix Applied:**
- Updated `send_email()` function to accept `product_name` parameter
- Updated `process_single_user()` to pass `product_name` to `send_email()`
- Added checks to prevent using order IDs (starting with "SO-") as product names
- When product name is an order ID, falls back to "Assessment Report" instead
- Added better logging to show what product name is being used

**Files Changed:**
- `api/razorpay-webhook.py`:
  - `send_email()`: Added `product_name` parameter, uses it in email subject and body
  - `process_single_user()`: Passes `product_name` to `send_email()`
  - Webhook handler: Added checks to avoid using order IDs as product names

---

### 2. DISC API Receiving "Basic" Instead of Correct Report Type ✅

**Problem:**
- When product name was "SO-05231-3" (order ID), `extract_report_type()` returned "Basic"
- DISC API was receiving "Basic" instead of the actual report type (e.g., "Sales", "Communication")

**Fix Applied:**
- Prevented order IDs from being used as product names
- Report type extraction now works on actual product names, not order IDs
- Added better logging to show what report type is being sent to DISC API

**Files Changed:**
- `api/razorpay-webhook.py`:
  - `register_on_disc_asia()`: Added detailed logging for request/response
  - Webhook handler: Added checks to extract product names correctly before extracting report type

---

## What to Check in Vercel Logs

After deployment, check the logs for:

### 1. Product Name Extraction
Look for lines like:
```
-> Processing Product: Sales Report - DISC
  Type: DISC | Report: Sales
```

**Should see:** Actual product name (e.g., "Sales Report", "Communication Report")
**Should NOT see:** Order ID like "SO-05231-3"

### 2. Email Sending
Look for lines like:
```
EMAIL SENT -> customer@example.com (Product: Sales Report - DISC)
```

**Should see:** Actual product name in parentheses
**Should NOT see:** Order ID in parentheses

### 3. DISC API Request
Look for lines like:
```
-> DISC API Call: https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
-> Request: Name=John Doe, Email=john@example.com, Type=Sales
-> Request Payload: {
  "credentials": {...},
  "respondentDetails": [{
    "name": "John Doe",
    "type": "Sales"  <-- Should be "Sales", "Communication", etc., NOT "Basic"
  }]
}
```

**Should see:** Correct report type (e.g., "Sales", "Communication", "Managerial")
**Should NOT see:** "Basic" unless it's actually a Basic report

### 4. DISC API Response
Look for lines like:
```
-> Response Status: 200
-> Response JSON: {
  "success": true,
  "respondentDetails": [{
    "link": "https://discreport.discasiaplus.org/login?token=...",
    "respondentId": 12345
  }]
}
[OK] DISC SUCCESS -> Link: https://discreport.discasiaplus.org/login?token=...
[OK] DISC SUCCESS -> Respondent ID: 12345
```

**Should see:** Success response with link and respondent ID

---

## Testing Checklist

### Test 1: Email Shows Product Name
1. Make a test purchase of a "Sales Report" or "Communication Report"
2. Check the email you receive
3. **Verify:** Email shows "Sales Report" or "Communication Report" (NOT "SO-05231-3")
4. **Verify:** Subject line shows "Your Sales Report is Ready!" (or appropriate product name)

### Test 2: DISC API Receives Correct Report Type
1. Check Vercel logs after a purchase
2. **Verify:** DISC API request shows correct `type` field (e.g., "Sales", "Communication")
3. **Verify:** DISC API response shows success with link and respondent ID

### Test 3: Multiple Report Types
1. Test with different report types:
   - Sales Report → Should send "Sales" to DISC API
   - Communication Report → Should send "Communication" to DISC API
   - Managerial Report → Should send "Managerial" to DISC API
   - Advanced Report → Should send "Advanced" to DISC API
2. **Verify:** Each type is correctly identified and sent to DISC API

---

## How It Works Now

1. **Order Received from Razorpay**
   - Webhook extracts order ID (e.g., "SO-05231-3")
   - Queries Odoo database for order details

2. **Product Name Extraction**
   - If Odoo order found:
     - Extracts `product_name` from Odoo order line
     - If product_name is empty, uses `line_name`
     - If both are empty or order ID, uses "Assessment Report"
   - If Odoo order not found:
     - Checks Razorpay order notes for product name
     - If not found, uses "Assessment Report" (NOT order ID)

3. **Report Type Extraction**
   - Extracts report type from product name using `extract_report_type()`
   - Looks for keywords: "Sales", "Communication", "Managerial", "Advanced", "Student", "Career", "Full", "Basic"
   - Returns appropriate report type

4. **DISC API Call**
   - Sends request with correct report type in `type` field
   - Logs full request and response for debugging

5. **Email Sending**
   - Uses actual product name in email subject and body
   - Shows "Sales Report" instead of "SO-05231-3"
   - Includes assessment link and password

---

## Expected Behavior After Fix

✅ **Email shows:** "Sales Report" or "Communication Report" (actual product name)
✅ **DISC API receives:** "Sales", "Communication", etc. (correct report type)
✅ **Logs show:** Detailed information about product name and report type
✅ **No more:** Order IDs ("SO-05231-3") in emails or "Basic" as default report type

---

## Deployment Status

✅ Code changes committed and pushed to GitHub
✅ Vercel should automatically deploy (check Vercel dashboard)
✅ Wait 1-2 minutes for deployment to complete
✅ Test with a new purchase to verify fixes

---

## If Issues Persist

1. **Check Vercel Logs:**
   - Look for "Processing Product:" messages
   - Verify product names are being extracted correctly
   - Check DISC API request/response logs

2. **Check Odoo Database:**
   - Verify products have proper names in Odoo
   - Check if `product_name` or `line_name` fields are populated

3. **Check Product Descriptions:**
   - Verify product descriptions in Odoo contain report type keywords
   - Examples: "Sales Report", "Communication Report", "Managerial Report"

4. **Contact Support:**
   - If product names are still showing as order IDs
   - If DISC API is still receiving "Basic" instead of correct type
   - Provide Vercel logs and order ID for debugging
