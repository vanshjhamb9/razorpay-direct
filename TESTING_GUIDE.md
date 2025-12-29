# Testing Guide for Odoo XML-RPC Integration

This guide explains how to test the Odoo integration to ensure it's working correctly.

## Quick Test Methods

### Method 1: Test Endpoint (Easiest)

The Flask app includes a test endpoint you can access directly:

1. **Start your Flask server:**
   ```bash
   python main.py
   ```

2. **Test with a browser or curl:**
   
   **Using Order ID:**
   ```
   http://localhost:5000/test-odoo?order_id=35473
   ```
   
   **Using Order Name:**
   ```
   http://localhost:5000/test-odoo?order_id=SO-05200-5
   ```

   **Using curl:**
   ```bash
   curl "http://localhost:5000/test-odoo?order_id=35473"
   ```

3. **Expected Response:**
   ```json
   {
     "success": true,
     "sale_order_id": 35473,
     "products": [
       {
         "product_id": 123,
         "product_name": "DISC Basic Report",
         "line_name": "DISC Basic Report",
         "quantity": 1,
         "price_unit": 525.0,
         "price_subtotal": 525.0,
         "detected_type": "DISC"
       }
     ],
     "message": "Successfully retrieved 1 product(s) from Odoo"
   }
   ```

---

### Method 2: Standalone Odoo Connection Test

Test the Odoo connection independently:

1. **Run the test script:**
   ```bash
   python test_odoo_connection.py
   ```

2. **Test with a specific order:**
   ```bash
   python test_odoo_connection.py 35473
   ```
   
   Or with order name:
   ```bash
   python test_odoo_connection.py SO-05200-5
   ```

3. **What it tests:**
   - ✅ Odoo connection and authentication
   - ✅ Listing recent sale orders
   - ✅ Querying products from a specific order
   - ✅ Product type detection (DISC/Harrison)

---

### Method 3: Full Webhook Test

Test the complete webhook flow with Odoo integration:

1. **Update test payloads:**
   - Open `test_odoo_webhook.py`
   - Replace order IDs with actual Odoo order IDs from your database
   - Update customer email addresses if needed

2. **Run the test:**
   ```bash
   python test_odoo_webhook.py
   ```
   
   Or with webhook URL:
   ```bash
   python test_odoo_webhook.py https://your-app-url.repl.co
   ```

3. **What it tests:**
   - ✅ Webhook receives payment event
   - ✅ Extracts order ID from description/notes
   - ✅ Queries Odoo database
   - ✅ Detects product type
   - ✅ Routes to appropriate API (DISC/Harrison)
   - ✅ Sends email to customer

---

## Step-by-Step Testing Process

### Step 1: Verify Odoo Connection

```bash
python test_odoo_connection.py
```

**Expected Output:**
```
✓ Odoo Version: 18.0
✓ Authentication successful! User ID: 2
✓ Found 5 sale order(s)
```

**If it fails:**
- Check `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` environment variables
- Verify credentials are correct
- Check network connectivity to Odoo server

---

### Step 2: Find a Test Order

From the output of Step 1, note down a sale order ID (e.g., `35473`).

Or query Odoo directly:
```bash
python test_odoo_connection.py
# Look for order IDs in the output
```

---

### Step 3: Test Product Retrieval

```bash
python test_odoo_connection.py 35473
```

**Expected Output:**
```
✓ Found sale order in Odoo: ID 35473
✓ Found 1 product(s):
  Product Name: DISC Basic Report
  → Detected Type: DISC
```

**Verify:**
- Products are retrieved correctly
- Product names are shown
- Product type is detected (DISC or HARRISON)

---

### Step 4: Test Webhook Integration

1. **Update `test_odoo_webhook.py`:**
   - Set `description` to your test order ID: `"description": "35473"`
   - Or use order name: `"description": "SO-05200-5"`

2. **Run test:**
   ```bash
   python test_odoo_webhook.py
   ```

3. **Check Flask logs** for:
   - `→ Querying Odoo database for order: 35473`
   - `✓ Successfully retrieved X product(s) from Odoo`
   - `✓ Product identified as DISC/HARRISON`
   - `✓ DISC/HARRISON Account Created + Email Sent`

---

### Step 5: Test with Real Payment (Optional)

1. Make a test payment through your Odoo website
2. Ensure the Razorpay description contains the Odoo order ID or name
3. Check webhook logs to verify:
   - Odoo query executed
   - Products retrieved
   - Account created on appropriate API
   - Email sent to customer

---

## Troubleshooting

### Issue: "Odoo authentication failed"

**Solutions:**
- Verify `ODOO_USERNAME` and `ODOO_PASSWORD` are correct
- Check if user has access to `sale.order` and `sale.order.line` models
- Try logging into Odoo web interface with same credentials

### Issue: "Sale order not found"

**Solutions:**
- Verify the order ID exists in Odoo
- Check if using correct format (numeric ID vs. name like "SO-05200-5")
- Ensure order is in the correct database

### Issue: "No products found"

**Solutions:**
- Verify the sale order has order lines
- Check if order lines are not cancelled
- Verify product fields are accessible

### Issue: "Product type not detected"

**Solutions:**
- Check product names in Odoo contain "disc" or "harrison" keywords
- Review logs to see what product names were retrieved
- Update product names in Odoo if needed

---

## Test Checklist

Before going live, verify:

- [ ] Odoo connection works (`test_odoo_connection.py`)
- [ ] Can retrieve products from a test order
- [ ] Product type detection works (DISC vs Harrison)
- [ ] Webhook test endpoint works (`/test-odoo`)
- [ ] Full webhook flow works (`test_odoo_webhook.py`)
- [ ] DISC API registration works
- [ ] Harrison API registration works (if configured)
- [ ] Email sending works
- [ ] Logs show all steps clearly

---

## Environment Variables Checklist

Ensure these are set:

```bash
# Odoo
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=2
ODOO_PASSWORD=-KsZAxbX2!Fn36g

# APIs
DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC
HARRASON_API_URL=<your_url>
HARRASON_CREDENTIAL=<your_credential>

# Email
SMTP_EMAIL=info@inowix.in
SMTP_PASSWORD=jxrmhihcvqlqojqa
```

---

## Quick Test Commands

```bash
# Test Odoo connection
python test_odoo_connection.py

# Test specific order
python test_odoo_connection.py 35473

# Test webhook endpoint
curl "http://localhost:5000/test-odoo?order_id=35473"

# Test full webhook
python test_odoo_webhook.py
```

---

## Need Help?

Check the logs for detailed information:
- Flask server logs show all Odoo queries
- Test scripts show step-by-step progress
- Error messages include tracebacks for debugging

