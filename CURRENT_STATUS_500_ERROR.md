# 🚨 Debugging Status: ImageKit Uploads

## Current Situation
1. **Diagnostic Script Works** ✅
   - Test images are uploading successfully to ImageKit.
   - This confirms credentials and connectivity are GOOD.
   - This confirms the `imagekitio` package is working for the script.

2. **Dashboard Upload Fails** ❌
   - User gets 500 error when uploading via Web UI.
   - Request ID: `GmSkx6DdTheglxPQ5nX1uw`

## Why the Discrepancy?
This is likely a **Caching** or **Process Hygiene** issue where the web server (Gunicorn) is either:
- Running an old version of the code (pre-fix).
- Using a cached/broken instance of the storage backend.
- Handling the request data differently than the diagnostic script.

## 🛠️ The Fix Attempt (Applied)

### 1. Exposed Real Error
I modified `nxtbn/filemanager/api/dashboard/views.py` to catch the 500 error and return it as a **400 Bad Request** with the full error details.
**Benefit**: You will see the EXACT error message in your browser (Network Tab) instead of a generic "Server Error".

### 2. Pinned Stable Version
I pinned `imagekitio==3.2.0` in `requirements.txt` to ensure stability.

### 3. Added Resilient Fallbacks
Updated `imagekit_storage.py` to handle mismatched API parameter names (`public_key` vs `publicKey`).

## 👉 ACTION REQUIRED

1. **Deploy These Changes**
   ```bash
   git add .
   git commit -m "Add debug view for uploads and pin imagekitio"
   git push origin main
   ```

2. **Wait for Deployment to Finish** (Ensure Build Cache is cleared if possible).

3. **Try Uploading Again**
   - Go to Dashboard.
   - Try to upload an image.
   - **If it fails**: Open Developer Tools (F12) -> Network -> Click the red `images/` request -> **Response** tab.
   - **Copy the JSON error message** and share it (or paste it here).

4. **(Optional) Run Version Check**
   If you have console access in production:
   ```bash
   python nxtbn/check_imagekit_version.py
   ```
