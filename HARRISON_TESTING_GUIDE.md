# Harrison Product Testing Guide

Complete testing guide for Harrison/Harrason products, similar to DISC testing.

## Quick Start

### 1. Find Harrison Orders

```bash
python find_harrison_orders.py
```

This will:
- Scan recent orders in Odoo
- Find orders with Harrison/Harrason products
- Display order details and customer information
- Suggest which order to test with

### 2. Test Endpoint

```bash
python test_harrison_endpoint.py [order_id]
```

Example:
```bash
python test_harrison_endpoint.py 35456
```

Or using curl:
```bash
curl "http://localhost:5000/test-odoo?order_id=35456"
```

This tests:
- Odoo connection
- Product retrieval
- Product type detection (should be HARRISON)

### 3. Test Full Webhook

```bash
python test_harrison_webhook.py [order_id]
```

Example:
```bash
python test_harrison_webhook.py 35456
```

This simulates a complete payment webhook and tests:
- Webhook reception
- Odoo query
- Product detection (HARRISON)
- API routing (should go to HARRISON API, not DISC)
- Email sending

## Product Detection

The system detects Harrison products by checking for these keywords in product names:
- `harrison`
- `harrason`
- `harison`
- `harisson`

**Case-insensitive matching**

## Expected Behavior

When a Harrison product is detected:

1. **Product Type**: `HARRISON` (not DISC)
2. **API Called**: HARRISON API endpoint
3. **Email Sent**: To customer with Harrison assessment link

## Verification Checklist

After testing, verify:

- [ ] Order found in Odoo
- [ ] Products retrieved successfully
- [ ] Product type detected as `HARRISON` (not DISC)
- [ ] HARRISON API called (check logs)
- [ ] Email sent to customer
- [ ] Email contains Harrison assessment link

## Common Issues

### Issue: Product Detected as DISC Instead of HARRISON

**Cause**: Product name doesn't contain Harrison keywords

**Solution**:
1. Check product name in Odoo
2. Ensure it contains "harrison" or "harrason"
3. Update product name if needed

### Issue: HARRISON API Not Configured

**Cause**: `HARRASON_API_URL` or `HARRASON_CREDENTIAL` not set

**Solution**:
```bash
set HARRASON_API_URL=https://your-harrison-api-url
set HARRASON_CREDENTIAL=your-credential
```

### Issue: No Harrison Orders Found

**Cause**: No orders with Harrison products exist

**Solution**:
1. Create a test order in Odoo
2. Add a product with "Harrison" or "Harrason" in the name
3. Run `find_harrison_orders.py` again

## Test Files

1. **find_harrison_orders.py** - Find orders with Harrison products
2. **test_harrison_endpoint.py** - Test endpoint with Harrison order
3. **test_harrison_webhook.py** - Test full webhook flow for Harrison
4. **HARRISON_TESTING_GUIDE.md** - This guide

## Comparison: DISC vs Harrison

| Aspect | DISC | Harrison |
|--------|------|----------|
| Keywords | `disc`, `DISC` | `harrison`, `harrason` |
| API | DISC Asia+ API | HARRISON API |
| Detection | `determine_product_type_from_odoo()` | Same function |
| Default | Defaults to DISC if unclear | Must contain Harrison keywords |

## Example Test Output

```
[OK] Found order: SO-05206
  Customer: John Doe
  Email: john@example.com
  Products: 1
    - Harrison Leadership Assessment

[OK] Product detected as: HARRISON
[OK] HARRISON API called
[OK] Email sent to john@example.com
```

## Next Steps

1. Run `find_harrison_orders.py` to find test orders
2. Test endpoint with found order
3. Test full webhook flow
4. Verify email received with Harrison link
5. Test with real payment when ready

