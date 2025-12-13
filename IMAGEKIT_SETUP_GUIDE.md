# ImageKit Product Image Upload Testing - Complete Setup

## What Has Been Created

We've created a comprehensive testing framework to verify that product images are uploaded to ImageKit accurately according to the [ImageKit API reference](https://imagekit.io/docs/api-reference/upload-file/).

### Files Created

1. **Test Suite** (`nxtbn/product/tests/test_imagekit_upload.py`)
   - 9 comprehensive test cases
   - Tests basic uploads, product image creation, batch operations
   - Validates URL generation, metadata, and variants
   - Uses Django TestCase framework

2. **Management Command** (`nxtbn/core/management/commands/test_imagekit_uploads.py`)
   - 7 quick integration tests
   - CLI tool for interactive testing
   - Detailed verbose output
   - Quick pass/fail summary

3. **Verification Script** (`verify_imagekit.py`)
   - Standalone Python script
   - Checks configuration and integration
   - Validates storage backend setup
   - Tests upload capability

4. **Documentation**
   - `IMAGEKIT_TESTING_GUIDE.md` - Comprehensive guide with all details
   - `IMAGEKIT_QUICK_REFERENCE.md` - Quick command reference
   - This file - Setup and overview

---

## Quick Start (30 seconds)

### 1. Run the Management Command
```bash
python manage.py test_imagekit_uploads --verbose
```

### 2. Expected Output
```
======================================================================
ImageKit Upload Integration Tests
======================================================================

✅ ImageKit Configuration Found

[Test 1] Basic File Upload
--------------------------------------------------
  ✅ File uploaded successfully
  ✅ File deleted successfully

[Test 2] Image File Upload
--------------------------------------------------
  ✅ Image uploaded successfully

...

✅ All tests passed! (7/7)
======================================================================
```

---

## What Gets Tested

### Management Command (7 Tests)
| # | Test | Validates |
|---|------|-----------|
| 1 | Basic File Upload | Text file upload, URL generation, deletion |
| 2 | Image File Upload | JPEG image upload to ImageKit |
| 3 | Multiple File Uploads | Batch upload of 3 images |
| 4 | URL Generation | CDN URL format and accessibility |
| 5 | File Metadata | File information retrieval |
| 6 | Delete Operation | File deletion by ID |
| 7 | Large Image Upload | 1920x1080 image handling |

### Test Suite (9 Tests)
| # | Test | Validates |
|---|------|-----------|
| 1 | Basic Image Upload | ImageKit upload functionality |
| 2 | Product Image Creation | Django ORM integration |
| 3 | Multiple Images | Batch image uploads |
| 4 | Product with Images | Product-image relationships |
| 5 | Image Variants | XS/thumbnail variant handling |
| 6 | URL Format | CDN URL compliance |
| 7 | Upload Options | Folder paths and options |
| 8 | Response Metadata | Upload response structure |
| 9 | Dimension Preservation | Image dimension preservation |

---

## Test Execution Methods

### Method 1: Management Command (Recommended for Quick Testing)
```bash
# Quick run
python manage.py test_imagekit_uploads

# Detailed output
python manage.py test_imagekit_uploads --verbose
```

### Method 2: Test Suite (Recommended for CI/CD)
```bash
# All tests
python manage.py test nxtbn.product.tests.test_imagekit_upload

# Specific test class
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase

# Specific test method
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_basic_image_upload_to_imagekit

# With verbose output
python manage.py test nxtbn.product.tests.test_imagekit_upload --verbosity=2
```

### Method 3: Verification Script (For Setup Checks)
```bash
python verify_imagekit.py
```

---

## Prerequisites

### 1. Environment Variables
Create `.env` file with:
```env
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint/
```

### 2. ImageKit Account
- Get keys from: https://imagekit.io/dashboard
- Create an ImageKit account if needed
- Copy your URL endpoint

### 3. Dependencies
All dependencies already installed in `requirements.txt`:
```
imagekitio==3.2.1
Pillow>=9.0.0
Django>=4.2
```

---

## ImageKit API Coverage

