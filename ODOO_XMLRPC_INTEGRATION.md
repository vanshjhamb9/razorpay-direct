# Odoo XML-RPC Integration Guide

## Overview
This middleware now connects to your Odoo database using XML-RPC to automatically detect which products were sold when a payment is received, and routes them to the appropriate assessment API (DISC or Harrison).

## How It Works

### Flow Diagram
```
1. Razorpay Payment Captured
   ↓
2. Webhook Receives Payment Event
   ↓
3. Extract Order Identifier (from description or notes)
   ↓
4. Query Odoo Database via XML-RPC
   - Connect to: https://bodhih.odoo.com/xmlrpc/2/object
   - Search for sale.order by ID or name
   - Get sale.order.line items (products sold)
   ↓
5. Analyze Product Names
   - Check if product contains "disc" → Use DISC Asia+ API
   - Check if product contains "harrison/harrason" → Use Harrison API
   ↓
6. Create Account on Appropriate API
   ↓
7. Send Email to Customer with Account Details
```

## Configuration

### Environment Variables Required

Add these to your environment (Replit Secrets or `.env` file):

```bash
# Odoo XML-RPC Configuration
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=2
ODOO_PASSWORD=-KsZAxbX2!Fn36g

# Existing API configurations
DISC_API_URL=https://discapi.discasiaplus.org/api/DISC/Respondent_and_Report_Details_Bodhih
DISC_CREDENTIAL=vezHgzd1EueI3clvF/1kNnMyCITD9UwC
HARRASON_API_URL=<your_harrison_api_url>
HARRASON_CREDENTIAL=<your_harrison_credential>
```

## How Order Identification Works

The system tries multiple methods to identify the Odoo sale order:

1. **From Description**: Extracts sale order name pattern (e.g., "SO-05200-5")
2. **From Notes**: Looks for `sale_order_id`, `order_id`, or `odoo_order_id` fields
3. **Direct ID**: If description is a numeric ID, uses it directly

## Product Type Detection

The system automatically detects product type from Odoo product names:

- **DISC Products**: Contains keywords like "disc", "DISC", "diSC"
- **Harrison Products**: Contains keywords like "harrison", "harrason", "harison"
- **Default**: If unclear, defaults to DISC

## Example Odoo Query

When payment is received, the system queries Odoo like this:

```python
# Search for sale order
sale_order_ids = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'sale.order', 'search',
    [[('id', '=', order_id)]],
    {'limit': 1}
)

# Get order lines (products)
order_lines = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'sale.order.line', 'search_read',
    [[('order_id', '=', sale_order_id)]],
    {
        'fields': ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal', 'name'],
        'limit': 100
    }
)
```

## Features

✅ **Automatic Product Detection**: Queries Odoo database to get exact products sold
✅ **Smart Routing**: Automatically routes to DISC or Harrison API based on product name
✅ **Multiple Products Support**: Handles orders with multiple products
✅ **Fallback Logic**: Falls back to Razorpay/notes if Odoo query fails
✅ **Comprehensive Logging**: Logs all Odoo queries and product detection

## Testing

To test the integration:

1. Make a payment through your Odoo website
2. Check the webhook logs to see:
   - Odoo connection status
   - Products retrieved from database
   - Product type detection
   - API routing decision

## Troubleshooting

### Odoo Authentication Fails
- Verify `ODOO_USERNAME` and `ODOO_PASSWORD` are correct
- Check that the user has access to `sale.order` and `sale.order.line` models

### Order Not Found
- Ensure the order identifier is passed correctly in Razorpay description or notes
- Check that the sale order exists in Odoo database

### Products Not Detected
- Verify product names in Odoo contain "disc" or "harrison" keywords
- Check logs for product name extraction details

## Security Notes

⚠️ **Important**: 
- Never commit Odoo credentials to version control
- Use environment variables for all sensitive data
- The Odoo password is stored in environment variables, not in code

