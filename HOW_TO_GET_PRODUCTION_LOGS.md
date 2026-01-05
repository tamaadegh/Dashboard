# 🔍 How to Get Production Logs & Debug 500 Errors

## The Issue

You're getting 500 errors when uploading images. We need to see the actual error message from the logs to diagnose the problem.

---

## Step 1: Check Startup Logs

When your container starts, the diagnostic runs automatically. Look for this section in your deployment logs:

```
Verifying image upload system...
================================================================================
PRODUCTION IMAGE UPLOAD DIAGNOSTIC
================================================================================
```

### ✅ What "Success" Looks Like:

```
1. Checking Django Configuration...
✓ IMAGEKIT_PRIVATE_KEY: ***SET***
✓ IMAGEKIT_PUBLIC_KEY: ***SET***
✓ IMAGEKIT_URL_ENDPOINT: https://ik.imagekit.io/tamaade

2. Checking Storage Backend...
✓ Using ImageKit storage
✓ ImageKit client initialized

3. Testing Image Optimization...
✓ Image optimization works correctly

4. Testing Storage Upload...
✓ Storage upload works correctly

5. Testing Full Serializer Flow...
✓ Full serializer flow works correctly
```

### ❌ If You See Errors:

Look for lines with ✗ - they'll tell you what's wrong.

---

## Step 2: Get Application Error Logs

When the 500 error occurs (after trying to upload), check the logs immediately.

### For Railway:

1. Go to your project: https://railway.app
2. Click on your backend service
3. Click on **"Deployments"**
4. Click on the latest deployment
5. Look at the **logs** - scroll to the time of the error (22:50:52 UTC)

### For Render:

1. Go to your dashboard
2. Select your service
3. Click on **"Logs"** tab
4. Look for errors around the upload time

### What to Look For:

The logs should show detailed information like:

```
[INFO] Starting image upload: filename.jpg
[INFO] Read X bytes from uploaded file
[INFO] Creating main optimized image...
[ERROR] Image processing failed: SomeError: actual error message here

OR

[INFO] Main image created successfully
[INFO] Creating thumbnail...
[ERROR] Thumbnail creation failed: actual error

OR

[INFO] Thumbnail created successfully
[INFO] Calling super().create() to save to database/storage...
[ERROR] ImageKit upload failed: actual error
```

---

## Step 3: Common Errors & Solutions

### Error: "ImageKit BadRequest: Invalid authentication"
**Cause**: API keys are incorrect or not properly set  
**Fix**: 
- Verify keys in platform match your `.env` exactly
- Check for extra spaces or missing characters
- Make sure you copied the full keys including `+` and `=` symbols

### Error: "ImageKit BadRequest: File size too large"
**Cause**: Image exceeds ImageKit plan limits  
**Fix**: Check your ImageKit dashboard for upload limits

### Error: "cannot identify image file"
**Cause**: File corruption or incorrect format  
**Fix**: Should be fixed by our code changes

### Error: "Connection timeout" or "Network error"
**Cause**: Can't reach ImageKit API  
**Fix**: 
- Check if ImageKit service is up: https://status.imagekit.io/
- Verify your production server can reach external APIs

### Error: "WORKER TIMEOUT"
**Cause**: Process took longer than 120 seconds  
**Fix**: Should be fixed (we increased timeout to 120s)

---

## Step 4: Copy Logs Here

Once you find the error in the logs, copy **the full error traceback** and share it. It will look something like:

```
Traceback (most recent call last):
  File "/path/to/file.py", line XX, in function_name
    code here
  ...
SomeException: The actual error message
```

---

## Quick Commands

### Check ImageKit credentials in production:
```bash
# SSH into your container or use platform shell
python manage.py check_imagekit
```

### Run full diagnostic manually:
```bash
python manage.py diagnose_upload
```

---

## What I Need

To help you fix the 500 error, please share:

1. ✅ **Startup logs** - Did the diagnostic pass on startup?
2. ✅ **Error logs** - What error appears when you try to upload?
3. ✅ **Full traceback** - The complete error trace from the logs

With this information, I can tell you exactly what's wrong and how to fix it!

---

## Railway Specific: How to Get Logs

### Using Railway CLI:
```bash
railway logs
```

### Using Web Interface:
1. Project → Service → Deployments
2. Click latest deployment
3. Logs tab shows real-time output
4. Use filter to find errors: type "error" or "traceback"

### Get logs around specific time:
The error occurred at: **2026-01-05T22:50:52.723361431Z**

Look for logs from **22:50:50 to 22:50:55** UTC

---

## What the Logs Will Reveal

The detailed logging we added will show:
- ✅ Which step succeeded
- ❌ Which step failed
- 📝 The exact error message
- 🔍 Full traceback for debugging

This will tell us if it's:
- Environment variable issue
- ImageKit API issue  
- Network/connectivity issue
- Code bug
- File size/format issue