Our tests validate all the key ImageKit API endpoints according to their [official documentation](https://imagekit.io/docs/api-reference/):

### ✅ Upload File Endpoint
- **API**: `POST /api/v1/files/upload`
- **Tests**: 
  - Basic text file upload
  - Image file upload (JPEG, PNG)
  - Multiple file uploads
  - Large file uploads
- **Validates**:
  - File is stored in ImageKit
  - Response contains metadata (file_id, url, file_name)
  - URL is accessible via CDN

### ✅ Delete File Endpoint
- **API**: `DELETE /api/v1/files/{fileId}`
- **Tests**: File deletion by ID
- **Validates**: File is removed from ImageKit

### ✅ URL Construction
- **Tests**: CDN URL generation and format
- **Validates**: 
  - URL format compliance
  - Endpoint is included
  - URLs are HTTP/HTTPS
  - URLs are accessible

---

## File Locations

```
nxtbn/
├── core/
│   ├── management/
│   │   └── commands/
│   │       └── test_imagekit_uploads.py      ← Management command
│   ├── imagekit_storage.py                    ← Storage backend
│   └── storage_backends.py                    ← Alternative backend
├── product/
│   ├── tests/
│   │   └── test_imagekit_upload.py           ← Test suite
│   └── models.py                              ← Product model
├── filemanager/
│   └── models.py                              ← Image model
├── verify_imagekit.py                         ← Verification script
├── IMAGEKIT_TESTING_GUIDE.md                 ← Full documentation
├── IMAGEKIT_QUICK_REFERENCE.md               ← Quick reference
└── settings.py                                ← Configuration
```

---

## Integration Points

### Storage Backend
- **File**: `nxtbn/core/imagekit_storage.py`
- **Class**: `ImageKitStorage`
- **Purpose**: Django storage backend for ImageKit
- **Methods**: `_save()`, `delete()`, `url()`, `exists()`

### Image Model
- **File**: `nxtbn/filemanager/models.py`
- **Class**: `Image`
- **Fields**: 
  - `image` → Uploaded to ImageKit
  - `image_xs` → Thumbnail variant
- **Methods**: `get_image_url()`, `get_image_xs_url()`

### Product Model
- **File**: `nxtbn/product/models.py`
- **Class**: `Product`
- **Relationship**: ManyToMany with Image
- **Methods**: `product_thumbnail()`, `product_thumbnail_xs()`

---

## Expected Results

### Successful Test Output
```
✅ All tests passed! (7/7)
✅ All 9 test cases pass individually
✅ Images appear in ImageKit dashboard
✅ CDN URLs are accessible
```

### What It Proves
- ✅ Images are uploaded to ImageKit
- ✅ URLs are generated correctly
- ✅ Product-image relationships work
- ✅ Batch operations function properly
- ✅ File deletion works
- ✅ Implementation matches ImageKit API spec

---

## Troubleshooting

### Issue: "ImageKit is not properly configured"
**Solution**: 
```bash
# Check .env file has all three keys
cat .env | grep IMAGEKIT

# Or set variables directly
export IMAGEKIT_PRIVATE_KEY=your_key
export IMAGEKIT_PUBLIC_KEY=your_key
export IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint/
```

### Issue: "Connection refused" or timeout
**Solution**:
- Check internet connection
- Verify ImageKit API is online: https://imagekit.io/
- Check credentials in ImageKit dashboard

### Issue: Tests pass but URLs don't work
**Solution**:
- Verify endpoint is correct
- Check ImageKit CDN is enabled
- Verify files appear in ImageKit dashboard
- Check authentication is correct

### Issue: "Module not found" errors
**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or specifically
pip install imagekitio Pillow
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: ImageKit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python manage.py test nxtbn.product.tests.test_imagekit_upload
        env:
          IMAGEKIT_PRIVATE_KEY: ${{ secrets.IMAGEKIT_PRIVATE_KEY }}
          IMAGEKIT_PUBLIC_KEY: ${{ secrets.IMAGEKIT_PUBLIC_KEY }}
          IMAGEKIT_URL_ENDPOINT: ${{ secrets.IMAGEKIT_URL_ENDPOINT }}
```

### GitLab CI Example
```yaml
test:imagekit:
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
  script:
    - python manage.py test nxtbn.product.tests.test_imagekit_upload
  variables:
    IMAGEKIT_PRIVATE_KEY: $IMAGEKIT_PRIVATE_KEY
    IMAGEKIT_PUBLIC_KEY: $IMAGEKIT_PUBLIC_KEY
    IMAGEKIT_URL_ENDPOINT: $IMAGEKIT_URL_ENDPOINT
```

---

## Manual Verification Checklist

- [ ] ImageKit account created
- [ ] API keys copied to `.env`
- [ ] Environment variables loaded
- [ ] `python manage.py test_imagekit_uploads --verbose` runs successfully
- [ ] All 7 tests pass
- [ ] `python manage.py test nxtbn.product.tests.test_imagekit_upload` runs successfully
- [ ] All 9 tests pass
- [ ] Images visible in ImageKit dashboard
- [ ] CDN URLs are accessible
- [ ] Product images are uploading to ImageKit

---

## Next Steps

### 1. Run Tests Today
```bash
python manage.py test_imagekit_uploads --verbose
```

### 2. Verify Dashboard
- Log into ImageKit dashboard
- Navigate to Media Library
- Confirm test images are there

### 3. Integrate Tests
- Add to CI/CD pipeline
- Run on every push
- Monitor for failures

### 4. Monitor Production
- Log image upload operations
- Track ImageKit API performance
- Monitor CDN availability

---

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `IMAGEKIT_TESTING_GUIDE.md` | Detailed guide with all test information |
| `IMAGEKIT_QUICK_REFERENCE.md` | Quick command reference and troubleshooting |
| This file | Setup overview and integration guide |

---

## Support Resources

- **ImageKit Documentation**: https://imagekit.io/docs/
- **ImageKit API Reference**: https://imagekit.io/docs/api-reference/
- **ImageKit Python SDK**: https://github.com/imagekit-developer/imagekit-python
- **Django File Storage**: https://docs.djangoproject.com/en/4.2/topics/files/storage/

---

## Summary

You now have a complete testing framework to validate ImageKit image uploads:

✅ **Management Command** - 7 quick tests for validation
✅ **Test Suite** - 9 comprehensive tests for CI/CD  
✅ **Verification Script** - Setup validation tool
✅ **Documentation** - Complete guides and references

Run `python manage.py test_imagekit_uploads --verbose` to get started!

---

**Last Updated**: December 13, 2025
**Version**: 1.0
**Status**: Ready for use
