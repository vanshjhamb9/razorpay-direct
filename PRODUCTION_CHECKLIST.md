# Production Deployment Checklist

## Pre-Launch Checklist

### ✅ Server Deployment
- [x] Server deployed to Vercel
- [x] Server accessible at https://bodhih.vercel.app/
- [x] All endpoints tested and working
- [x] Odoo connection verified

### ⚠️ Configuration Required

#### Razorpay Setup
- [ ] Webhook URL configured: `https://bodhih.vercel.app/razorpay-webhook`
- [ ] `payment.captured` event enabled
- [ ] Webhook secret configured (recommended)
- [ ] Test webhook sent and verified

#### Vercel Environment Variables
- [ ] ODOO_URL set
- [ ] ODOO_DB set
- [ ] ODOO_USERNAME set
- [ ] ODOO_PASSWORD set
- [ ] DISC_API_URL set
- [ ] DISC_CREDENTIAL set
- [ ] HARRASON_API_URL set (if using)
- [ ] HARRASON_CREDENTIAL set (if using)
- [ ] SMTP_EMAIL set
- [ ] SMTP_PASSWORD set
- [ ] FROM_NAME set
- [ ] REPLY_TO_EMAIL set

#### Odoo Configuration
- [ ] Payment description includes order ID
- [ ] Orders have products assigned
- [ ] Customer emails are accurate
- [ ] Product names contain "disc" or "harrison" keywords

## Testing Checklist

### Endpoint Tests
- [x] `/test-odoo` endpoint works
- [x] `/razorpay-webhook` endpoint accepts POST
- [x] Odoo connection works from server
- [x] Product detection works (DISC)
- [ ] Product detection works (Harrison) - when order available

### Integration Tests
- [ ] Test payment triggers webhook
- [ ] Webhook queries Odoo successfully
- [ ] Products retrieved correctly
- [ ] Product type detected correctly
- [ ] Correct API called (DISC/Harrison)
- [ ] Email sent successfully
- [ ] Customer receives email

## Post-Launch Monitoring

### First 24 Hours
- [ ] Monitor all webhook calls
- [ ] Verify all payments processed
- [ ] Check email delivery rate
- [ ] Monitor error logs
- [ ] Verify customer satisfaction

### Weekly Checks
- [ ] Review webhook success rate
- [ ] Check failed payments
- [ ] Verify email delivery
- [ ] Review error logs
- [ ] Test with sample orders

## Rollback Plan

If issues occur:
1. **Disable Razorpay webhook** temporarily
2. **Check Vercel logs** for errors
3. **Verify environment variables** are correct
4. **Test endpoints** manually
5. **Re-enable webhook** after fixes

## Support Contacts

- **Technical Issues**: Check Vercel logs
- **Payment Issues**: Check Razorpay dashboard
- **Email Issues**: Verify SMTP settings
- **Odoo Issues**: Check Odoo connection

## Quick Commands

```bash
# Test endpoint
curl "https://bodhih.vercel.app/test-odoo?order_id=35456"

# Test webhook
python test_deployed_webhook.py 35456

# Run full test suite
python test_deployed_server.py
```








