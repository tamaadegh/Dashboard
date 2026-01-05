"""
Quick diagnostic script to test image upload functionality.
Run with: python manage.py shell < test_image_upload_debug.py
"""

import io
import logging
from PIL import Image as PILImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from nxtbn.filemanager.models import Image
from nxtbn.users.models import User

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("=" * 80)
print("IMAGE UPLOAD DIAGNOSTIC TEST")
print("=" * 80)

# Step 1: Check if ImageKit is configured
print("\n1. Checking ImageKit Configuration...")
from django.conf import settings
print(f"   IS_IMAGEKIT: {getattr(settings, 'IS_IMAGEKIT', False)}")
print(f"   IMAGEKIT_PRIVATE_KEY: {'***' if settings.IMAGEKIT_PRIVATE_KEY else 'NOT SET'}")
print(f"   IMAGEKIT_PUBLIC_KEY: {'***' if settings.IMAGEKIT_PUBLIC_KEY else 'NOT SET'}")
print(f"   IMAGEKIT_URL_ENDPOINT: {settings.IMAGEKIT_URL_ENDPOINT or 'NOT SET'}")
print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

# Step 2: Check if storage backend can be initialized
print("\n2. Testing Storage Backend Initialization...")
try:
    from django.core.files.storage import default_storage
    print(f"   ✓ Storage backend: {type(default_storage).__name__}")
except Exception as e:
    print(f"   ✗ Failed to initialize storage: {e}")
    exit(1)

# Step 3: Create a test image in memory
print("\n3. Creating Test Image...")
try:
    img = PILImage.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    print(f"   ✓ Created test image: {len(img_io.getvalue())} bytes")
except Exception as e:
    print(f"   ✗ Failed to create test image: {e}")
    exit(1)

# Step 4: Test the serializer's optimize_image_from_bytes method
print("\n4. Testing Image Optimization...")
try:
    from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
    
    image_bytes = img_io.getvalue()
    
    # Test main image optimization
    print("   Testing main image optimization...")
    optimized_main = ImageSerializer.optimize_image_from_bytes(
        image_bytes,
        "test_image.jpg",
        max_size_kb=200,
        format="WEBP",
        max_dimension=800
    )
    print(f"   ✓ Main image optimized: {optimized_main.name}, {len(optimized_main.read())} bytes")
    
    # Test thumbnail optimization
    print("   Testing thumbnail optimization...")
    optimized_thumb = ImageSerializer.optimize_image_from_bytes(
        image_bytes,
        "test_image.jpg",
        max_size_kb=10,
        format="png",
        max_dimension=50
    )
    print(f"   ✓ Thumbnail optimized: {optimized_thumb.name}, {len(optimized_thumb.read())} bytes")
    
except Exception as e:
    print(f"   ✗ Optimization failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: Test storage upload
print("\n5. Testing Storage Upload...")
try:
    img_io.seek(0)
    test_name = default_storage.save('test_upload.jpg', img_io)
    print(f"   ✓ File saved: {test_name}")
    
    url = default_storage.url(test_name)
    print(f"   ✓ File URL: {url}")
    
    # Clean up
    default_storage.delete(test_name)
    print(f"   ✓ Test file deleted")
    
except Exception as e:
    print(f"   ✗ Storage upload failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 6: Test full serializer flow (without actual DB save)
print("\n6. Testing Full Serializer Flow...")
try:
    # Get a test user
    user = User.objects.first()
    if not user:
        print("   ✗ No users found in database")
        exit(1)
    
    print(f"   Using user: {user.email}")
    
    # Create uploaded file object
    img_io.seek(0)
    uploaded_file = InMemoryUploadedFile(
        img_io,
        field_name='image',
        name='test_upload.jpg',
        content_type='image/jpeg',
        size=len(img_io.getvalue()),
        charset=None
    )
    
    # Create mock request
    class MockRequest:
        def __init__(self, user):
            self.user = user
    
    # Test serializer
    from rest_framework.request import Request
    from django.test import RequestFactory
    
    factory = RequestFactory()
    django_request = factory.post('/test/')
    django_request.user = user
    
    serializer = ImageSerializer(
        data={
            'name': 'Test Image',
            'image': uploaded_file,
            'image_alt_text': 'Test'
        },
        context={'request': MockRequest(user)}
    )
    
    if serializer.is_valid():
        print("   ✓ Serializer validation passed")
        print("   Note: Not saving to database in this test")
    else:
        print(f"   ✗ Serializer validation failed: {serializer.errors}")
        exit(1)
    
except Exception as e:
    print(f"   ✗ Serializer test failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED ✓")
print("=" * 80)
print("\nIf uploads are still failing in production, check:")
print("1. Application logs for detailed error messages")
print("2. ImageKit dashboard for API errors")
print("3. Network connectivity to ImageKit API")
print("4. File size limits in your deployment platform")
