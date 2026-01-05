# Image Upload Troubleshooting Guide

## Current Status: Still Getting 500 Errors

The code has been fixed, but you're still seeing 500 errors. Here's what to check:

## 1. **DEPLOYMENT CHECK** ⚠️ MOST LIKELY ISSUE

The changes we made are in your local files, but **the production container hasn't been rebuilt yet**.

### To Deploy the Fix:

```bash
# If using Docker locally:
docker-compose down
docker-compose build --no-cache
docker-compose up

# If deploying to a platform (Railway, Render, etc.):
# You need to trigger a new deployment with the updated code
# This usually means:
git add .
git commit -m "Fix image upload file pointer issue"
git push origin main
```

**The container must be rebuilt for the code changes to take effect!**

---

## 2. Check Application Logs

With the new logging we added, you should see detailed messages. Look for:

```
Starting image upload: <filename>
Read X bytes from uploaded file
Creating main optimized image...
Main image created successfully
Creating thumbnail...
Thumbnail created successfully
Calling super().create() to save to database/storage...
[_save] Starting upload for: <filename>
[_save] Read X bytes from content
[_save] Calling ImageKit upload_file...
```

If you see an error before "Main image created successfully", the problem is in PIL processing.
If you see an error after "Calling ImageKit upload_file...", the problem is with ImageKit API.

---

## 3. ImageKit Configuration Issues

### Check Environment Variables:

Make sure these are set in production:

```bash
IMAGEKIT_PRIVATE_KEY=private_xxx...
IMAGEKIT_PUBLIC_KEY=public_xxx...
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id_here
```

### Test ImageKit Connection:

```python
# In Django shell:
from django.conf import settings
from imagekitio import ImageKit

client = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
)

# Try a simple upload
with open('test.jpg', 'rb') as f:
    response = client.upload_file(
        file=f,
        file_name='test.jpg'
    )
    print(response)
```

---

## 4. Common Error Scenarios

### Error: "cannot identify image file"
**Cause**: File pointer issue (should be fixed now)
**Solution**: Rebuild container with new code

### Error: "ImageKit BadRequest: Invalid authentication"
**Cause**: Wrong API keys
**Solution**: Check IMAGEKIT_PRIVATE_KEY and IMAGEKIT_PUBLIC_KEY

### Error: "ImageKit BadRequest: File size too large"
**Cause**: Image exceeds ImageKit limits
**Solution**: Check ImageKit plan limits

### Error: "No module named 'imagekitio'"
**Cause**: Missing dependency
**Solution**: Check Dockerfile includes `pip install imagekitio`

### Error: "Connection timeout"
**Cause**: Network issues or ImageKit API down
**Solution**: Check network connectivity, ImageKit status

---

## 5. Run Diagnostic Script

We created a diagnostic script. Run it in production:

```bash
# SSH into your container or use your platform's shell
python manage.py shell < test_image_upload_debug.py
```

This will test each component step-by-step and show exactly where it fails.

---

## 6. Temporary Workaround: Use Local Storage

If you need to get uploads working immediately while debugging ImageKit:

In your `.env` file, temporarily comment out ImageKit credentials:

```bash
# IMAGEKIT_PRIVATE_KEY=...
# IMAGEKIT_PUBLIC_KEY=...
# IMAGEKIT_URL_ENDPOINT=...
```

This will fall back to local file storage. **Not recommended for production**, but useful for testing.

---

## 7. Check Gunicorn Logs

The 500 error should have a full stack trace in the Gunicorn logs. Look for:

```
[ERROR] Exception in ASGI application
Traceback (most recent call last):
  ...
```

This will tell you the exact line where it's failing.

---

## 8. Verify File Upload Size Limits

Check if your deployment platform has file size limits:

- **Railway**: 100MB default
- **Render**: 100MB default  
- **Heroku**: 30MB (ephemeral filesystem)
- **Nginx**: Check `client_max_body_size`

---

## Next Steps:

1. ✅ **Rebuild and redeploy** the container
2. ✅ **Check the logs** for the detailed error messages we added
3. ✅ **Run the diagnostic script** if still failing
4. ✅ **Share the full error traceback** if you need more help

The fix is in the code, but it needs to be deployed!
