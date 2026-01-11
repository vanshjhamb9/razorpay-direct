# Complete Testing Guide - All Changes

This guide covers testing for all recent changes:
- SMTP configuration (mail.bodhih.com)
- Email product names (not just "Basic Assessment")
- Odoo order status updates
- DISC API response logging
- Report type extraction

---

## 🚀 Quick Start

### Option 1: Run Complete Test Suite (Recommended)

```bash
# Test deployed server
python TEST_ALL_CHANGES.py

# Test with specific order ID
python TEST_ALL_CHANGES.py 35456

# Test locally (requires Flask server running)
python TEST_ALL_CHANGES.py --local 35456
```

This will test:
- ✅ SMTP connection to mail.bodhih.com
- ✅ Webhook endpoint accessibility
- ✅ Odoo query functionality
- ✅ Report type extraction
- ✅ Full payment flow

---

## 📋 Individual Tests

### 1. Test SMTP Connection

**Purpose:** Verify SMTP server (mail.bodhih.com) is accessible and credentials work.

**Manual Test:**
```python
import smtplib
from email.message import EmailMessage

SMTP_EMAIL = "assessments@bodhih.com"
SMTP_PASSWORD = "L[E0xV7bE1,Y"
SMTP_SERVER = "mail.bodhih.com"
SMTP_PORT = 465

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as s:
        s.login(SMTP_EMAIL, SMTP_PASSWORD)
        msg = EmailMessage()
        msg['From'] = SMTP_EMAIL
        msg['To'] = SMTP_EMAIL  # Send to self
        msg['Subject'] = "Test Email"
        msg.set_content("Test")
        s.send_message(msg)
    print("✓ SMTP connection successful")
except Exception as e:
    print(f"✗ SMTP error: {e}")
```

**Expected Result:**
- ✓ Connection successful
- ✓ Authentication successful
- ✓ Email sent successfully

**What to Check:**
- Email arrives in your inbox
- Email is from `assessments@bodhih.com`

---

### 2. Test Webhook Endpoint

**Purpose:** Verify webhook endpoint is accessible and processes payments.

**Using Test Script:**
```bash
python TEST_ALL_CHANGES.py
```

**Manual Test (Deployed):**
```bash
curl -X POST https://bodhih.vercel.app/razorpay-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.captured",
    "payload": {
      "payment": {
        "entity": {
          "id": "pay_test_123",
          "amount": 1200,
          "description": "Sales Report - DISC",
          "email": "your-email@example.com",
          "notes": {
            "name": "Test Customer",
            "user_email": "your-email@example.com",
            "gender": "Male"
          }
        }
      }
    }
  }'
```

**Manual Test (Local):**
```bash
# Start Flask server first
python main.py

# Then in another terminal:
curl -X POST http://localhost:5000/razorpay-webhook \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Expected Result:**
- Status: 200 OK
- Response: "OK"

**What to Check in Logs:**
- "WEBHOOK ENDPOINT HIT"
- "Event: payment.captured"
- "Processing Product: Sales Report - DISC"
- "Report type: Sales"
- "EMAIL SENT"

---

### 3. Test Odoo Query Endpoint

**Purpose:** Verify Odoo integration retrieves products correctly.

**Using Test Script:**
```bash
python TEST_ALL_CHANGES.py 35456
```

**Manual Test:**
```bash
# Browser
https://bodhih.vercel.app/test-odoo?order_id=35456

# Or curl
curl "https://bodhih.vercel.app/test-odoo?order_id=35456"
```

**Expected Response:**
```json
{
  "success": true,
  "sale_order_id": 35456,
  "products": [
    {
      "product_name": "Sales Report - DISC",
      "line_name": "Sales Report - DISC",
      "detected_type": "DISC",
      "product_id": 123,
      "quantity": 1,
      "price_unit": 12.00
    }
  ],
  "message": "Successfully retrieved 1 product(s) from Odoo"
}
```

**What to Check:**
- Products are retrieved correctly
- Product type detection works (DISC/Harrison)
- Order ID/name matching works

---

### 4. Test Report Type Extraction

**Purpose:** Verify different product names extract correct report types.

**Test Cases:**
| Product Name | Expected Report Type |
|-------------|---------------------|
| Sales Report - DISC | Sales |
| Communication Report - DISC | Communication |
| Basic Assessment | Basic |
| Advanced Report | Advanced |
| Career Report | Career |
| Managerial Report | Managerial |

**Using Test Script:**
```bash
python TEST_ALL_CHANGES.py
```
(Test 4 will run automatically)

**Manual Test:**
Check server logs when processing different products - you should see:
```
[OK] Extracted report type 'Sales' from description: 'Sales Report - DISC'
```

---

### 5. Test Full Payment Flow

**Purpose:** Test complete flow: Payment → Odoo Query → DISC API → Email → Order Update.

**Using Test Script:**
```bash
# With real order ID
python TEST_ALL_CHANGES.py 35456

