# ImageKit Upload Flow & Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Upload Flow                                  │
└─────────────────────────────────────────────────────────────────────┘

1. Image File Upload (via Django Admin or API)
   │
   └─→ Product Model / Image Model
       │
       └─→ ImageField (storage=default_storage)
           │
           └─→ ImageKitStorage._save()
               │
               └─→ imagekitio.ImageKit.upload_file()
                   │
                   └─→ [HTTP] POST to ImageKit API
                       │
                       ├─→ https://api.imagekit.io/api/v1/files/upload
                       │
                       └─→ ImageKit Servers
                           │
                           ├─→ File Storage (CDN)
                           ├─→ Generate CDN URL
                           └─→ Return Response {file_id, url, ...}
                               │
                               └─→ Back to Storage Backend
                                   │
                                   └─→ Django Model Saves Reference
                                       │
                                       └─→ Database (file path/ID)


2. URL Generation (when accessing image)
   │
   └─→ Image.get_image_url(request)
       │
       └─→ image.url property
           │
           └─→ ImageKitStorage.url()
               │
               └─→ Returns CDN URL
                   │
                   └─→ Client/Browser
                       │
                       └─→ [HTTP GET] to ImageKit CDN
                           │
                           └─→ https://ik.imagekit.io/endpoint/path/...
                               │
                               └─→ Image Delivered via CDN


3. Deletion (when removing image)
   │
   └─→ Image.delete() or image.image.delete()
       │
       └─→ ImageKitStorage.delete()
           │
           └─→ imagekitio.ImageKit.delete_file()
               │
               └─→ [HTTP] DELETE to ImageKit API
                   │
                   └─→ ImageKit Removes File
                       │
                       └─→ Deletion Confirmed
```

---

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Django Application                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Views / Admin / API Endpoints                              │ │
│  │  (Product Admin, Image Upload, etc.)                        │ │
│  └────────────────────────┬────────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼────────────────────────────────────┐ │
│  │  Django Models                                              │ │
│  │  ┌───────────────────┐  ┌──────────────────────────────┐   │ │
│  │  │  Product Model    │  │  Image Model                 │   │ │
│  │  ├───────────────────┤  ├──────────────────────────────┤   │ │
│  │  │ - id              │  │ - id                         │   │ │
│  │  │ - name            │  │ - name                       │   │ │
│  │  │ - images (M2M) ──────→ - image (ImageField)        │   │ │
│  │  │ - ...             │  │ - image_xs (ImageField)      │   │ │
│  │  └───────────────────┘  │ - created_by                 │   │ │
│  │                         └──────────────────────────────┘   │ │
│  └────────────────────────┬────────────────────────────────────┘ │
│                           │                                       │
│  ┌────────────────────────▼────────────────────────────────────┐ │
│  │  Default File Storage (from settings.py)                   │ │
│  │  DEFAULT_FILE_STORAGE =                                    │ │
│  │  'nxtbn.core.imagekit_storage.ImageKitStorage'            │ │
│  └────────────────────────┬────────────────────────────────────┘ │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                   ImageKitStorage Backend                          │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  class ImageKitStorage(Storage):                         │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │  def __init__(self):                               │  │    │
│  │  │      self.client = ImageKit(                       │  │    │
│  │  │          private_key=IMAGEKIT_PRIVATE_KEY,        │  │    │
│  │  │          public_key=IMAGEKIT_PUBLIC_KEY,          │  │    │
│  │  │          url_endpoint=IMAGEKIT_URL_ENDPOINT       │  │    │
│  │  │      )                                             │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │  def _save(self, name, content):                   │  │    │
│  │  │      return self.client.upload_file(               │  │    │
│  │  │          file=content,                             │  │    │
│  │  │          file_name=name                            │  │    │
│  │  │      )                                             │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │  def url(self, name):                              │  │    │
│  │  │      return generate_cdn_url(name)                 │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  │  ┌────────────────────────────────────────────────────┐  │    │
│  │  │  def delete(self, name):                           │  │    │
│  │  │      self.client.delete_file(file_id=name)        │  │    │
│  │  └────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ (HTTP Requests)
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                   ImageKit Python SDK                             │
│                   (imagekitio library)                            │
├───────────────────────────────────────────────────────────────────┤
│  - Handles API authentication                                     │
│  - Constructs HTTP requests                                       │
│  - Parses responses                                               │
│  - Returns metadata (file_id, url, etc.)                          │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ (HTTPS)
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                   ImageKit API Servers                            │
│                   (imagekit.io)                                   │
├───────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                        │
│  - POST   /api/v1/files/upload          (Upload file)            │
│  - DELETE /api/v1/files/{fileId}        (Delete file)            │
│  - GET    /api/v1/files/{fileId}        (Get file info)          │
│                                                                    │
│  Responses:                                                        │
│  {                                                                 │
│    "file_id": "xyz123",                                           │
│    "file_name": "image.jpg",                                      │
│    "url": "https://ik.imagekit.io/.../image.jpg",               │
│    "height": 800,                                                 │
│    "width": 600,                                                  │
│    "file_type": "image",                                          │
│    "file_size": 102400                                            │
│  }                                                                 │
└───────────────────────────┬───────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ┌────────┐          ┌────────┐         ┌────────┐
    │ CDN    │          │ Storage│         │ Cache  │
    │ Nodes  │          │Buckets │         │Servers │
    └────────┘          └────────┘         └────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    Serves Images
```

