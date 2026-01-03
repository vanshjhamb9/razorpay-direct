# Deployed Server Testing Guide

Server deployed at: **https://bodhih.vercel.app/**

## Quick Tests

### 1. Test Odoo Endpoint

```bash
# Test with order ID
curl "https://bodhih.vercel.app/test-odoo?order_id=35456"

# Or using Python
python test_deployed_server.py 35456
```

### 2. Test Webhook Endpoint

```bash
python test_deployed_webhook.py 35456
```

### 3. Run All Tests

```bash
python test_deployed_server.py
```

## Test Endpoints

### Root Endpoint
- **URL**: `https://bodhih.vercel.app/`
- **Method**: GET
- **Expected**: 200 OK

### Odoo Test Endpoint
- **URL**: `https://bodhih.vercel.app/test-odoo?order_id=35456`
- **Method**: GET
- **Expected**: JSON with products and detected types

### Webhook Endpoint
- **URL**: `https://bodhih.vercel.app/razorpay-webhook`
- **Method**: POST
- **Expected**: 200 OK (processes payment.captured events)

## Razorpay Configuration

Update Razorpay webhook settings:

1. **Webhook URL**: `https://bodhih.vercel.app/razorpay-webhook`
2. **Events**: Enable `payment.captured`
3. **Secret**: Configure if using signature verification

## Testing Checklist

- [ ] Server is accessible
- [ ] Root endpoint responds
- [ ] Odoo endpoint works with order IDs
- [ ] Odoo connection works from server
- [ ] Product detection works (DISC/Harrison)
- [ ] Webhook endpoint accepts POST requests
- [ ] Webhook processes payment.captured events
- [ ] Webhook ignores other events
- [ ] Odoo query executes correctly
- [ ] API routing works (DISC vs Harrison)

## Expected Behavior

### Odoo Endpoint Test
```json
{
  "success": true,
  "sale_order_id": 35456,
  "products": [
    {
      "product_name": "Test - DISC Asia+ Basic Report",
      "detected_type": "DISC"
    }
  ],
  "message": "Successfully retrieved 1 product(s) from Odoo"
}
```

### Webhook Test
- Status: 200 OK
- Response: "OK"
- Server logs show:
  - Odoo query executed
  - Products retrieved
  - Product type detected
  - API called
  - Email sent (if configured)

## Troubleshooting

### Server Not Accessible
- Check Vercel deployment status
- Verify domain is correct
- Check server logs in Vercel dashboard

### Odoo Connection Fails
- Verify environment variables are set in Vercel
- Check ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
- Verify Odoo server allows connections from Vercel

### Webhook Not Processing
- Check Razorpay webhook URL is correct
- Verify `payment.captured` event is enabled
- Check server logs for webhook calls
- Verify payment description contains order ID

## Environment Variables Required

Ensure these are set in Vercel:

```bash
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=siddharthan@bodhih.com
ODOO_PASSWORD=-KsZAxbX2!Fn36g

DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC

HARRASON_API_URL=<your_harrison_url>
HARRASON_CREDENTIAL=<your_harrison_credential>

SMTP_EMAIL=info@inowix.in
SMTP_PASSWORD=jxrmhihcvqlqojqa
```

## Test Files

1. **test_deployed_server.py** - Comprehensive test suite
2. **test_deployed_webhook.py** - Webhook testing
3. **DEPLOYED_SERVER_TESTING.md** - This guide

## Next Steps

1. Run comprehensive tests: `python test_deployed_server.py`
2. Test with real order: `python test_deployed_webhook.py 35456`
3. Update Razorpay webhook URL
4. Test with real payment
5. Monitor server logs for issues








