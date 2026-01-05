#!/usr/bin/env python
"""
Quick test runner for image upload functionality.
Run with: python test_image_upload_quick.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Now import after Django is set up
import io
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer

print("="*80)
print("QUICK IMAGE UPLOAD TEST")
print("="*80)
print()

# Test 1: optimize_image_from_bytes with WEBP
print("Test 1: optimize_image_from_bytes - WEBP format")
print("-"*80)
try:
    img = PILImage.new('RGB', (800, 600), color='blue')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    image_bytes = img_io.getvalue()
    
    print(f"  Created test image: {len(image_bytes)} bytes")
    
    optimized = ImageSerializer.optimize_image_from_bytes(
        image_bytes,
        'test_image.jpg',
        max_size_kb=200,
        format='WEBP',
        max_dimension=800
    )
    
    optimized_content = optimized.read()
    print(f"  ✓ Optimized to: {len(optimized_content)} bytes ({len(optimized_content)/1024:.1f}KB)")
    print(f"  ✓ Filename: {optimized.name}")
    print("✅ TEST 1 PASSED")
except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: optimize_image_from_bytes with PNG thumbnail
print("Test 2: optimize_image_from_bytes - PNG thumbnail")
print("-"*80)
try:
    img = PILImage.new('RGB', (1920, 1080), color='green')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    image_bytes = img_io.getvalue()
    
    print(f"  Created large image: {len(image_bytes)} bytes")
    
    thumbnail = ImageSerializer.optimize_image_from_bytes(
        image_bytes,
        'large_image.jpg',
        max_size_kb=10,
        format='png',
        max_dimension=50
    )
    
    thumb_content = thumbnail.read()
    print(f"  ✓ Thumbnail: {len(thumb_content)} bytes ({len(thumb_content)/1024:.1f}KB)")
    print(f"  ✓ Filename: {thumbnail.name}")
    print("✅ TEST 2 PASSED")
except Exception as e:
    print(f"❌ TEST 2 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Multiple calls with same bytes (THE CRITICAL FIX)
print("Test 3: Multiple calls with same bytes (CRITICAL FIX TEST)")
print("-"*80)
try:
    img = PILImage.new('RGB', (1024, 768), color='purple')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    image_bytes = img_io.getvalue()
    
    print(f"  Created test image: {len(image_bytes)} bytes")
    
    # First call
    print("  → Creating main image (WEBP)...")
    main_image = ImageSerializer.optimize_image_from_bytes(
        image_bytes,
        'test.jpg',
        max_size_kb=200,
        format='WEBP',
        max_dimension=800
    )
    main_content = main_image.read()
    print(f"    ✓ Main image: {len(main_content)} bytes")
    
    # Second call with SAME bytes
    print("  → Creating thumbnail (PNG) from SAME bytes...")
    thumbnail = ImageSerializer.optimize_image_from_bytes(
        image_bytes,  # Same bytes!
        'test.jpg',
        max_size_kb=10,
        format='png',
        max_dimension=50
    )
    thumb_content = thumbnail.read()
    print(f"    ✓ Thumbnail: {len(thumb_content)} bytes")
    
    print("✅ TEST 3 PASSED - Can process same bytes multiple times!")
except Exception as e:
    print(f"❌ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Test with actual storage backend (if ImageKit is configured)
print("Test 4: Storage backend test")
print("-"*80)
try:
    from django.core.files.storage import default_storage
    from django.conf import settings
    
    print(f"  Storage backend: {type(default_storage).__name__}")
    print(f"  IS_IMAGEKIT: {getattr(settings, 'IS_IMAGEKIT', False)}")
    
    if getattr(settings, 'IS_IMAGEKIT', False):
        print("  → Testing ImageKit upload...")
        
        img = PILImage.new('RGB', (400, 300), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        test_file = SimpleUploadedFile(
            'storage_test.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        saved_path = default_storage.save('test_uploads/storage_test.jpg', test_file)
        print(f"  ✓ Saved to: {saved_path}")
        
        url = default_storage.url(saved_path)
        print(f"  ✓ URL: {url}")
        
        # Cleanup
        default_storage.delete(saved_path)
        print("  ✓ Cleaned up test file")
        
        print("✅ TEST 4 PASSED - ImageKit storage works")
    else:
        print("  ℹ ImageKit not configured, using local storage")
        print("✅ TEST 4 SKIPPED")
        
except Exception as e:
    print(f"❌ TEST 4 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("TESTS COMPLETE")
print("="*80)
