# ImageKit Upload Testing Guide

This guide explains how to test if product images are uploaded to ImageKit accurately according to the [ImageKit API reference](https://imagekit.io/docs/api-reference/upload-file/).

## Overview

We've created two testing approaches:

1. **Management Command** - Quick interactive testing from the command line
2. **Test Suite** - Comprehensive automated tests with detailed validation

---

## Quick Start: Management Command

### Run All Tests

```bash
python manage.py test_imagekit_uploads
```

### Run with Verbose Output

```bash
python manage.py test_imagekit_uploads --verbose
```

### Example Output

```
======================================================================
ImageKit Upload Integration Tests
======================================================================

✅ ImageKit Configuration Found

Configuration Summary:
  • Endpoint: https://ik.imagekit.io/your-endpoint/
  • Private Key: ***xxxx
  • Public Key: ***xxxx

[Test 1] Basic File Upload
--------------------------------------------------
  ✅ File uploaded successfully
  ✅ File deleted successfully

[Test 2] Image File Upload
--------------------------------------------------
  ✅ Image uploaded successfully

[Test 3] Multiple File Uploads
--------------------------------------------------
  ✅ All 3 images uploaded successfully

[Test 4] URL Generation
--------------------------------------------------
  ✅ URL generated successfully
  ✅ URL contains ImageKit endpoint

[Test 5] File Metadata
--------------------------------------------------
  ✅ File saved with metadata

[Test 6] Delete Operation
--------------------------------------------------
  ✅ File deleted successfully

[Test 7] Large Image Upload
--------------------------------------------------
  ✅ Large image uploaded successfully

======================================================================
Test Summary
======================================================================
Basic File Upload                  ✅ PASS
Image File Upload                  ✅ PASS
Multiple File Uploads              ✅ PASS
URL Generation                     ✅ PASS
File Metadata                      ✅ PASS
Delete Operation                   ✅ PASS
Large Image Upload                 ✅ PASS
------================================================================
✅ All tests passed! (7/7)
======================================================================
```

---

## Detailed Test Suite

### Run Full Test Suite

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload --verbosity=2
```

### Run Specific Test Class

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase --verbosity=2
```

### Run Specific Test Method

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_image_creation_with_imagekit --verbosity=2
```

### Test Coverage

The test suite (`test_imagekit_upload.py`) includes:

#### Test 1: Basic Image Upload to ImageKit
- **What it tests**: Basic ImageKit upload functionality
- **Validates**: File is uploaded, path is returned, URL is accessible
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_basic_image_upload_to_imagekit`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_basic_image_upload_to_imagekit
```

#### Test 2: Product Image Creation via Django ORM
- **What it tests**: Creating Image objects through Django models
- **Validates**: ImageField properly uploads to ImageKit, URL generation works
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_product_image_creation_with_imagekit`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_image_creation_with_imagekit
```

#### Test 3: Multiple Images Upload
- **What it tests**: Batch upload of multiple images
- **Validates**: All images upload correctly, URLs are distinct and valid
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_multiple_images_upload`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_multiple_images_upload
```

#### Test 4: Product with Multiple Images
- **What it tests**: Full product creation with multiple ImageKit images
- **Validates**: Product-image relationships, URL generation for each image
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_product_with_multiple_images`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_with_multiple_images
```

#### Test 5: Image Variants (XS/Thumbnail)
- **What it tests**: Handling image XS (extra small) variants
- **Validates**: Both main and thumbnail URLs are generated correctly
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_image_with_small_variant`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_image_with_small_variant
```

#### Test 6: ImageKit URL Format
- **What it tests**: Generated URLs comply with ImageKit CDN format
- **Validates**: URLs start with http, contain endpoint, are properly formatted
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_imagekit_url_format`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_imagekit_url_format
```

#### Test 7: Upload with ImageKit Options
- **What it tests**: Upload options support (folder paths, unique filenames)
- **Validates**: Options are properly passed to ImageKit API
- **File**: `test_imagekit_upload.py:ImageKitUploadTestCase.test_upload_with_imagekit_options`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_upload_with_imagekit_options
```

#### Test 8: Upload Response Metadata
- **What it tests**: Upload response contains ImageKit metadata (file_id, url, etc.)
- **Validates**: Response structure matches ImageKit API spec
- **File**: `test_imagekit_upload.py:ImageKitUploadValidationTestCase.test_upload_response_metadata`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadValidationTestCase.test_upload_response_metadata
```

#### Test 9: Image Dimensions Preserved
- **What it tests**: Image dimensions are preserved through upload
- **Validates**: Uploaded images maintain original dimensions
- **File**: `test_imagekit_upload.py:ImageKitUploadValidationTestCase.test_image_dimensions_preserved`

```python
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadValidationTestCase.test_image_dimensions_preserved
```

---

## What These Tests Validate

### According to ImageKit API Reference

✅ **File Upload** (`POST /api/v1/files/upload`)
- Accepts file in multipart request
- Returns file metadata (file_id, url, file_name, etc.)
- Supports options like `folder`, `use_unique_file_name`, `tags`
- Supports various image formats (JPEG, PNG, WebP, etc.)

✅ **URL Generation**
- Generates valid CDN URLs for uploaded files
- URLs are accessible via ImageKit endpoint
- URLs support transformation parameters

✅ **File Operations**
- Delete files by file_id
- Check file existence
- Retrieve file metadata

### Product-Specific Validation

✅ **Image Model Integration**
- Images upload to ImageKit storage backend
- ImageField stores file path/reference correctly
- Image URL methods work with ImageKit paths
- Thumbnail variants (image_xs) are handled properly

✅ **Product Relationships**
- Products can have multiple ImageKit-hosted images
- Image relationships are maintained correctly
- Batch operations on product images work

---

## Troubleshooting

### Test Fails: "ImageKit is not properly configured"

**Solution:** Set environment variables in `.env`:
```env
IMAGEKIT_PRIVATE_KEY=your_private_key_here
IMAGEKIT_PUBLIC_KEY=your_public_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint/
```

### Test Fails: "Connection refused" or timeout

**Solution:** 
- Verify ImageKit credentials are correct
- Check your internet connection
- ImageKit API might be temporarily unavailable

### Test Passes but URLs don't work

**Solution:**
- Verify the URL endpoint is correct and matches your ImageKit account
- Check ImageKit dashboard to confirm files were uploaded
- Verify CDN is properly configured in ImageKit dashboard

---

## Integration with CI/CD

Add to your CI/CD pipeline:

### GitHub Actions Example

```yaml
name: ImageKit Upload Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run ImageKit Upload Tests
        env:
          IMAGEKIT_PRIVATE_KEY: ${{ secrets.IMAGEKIT_PRIVATE_KEY }}
          IMAGEKIT_PUBLIC_KEY: ${{ secrets.IMAGEKIT_PUBLIC_KEY }}
          IMAGEKIT_URL_ENDPOINT: ${{ secrets.IMAGEKIT_URL_ENDPOINT }}
        run: |
          python manage.py test_imagekit_uploads --verbose
```

---

## Manual Testing Workflow

### 1. Test Basic Upload

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_basic_image_upload_to_imagekit
```

### 2. Test Product Image Creation

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_image_creation_with_imagekit
```

### 3. Verify Images in Dashboard

1. Log into ImageKit dashboard
2. Navigate to Media Library
3. Check for uploaded test images
4. Verify images are accessible via CDN

### 4. Test Full Workflow

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_with_multiple_images
```

---

## Performance Testing

For load testing image uploads:

```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_multiple_images_upload --verbosity=2
```

This test uploads 3 images in sequence and measures upload time.

---

## Debugging

Enable logging to see detailed upload information:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'nxtbn.core': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

Then run tests with verbose output:

```bash
python manage.py test_imagekit_uploads --verbose
```

---

## Additional Resources

- [ImageKit API Documentation](https://imagekit.io/docs/api-reference/)
- [ImageKit Python SDK](https://github.com/imagekit-developer/imagekit-python)
- [Django Storage Backends](https://docs.djangoproject.com/en/4.2/topics/files/storage/)
- [Product Tests](./test_imagekit_upload.py)

---

## Summary

These tests ensure that:

1. ✅ Images are uploaded to ImageKit correctly
2. ✅ URLs are generated accurately
3. ✅ Product-image relationships work
4. ✅ Multiple images can be uploaded
5. ✅ Files can be deleted
6. ✅ Metadata is preserved
7. ✅ The implementation matches ImageKit API spec

Run the tests regularly to catch any integration issues early.
