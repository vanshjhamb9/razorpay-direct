# Testing with Inowix SMTP Server

## 🔄 Configuration Change

**Changed SMTP settings to test with inowix:**
- **SMTP Server:** `smtp.gmail.com` (Gmail SMTP for inowix email)
- **SMTP Port:** `587` (STARTTLS - more likely to work)
- **SMTP Email:** `info@inowix.in`
- **SMTP Password:** (needs to be set in Render environment variables)

## 📋 Next Steps

### 1. Update Render Environment Variables

Go to Render Dashboard → Your Service → Environment tab:

**Update these variables:**
- `SMTP_EMAIL` = `info@inowix.in`
- `SMTP_PASSWORD` = (your inowix Gmail app password)
- `SMTP_SERVER` = `smtp.gmail.com`
- `SMTP_PORT` = `587`
- `REPLY_TO_EMAIL` = `info@inowix.in`

**Note:** For Gmail, you'll need an **App Password**, not your regular password:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Generate App Password for "Mail"
4. Use that 16-character password

### 2. Test the Flow

After updating environment variables:
1. Make a test payment
2. Check Render logs for:
   - `EMAIL SENT -> ...` (success)
   - OR `EMAIL FAILED -> ...` (still blocked)

### 3. Expected Results

**If inowix SMTP works:**
- ✅ Confirms issue is with `mail.bodhih.com` (firewall/network)
- ✅ Can use inowix SMTP as temporary solution
- ✅ Or fix `mail.bodhih.com` firewall settings

**If inowix SMTP also fails:**
- ❌ Confirms Render free tier is blocking SMTP
- ❌ Need to upgrade Render plan OR use email API service

## 🔄 Reverting Back

After testing, to revert to bodhih SMTP:
- Update environment variables back to:
  - `SMTP_EMAIL` = `assessments@bodhih.com`
  - `SMTP_SERVER` = `mail.bodhih.com`
  - `SMTP_PORT` = `465` or `587`
  - `REPLY_TO_EMAIL` = `support@bodhih.com`

---

**Code updated and ready to test!** 🚀
