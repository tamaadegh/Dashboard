# Docker Build Guide - Cloudinary & Dependencies

## Problem Fixed
Docker was caching old layers and not installing new dependencies (cloudinary, django-cloudinary-storage) even after updating `requirements.txt`.

## Solution Applied

### 1. **Fixed requirements.txt**
- Removed duplicate cloudinary entries
- Now properly includes: `cloudinary` and `django-cloudinary-storage`

### 2. **Updated Dockerfile**
- Changed from `requirements-simple.txt` → `requirements.txt`
- Added `COPY ./requirements.txt` BEFORE pip install (for cache invalidation)
- Added `--upgrade` flag to pip install
- Added `ARG CACHEBUST` for manual cache busting

### 3. **Docker Layer Caching Strategy**
```dockerfile
# Files copied EARLY in Dockerfile (before RUN commands)
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
COPY ./requirements.txt /tmp/requirements.txt  # ← This invalidates cache when changed!
```

When `requirements.txt` changes, Docker rebuilds from this point forward.

## How to Build

### Standard Build (Uses Cache)
```bash
docker build -t nxtbn/nxtbn:latest .
```

### Force Rebuild (Bust Cache)
```bash
# Windows PowerShell
docker build --build-arg CACHEBUST=$(Get-Date -UFormat %s) -t nxtbn/nxtbn:latest .

# Linux/Mac
docker build --build-arg CACHEBUST=$(date +%s) -t nxtbn/nxtbn:latest .
```

### Complete Rebuild (No Cache at All)
```bash
docker build --no-cache -t nxtbn/nxtbn:latest .
```

## Verify Cloudinary Installation

After building, verify cloudinary is installed:
```bash
docker run --rm nxtbn/nxtbn:latest pip list | grep cloudinary
```

Expected output:
```
cloudinary                 1.x.x
django-cloudinary-storage  0.x.x
```

## Deployment to Railway/Production

1. **Commit changes:**
```bash
git add Dockerfile requirements.txt
git commit -m "fix: Update Dockerfile to install cloudinary dependencies"
git push
```

2. **Railway will auto-rebuild** with new dependencies

3. **Verify in Railway logs:**
Look for:
```
Successfully installed cloudinary-x.x.x django-cloudinary-storage-x.x.x
```

## Troubleshooting

### If cloudinary still not installed:
1. Check Railway build logs for pip install errors
2. Try manual rebuild in Railway dashboard
3. Verify `requirements.txt` is committed to git
4. Check Railway environment variables include Cloudinary credentials

### If images still not working:
1. Verify `.env` has Cloudinary credentials
2. Check `settings.py` has `IS_CLOUDINARY = True`
3. Test with: `python manage.py shell`
   ```python
   from django.conf import settings
   print(settings.IS_CLOUDINARY)  # Should be True
   ```

## Files Modified
- ✅ `Dockerfile` - Now installs from requirements.txt with cache busting
- ✅ `requirements.txt` - Removed duplicates, includes cloudinary
- ✅ `.dockerignore` - Already optimized (no changes needed)

## Next Steps
1. Push changes to git
2. Railway will auto-deploy
3. Test image uploads in production
4. Images should now use Cloudinary URLs