# The script will simulate a payment for "Sales Report - DISC"
```

**What Happens:**
1. Webhook receives payment.captured event
2. Extracts order ID from description
3. Queries Odoo for products
4. Extracts report type (e.g., "Sales")
5. Calls DISC API with correct report type
6. Sends email with actual product name
7. Updates Odoo order status

**What to Check:**

1. **Email:**
   - ✓ Received confirmation email
   - ✓ Email shows "Sales Report - DISC" (not "Basic Assessment")
   - ✓ Email from: `assessments@bodhih.com`
   - ✓ Contains assessment link

2. **Server Logs:**
   - ✓ "Processing Product: Sales Report - DISC"
   - ✓ "Report type: Sales"
   - ✓ "DISC API Call: ..."
   - ✓ Full DISC API request/response logged
   - ✓ "EMAIL SENT"
   - ✓ "Odoo order status updated"

3. **Odoo (if order exists):**
   - ✓ Order state changed from 'draft' to 'sale'
   - ✓ Payment reference added to order notes

---

## 🧪 Testing with Real Purchase

### Step-by-Step:

1. **Deploy Changes:**
   ```bash
   git add main.py api/razorpay-webhook.py
   git commit -m "Update SMTP config and fix email product names"
   git push
   ```

2. **Wait for Deployment:**
   - Check Vercel dashboard for deployment completion

3. **Make Test Purchase:**
   - Go to Odoo website
   - Add "Sales Report - DISC" to cart
   - Complete payment

4. **Check Email:**
   - Should receive email within 1-2 minutes
   - Email should show "Sales Report - DISC" (not "Basic Assessment")
   - Email should be from `assessments@bodhih.com`

5. **Check Odoo:**
   - Go to "Sales Orders" page
   - Order should appear in list
   - Order state should be "Sale" (not "Draft")
   - Order notes should contain payment ID

6. **Check Logs:**
   - View Vercel logs or server logs
   - Should see full DISC API request/response
   - Should see "Report type: Sales"
   - Should see "EMAIL SENT"

---

## 🔍 Troubleshooting

### Email Not Received

**Check:**
1. SMTP connection test passed?
2. Email address correct in webhook payload?
3. Check spam folder
4. Check server logs for "EMAIL SENT" or "EMAIL FAILED"

**Logs to Check:**
```
-> Connecting to SMTP server: mail.bodhih.com:465
-> Using email: assessments@bodhih.com
EMAIL SENT -> your-email@example.com
```

### Email Shows "Basic Assessment" Instead of Product Name

**Check:**
1. Product name is in Odoo order?
2. Check logs for "Extracted report type" - what does it show?
3. Report type extraction may not be matching product name

**Fix:**
- Check `extract_report_type()` function
- Verify product name in Odoo contains report type keywords
- Check logs for: `"[OK] Extracted report type 'X' from description: 'Y'"`

### Order Not Updating in Odoo

**Check:**
1. Order ID found in Odoo?
2. Check logs for "Updating Odoo order status"
3. Order may require manual confirmation

**Logs to Check:**
```
-> Updating Odoo order status for: 35456
-> Current order state: draft
[OK] Confirmed sale order SO-05223
```

### DISC API Not Working

**Check:**
1. Full request/response logged?
2. Check response status code (should be 200)
3. Check response JSON for "success": true

**Logs to Check:**
```
-> DISC API Call: https://discapi.discasiaplus.org/...
-> Request: Name=... Email=... Type=Sales
-> Response Status: 200
-> Response JSON: {"success": true, "respondentDetails": [...]}
[OK] DISC SUCCESS -> Link: https://...
```

---

## ✅ Testing Checklist

Before going live, verify:

- [ ] SMTP connection test passes
- [ ] Webhook endpoint responds (200 OK)
- [ ] Odoo query endpoint works with real order ID
- [ ] Report type extraction works for all product types
- [ ] Email shows correct product name (not "Basic Assessment")
- [ ] Email is from `assessments@bodhih.com`
- [ ] DISC API responses are fully logged
- [ ] Odoo orders update after payment (if applicable)
- [ ] Full payment flow works end-to-end

---

## 📝 Test Scenarios

### Scenario 1: Sales Report Purchase
- Product: "Sales Report - DISC"
- Expected Email: "Sales Report - DISC"
- Expected Report Type: "Sales"
- Expected DISC API Type: "Sales"

### Scenario 2: Communication Report Purchase
- Product: "Communication Report - DISC"
- Expected Email: "Communication Report - DISC"
- Expected Report Type: "Communication"
- Expected DISC API Type: "Communication"

### Scenario 3: Basic Assessment Purchase
- Product: "Basic Assessment"
- Expected Email: "Basic Assessment"
- Expected Report Type: "Basic"
- Expected DISC API Type: "Basic"

---

## 🚨 Important Notes

1. **Environment Variables:**
   - Make sure SMTP credentials are set in your deployment
   - Check: `SMTP_EMAIL`, `SMTP_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`

2. **Order ID Format:**
   - Odoo order ID can be numeric (e.g., `35456`) or name (e.g., `SO-05223`)
   - Webhook extracts order ID from description field

3. **Report Types:**
   - Must match DISC API valid types exactly
   - Valid types: Basic, Sales, Communication, Advanced, Career, Managerial, etc.

4. **Email Delays:**
   - Email sending may take 10-60 seconds
   - Check logs to confirm email was sent

5. **Odoo Order Updates:**
   - Only updates if order ID is found in Odoo
   - Some orders may require manual confirmation

---

## 📞 Support

If tests fail:
1. Check server logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test each component individually
4. Check network connectivity to mail.bodhih.com
5. Verify Odoo credentials are correct

---

## 🎯 Next Steps After Testing

Once all tests pass:
1. ✅ Deploy to production
2. ✅ Monitor first few real purchases
3. ✅ Verify emails are correct
4. ✅ Check Odoo orders are updating
5. ✅ Monitor DISC API responses