---

## Test Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  Test Execution Flow                                              │
└──────────────────────────────────────────────────────────────────┘

1. Management Command: python manage.py test_imagekit_uploads
   │
   ├─→ [Test 1] Basic File Upload
   │   ├─→ Create test content
   │   ├─→ Call default_storage.save()
   │   ├─→ Get URL
   │   ├─→ Cleanup
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 2] Image File Upload
   │   ├─→ Create PIL image
   │   ├─→ Save to storage
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 3] Multiple Uploads (×3)
   │   ├─→ Create 3 images
   │   ├─→ Upload all
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 4] URL Generation
   │   ├─→ Upload image
   │   ├─→ Get URL
   │   ├─→ Validate format
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 5] Metadata
   │   ├─→ Upload image
   │   ├─→ Check existence
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 6] Delete
   │   ├─→ Upload image
   │   ├─→ Delete file
   │   └─→ ✅/❌ Result
   │
   ├─→ [Test 7] Large Image
   │   ├─→ Create 1920×1080 image
   │   ├─→ Upload
   │   └─→ ✅/❌ Result
   │
   └─→ Summary Report
       ├─→ Tests Passed: X/7
       ├─→ Success Rate: Y%
       └─→ Overall: ✅ or ⚠️


2. Test Suite: python manage.py test nxtbn.product.tests.test_imagekit_upload
   │
   ├─→ ImageKitUploadTestCase
   │   ├─→ test_basic_image_upload_to_imagekit
   │   ├─→ test_product_image_creation_with_imagekit
   │   ├─→ test_multiple_images_upload
   │   ├─→ test_product_with_multiple_images
   │   ├─→ test_image_with_small_variant
   │   ├─→ test_imagekit_url_format
   │   └─→ test_upload_with_imagekit_options
   │
   └─→ ImageKitUploadValidationTestCase
       ├─→ test_upload_response_metadata
       └─→ test_image_dimensions_preserved
```

---

## Configuration & Environment

```
┌──────────────────────────────────────────────────────────────────┐
│  Configuration Sources                                            │
└──────────────────────────────────────────────────────────────────┘

.env file (local)
├── IMAGEKIT_PRIVATE_KEY
├── IMAGEKIT_PUBLIC_KEY
└── IMAGEKIT_URL_ENDPOINT
    │
    │ (loaded via)
    │
nxtbn/settings.py
├── IS_IMAGEKIT = bool(all three keys)
└── DEFAULT_FILE_STORAGE = 'nxtbn.core.imagekit_storage.ImageKitStorage'
    │
    │ (used by)
    │
nxtbn/core/imagekit_storage.py
├── ImageKitStorage.__init__()
│   └── Creates ImageKit client
└── ImageKit methods
    ├── upload_file()
    ├── delete_file()
    └── url generation
```

---

## API Integration Points

```
┌──────────────────────────────────────────────────────────────────┐
│  ImageKit API Integration                                         │
└──────────────────────────────────────────────────────────────────┘

