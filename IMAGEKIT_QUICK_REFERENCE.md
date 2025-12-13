# ImageKit Upload Testing - Quick Reference

## One-Line Quick Start

```bash
python manage.py test_imagekit_uploads --verbose
```

## Common Commands

| Task | Command |
|------|---------|
| Run all tests | `python manage.py test_imagekit_uploads` |
| Run with details | `python manage.py test_imagekit_uploads --verbose` |
| Test basic upload | `python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_basic_image_upload_to_imagekit` |
| Test product images | `python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_product_image_creation_with_imagekit` |
| Test multiple uploads | `python manage.py test nxtbn.product.tests.test_imagekit_upload.ImageKitUploadTestCase.test_multiple_images_upload` |
| Full test suite | `python manage.py test nxtbn.product.tests.test_imagekit_upload` |

## What Gets Tested

### Management Command Tests (7 tests)
1. Basic file upload
2. Image file upload
3. Multiple file uploads (batch)
4. URL generation
5. File metadata
6. Delete operation
7. Large image upload (1920x1080)

### Test Suite Tests (9 tests)
1. Basic image upload to ImageKit
2. Product image creation via Django ORM
3. Multiple images upload
4. Product with multiple images
5. Image variants (XS/thumbnail)
6. ImageKit URL format validation
7. Upload with ImageKit options
8. Upload response metadata
9. Image dimensions preservation

## Expected Results

✅ All 7 management command tests should PASS
✅ All 9 test suite tests should PASS

If any test fails:
1. Check ImageKit credentials in `.env`
2. Verify ImageKit API is accessible
3. Check internet connection
4. Review error message in output

## Required Environment Variables

```env
IMAGEKIT_PRIVATE_KEY=your_key_here
IMAGEKIT_PUBLIC_KEY=your_key_here
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_endpoint/
```

## Test Files Location

- **Management Command**: `nxtbn/core/management/commands/test_imagekit_uploads.py`
- **Test Suite**: `nxtbn/product/tests/test_imagekit_upload.py`
- **Documentation**: `IMAGEKIT_TESTING_GUIDE.md` (full guide)

## Verbose Output Example

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
----------------------------------------------------------------------
✅ All tests passed! (7/7)
======================================================================
```

## Debugging

Show detailed test output:
```bash
python manage.py test nxtbn.product.tests.test_imagekit_upload --verbosity=2
```

Show detailed management command output:
```bash
python manage.py test_imagekit_uploads --verbose
```

## Key API Endpoints Tested

According to [ImageKit API Reference](https://imagekit.io/docs/api-reference/upload-file/):

- **Upload File**: `POST /api/v1/files/upload`
  - Tests: File upload with multipart data
  - Validates: Response metadata, file_id, URL generation

- **Delete File**: `DELETE /api/v1/files/{fileId}`
  - Tests: File deletion by ID
  - Validates: Successful deletion

- **URL Construction**: CDN URL format
  - Tests: URL accessibility and format compliance
  - Validates: Endpoint integration

## Integration Points

✅ `nxtbn.core.imagekit_storage.ImageKitStorage`
- Primary storage backend
- Handles uploads/downloads/deletion

✅ `nxtbn.filemanager.models.Image`
- ImageField uses ImageKit storage
- `get_image_url()` and `get_image_xs_url()` methods

✅ `nxtbn.product.models.Product`
- Many-to-many relationship with Image
- Product images hosted on ImageKit

## CI/CD Integration

Add to your test suite:
```bash
pytest nxtbn/product/tests/test_imagekit_upload.py -v
# or
python manage.py test nxtbn.product.tests.test_imagekit_upload
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "ImageKit is not properly configured" | Set env vars in `.env` |
| "Connection refused" | Check ImageKit API is online |
| "Invalid credentials" | Verify API keys in ImageKit dashboard |
| "URL not accessible" | Check CDN configuration in ImageKit |
| Test hangs | Increase timeout or check network |

## Next Steps

1. ✅ Run management command: `python manage.py test_imagekit_uploads`
2. ✅ Run test suite: `python manage.py test nxtbn.product.tests.test_imagekit_upload`
3. ✅ Check ImageKit dashboard for uploaded files
4. ✅ Verify URLs are accessible
5. ✅ Integrate into CI/CD pipeline

---

**For full documentation, see**: `IMAGEKIT_TESTING_GUIDE.md`
