# 🔧 How to Fix ImageKit in Production

## The Issue

Your `.env` file is **gitignored** (correctly), so it doesn't get deployed to production. You need to set environment variables directly in your deployment platform.

## ✅ Solution: Set Environment Variables in Your Platform

### For Railway:

1. Go to your project dashboard: https://railway.app
2. Click on your backend service
3. Click on **"Variables"** tab
4. Add these variables:

```
IMAGEKIT_PRIVATE_KEY=private_EgDPXpuuDRIBRwGT1zEPHYhs+J8=
IMAGEKIT_PUBLIC_KEY=public_eXz8fVEsqLlyySBBsb8X4jazIX4=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/tamaade
```

5. **Redeploy** your service

### For Render:

1. Go to your dashboard
2. Select your service
3. Go to **"Environment"** tab
4. Add the variables above
5. Save and redeploy

### For any other platform:

Look for:
- "Environment Variables"
- "Config Vars"
- "Settings" → "Variables"

---

## ✅ Verify After Setting

After setting the variables and redeploying, the startup diagnostic will show:

```
Verifying image upload system...
================================================================================
1. Checking Django Configuration...
✓ IMAGEKIT_PRIVATE_KEY: ***SET***
✓ IMAGEKIT_PUBLIC_KEY: ***SET***
✓ IMAGEKIT_URL_ENDPOINT: https://ik.imagekit.io/tamaade
✓ IS_IMAGEKIT: True

2. Checking Storage Backend...
✓ Using ImageKit storage
✓ ImageKit client initialized
================================================================================
```

---

## 🔍 Check Current Status

Run this command to see if variables are set:

**Locally (will work):**
```bash
python manage.py check_imagekit
```

**In Production (after deploy):**
```bash
# Check the deployment logs for the diagnostic output
```

---

## ⚠️ Important Notes

1. **Never commit `.env` to git** - It contains secrets
2. **Set env vars in platform** - Not in code
3. **Redeploy after setting** - Changes need a new deployment
4. **Check startup logs** - The diagnostic runs automatically now

---

## 📋 Your ImageKit Credentials

From your `.env` file (copy these to your platform):

```bash
IMAGEKIT_PRIVATE_KEY=private_EgDPXpuuDRIBRwGT1zEPHYhs+J8=
IMAGEKIT_PUBLIC_KEY=public_eXz8fVEsqLlyySBBsb8X4jazIX4=
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/tamaade
```

Make sure to copy them **exactly** as shown (including the + and = symbols in the keys).

---

## ✅ After Fixing

1. Set variables in platform ✓
2. Redeploy ✓
3. Check startup logs ✓
4. Try uploading an image ✓

Your image uploads will work! 🎉