imagekitio Library
├── class ImageKit
│   ├── __init__(private_key, public_key, url_endpoint)
│   ├── upload_file(file, file_name, options={})
│   │   └─→ POST /api/v1/files/upload
│   ├── delete_file(file_id)
│   │   └─→ DELETE /api/v1/files/{file_id}
│   ├── get_file_details(file_id)
│   │   └─→ GET /api/v1/files/{file_id}/details
│   └── list_files(options={})
│       └─→ GET /api/v1/files
│
Response Structure
├── file_id (string)
├── file_name (string)
├── url (string) - CDN URL
├── file_type (string) - 'image', 'file'
├── height (integer)
├── width (integer)
├── file_size (integer)
└── created_at (timestamp)
```

---

## Model Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│  Django Model Relationships                                       │
└──────────────────────────────────────────────────────────────────┘

Product (1)
├── name: CharField
├── summary: TextField
├── description: JSONField (Editor.js)
├── created_by: FK → User
├── category: FK → Category
├── images: M2M → Image (through ProductImage)
├── variants: O2M → ProductVariant
└── ...

    │
    │ ManyToMany
    │ (through=None)
    │
    └─→ Image (Many)
        ├── id: UUID
        ├── name: CharField
        ├── image: ImageField
        │   └── upload_to = 'images/'
        │   └── storage = ImageKitStorage
        ├── image_xs: ImageField
        │   └── upload_to = 'images/xs/'
        │   └── storage = ImageKitStorage
        ├── image_alt_text: CharField
        └── created_by: FK → User

ProductVariant (Many)
└── image: FK → Image (null=True)
    └── Links to Image for variant-specific image
```

---

## Request/Response Example

```
┌──────────────────────────────────────────────────────────────────┐
│  Sample Upload Request/Response                                   │
└──────────────────────────────────────────────────────────────────┘

REQUEST
├── URL: https://upload.imagekit.io/api/v1/files/upload
├── Method: POST
├── Auth: Basic (Private Key)
├── Headers:
│   └── Content-Type: multipart/form-data
├── Body:
│   ├── file: <binary image data>
│   ├── file_name: product_image_123.jpg
│   ├── folder: /test-uploads/
│   ├── use_unique_file_name: true
│   └── tags: ["product", "image"]
│

RESPONSE (200 OK)
{
  "file_id": "5e1c2d3f4g5h6i7j8k9l",
  "file_name": "product_image_123.jpg",
  "url": "https://ik.imagekit.io/your_endpoint/test-uploads/product_image_123.jpg",
  "response_metadata": {
    "http_status_code": 200
  },
  "file_type": "image",
  "mime_type": "image/jpeg",
  "image_metadata": {
    "width": 1920,
    "height": 1080,
    "has_color": true
  },
  "file_size": 256000,
  "created_at": "2025-12-13T10:30:45.000Z"
}
```

---

## Storage Backend Methods Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  ImageKitStorage Method Flows                                     │
└──────────────────────────────────────────────────────────────────┘

SAVE OPERATION
──────────────
image.save(...)
  │
  └─→ ImageField.save()
      │
      └─→ storage._save(name, content)
          │
          ├─→ content.read() [get file bytes]
          │
          ├─→ self.client.upload_file(
          │       file=file_data,
          │       file_name=name
          │   )
          │
          ├─→ [ImageKit API Response]
          │
          └─→ Return file_id or name [saved to DB]


URL OPERATION
─────────────
image.image.url
  │
  └─→ ImageField.url property
      │
      └─→ storage.url(name)
          │
          └─→ Construct CDN URL
              │
              └─→ Return: 
                  https://ik.imagekit.io/endpoint/images/file.jpg


DELETE OPERATION
────────────────
image.delete()
  │
  └─→ ImageField.delete()
      │
      └─→ storage.delete(name)
          │
          └─→ self.client.delete_file(file_id=name)
              │
              └─→ [ImageKit API DELETE]
                  │
                  └─→ File removed from CDN
```

---

## Performance Characteristics

```
┌──────────────────────────────────────────────────────────────────┐
│  Expected Performance Metrics                                     │
└──────────────────────────────────────────────────────────────────┘

Upload Operations
├── Small image (< 1MB)      : ~500ms - 2s
├── Medium image (1-5MB)     : ~1s - 5s
├── Large image (5-20MB)     : ~5s - 15s
└── Network latency          : ~100-500ms (varies by location)

URL Generation
├── URL construction         : ~1ms
└── Return CDN URL          : Instant (no API call)

Delete Operations
├── Delete file              : ~500ms - 2s
└── Clear from CDN          : ~30s (cache expiration)

Read Operations
├── Get CDN URL              : ~1ms (instant)
├── Fetch from CDN           : ~200ms - 2s (depends on file size & location)
└── Browser cache            : Instant (if cached)

Metadata Retrieval
├── Upload response          : Included (no extra call)
├── Get file details         : ~300-800ms (optional API call)
└── List files               : ~1-3s per request
```

---

This architecture ensures reliable, scalable image hosting for your product catalog!
