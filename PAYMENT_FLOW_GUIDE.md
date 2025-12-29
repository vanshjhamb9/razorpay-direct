# Payment Flow Guide - What Happens When Payment is Made

## Complete Flow

```
1. Customer makes payment on Odoo website
   ↓
2. Razorpay processes payment
   ↓
3. Razorpay sends webhook to /razorpay-webhook
   ↓
4. Webhook extracts Odoo order ID from:
   - Description field (e.g., "35456" or "SO-05223")
   - Notes field (sale_order_id, order_id, or odoo_order_id)
   ↓
5. Webhook queries Odoo database via XML-RPC
   - Gets products sold in that order
   ↓
6. System detects product type:
   - If product name contains "disc" → DISC Asia+ API
   - If product name contains "harrison/harrason" → Harrison API
   ↓
7. Creates account on appropriate API
   ↓
8. Sends email to customer with:
   - Assessment link
   - Login credentials
```

## Important: Order ID Must Be in Payment Description

For the system to work, the **Odoo sale order ID or name must be in the Razorpay payment description**.

### Option 1: Order ID in Description
```
Description: "35456"
```
The webhook will use this directly as the Odoo order ID.

### Option 2: Order Name in Description
```
Description: "SO-05223"
```
The webhook will search for this order name in Odoo.

### Option 3: Order ID in Notes
```json
{
  "notes": {
    "sale_order_id": "35456",
    "name": "John Doe",
    "user_email": "john@example.com",
    "gender": "Male"
  }
}
```

## What to Check in Logs

When a payment comes through, you'll see in the Flask logs:

```
═══════════════════════════════════════════════════════════════════════════════════════════════
NEW PAYMENT FROM ODOO WEBSITE — BODHIH.COM
═══════════════════════════════════════════════════════════════════════════════════════════════
Time           : 28 Dec 2025, 01:30 PM
Amount         : ₹525.00
Payment ID     : pay_xxxxx
Order ID       : order_xxxxx
Description    : 35456  ← This should contain Odoo order ID
```

Then:
```
→ Querying Odoo database for order: 35456
[OK] Odoo authenticated successfully (UID: 2)
[OK] Found sale order in Odoo: ID 35456
[OK] Found 1 product(s) in Odoo order:
  - Product: Test - DISC Asia+ Basic Report
→ PROCESSING PRODUCTS FROM ODOO DATABASE
→ Processing Product: Test - DISC Asia+ Basic Report
  Type: DISC | Report: Basic
→ DISC API Call: https://discapi.discasiaplus.org/api/DISC/...
[OK] DISC SUCCESS → Link: https://...
[OK] John Doe: DISC ASIA+ Account Created + Email Sent to john@example.com
```

## Testing with Real Payment

1. **Make a payment** through your Odoo website
2. **Check Flask logs** to see:
   - Order ID extraction
   - Odoo query results
   - Product detection
   - API registration
   - Email sending

3. **Verify email** was sent to customer with assessment link

## Troubleshooting

### "Sale order not found in Odoo"
- Check if description contains the correct Odoo order ID
- Verify the order exists in Odoo database
- Check if order ID format is correct (numeric or "SO-XXXXX")

### "No products found"
- Order might not have order lines yet
- Check if order is confirmed in Odoo
- Verify products are added to the sale order

### "Product type not detected"
- Check product names in Odoo contain "disc" or "harrison" keywords
- Review logs to see what product names were retrieved

### "API registration failed"
- Check API credentials are correct
- Verify API endpoints are accessible
- Check API response in logs

## Expected Log Output

Successful payment processing should show:
```
[OK] Successfully retrieved 1 product(s) from Odoo
→ Processing Product: DISC Asia+ Basic Report
  Type: DISC | Report: Basic
[OK] DISC SUCCESS → Link: https://...
[OK] EMAIL SENT → customer@example.com
```

## Next Steps

1. Make a test payment with a product that has "DISC" or "Harrison" in the name
2. Ensure the Odoo order ID is in the payment description
3. Monitor Flask logs for the complete flow
4. Verify customer receives email with assessment link

