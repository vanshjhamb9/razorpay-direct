# Fix Odoo Authentication Issue

## Problem
Authentication is failing because Odoo XML-RPC requires an **email address** as the username, not a user ID.

## Solution

### Step 1: Find Your Odoo Login Email

1. Go to https://bodhih.odoo.com
2. Log in to your Odoo account
3. Note the **email address** you use to log in (not the user ID)

### Step 2: Test Authentication

Run this command with your email:

```bash
python test_with_email.py your-email@bodhih.com
```

Or run it interactively:
```bash
python test_with_email.py
# Then enter your email when prompted
```

### Step 3: Update Environment Variables

Once authentication succeeds, update your environment variables:

**Option A: Set in your system/environment:**
```bash
set ODOO_USERNAME=your-email@bodhih.com
```

**Option B: Create a `.env` file:**
```env
ODOO_URL=https://bodhih.odoo.com
ODOO_DB=bodhih
ODOO_USERNAME=your-email@bodhih.com
ODOO_PASSWORD=-KsZAxbX2!Fn36g
```

**Option C: Update in Replit Secrets:**
- Go to Replit Secrets tab
- Add/Update: `ODOO_USERNAME` = `your-email@bodhih.com`

### Step 4: Verify It Works

```bash
python quick_test.py
```

You should see:
```
[OK] Connected to Odoo
[OK] Found X recent order(s)
```

## Alternative: Using API Key (If Available)

If your Odoo setup supports API keys:

1. In Odoo, go to **Settings** → **Users & Companies** → **Users**
2. Click on your user
3. Go to **Preferences** → **Account Security**
4. Generate an **API Key**
5. Use the API key as the password instead

## Common Issues

### "Authentication failed" even with correct email
- Verify the password is correct
- Check if the user has XML-RPC access enabled in Odoo
- Ensure the user has access to `sale.order` and `sale.order.line` models

### "User doesn't have XML-RPC access"
- Contact your Odoo administrator to enable XML-RPC access for your user
- Or use a different user account that has XML-RPC access

## Need Help?

If you're not sure what email to use:
1. Check your Odoo login page - it usually shows the email format
2. Try common patterns:
   - `admin@bodhih.com`
   - `yourname@bodhih.com`
   - The email you use to receive Odoo notifications

