#!/usr/bin/env python
"""
Test the ImageKitStorage backend directly
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage

print("\n[DEBUG] Testing ImageKitStorage backend directly...")
print(f"[DEBUG] Storage backend: {type(default_storage).__name__}")

# Test with real image
pic_dir = Path(__file__).resolve().parent / 'picsImages'
real_images = [f for f in pic_dir.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg'}]

if not real_images:
    print("[FAIL] No JPEG images found")
    sys.exit(1)

image_path = real_images[0]
print(f"\n[DEBUG] Using image: {image_path.name}")
print(f"[DEBUG] File size: {image_path.stat().st_size / 1024:.1f} KB")

# Load image
with open(image_path, 'rb') as f:
    content = f.read()

print(f"[DEBUG] Loaded {len(content)} bytes")

# Create SimpleUploadedFile
test_image = SimpleUploadedFile(
    image_path.name,
    content,
    content_type='image/jpeg'
)

print(f"[DEBUG] Created SimpleUploadedFile: {test_image.name}")
print(f"[DEBUG] Content type: {test_image.content_type}")
print(f"[DEBUG] Size: {test_image.size}")

# Try to save via storage
print(f"\n[DEBUG] Calling default_storage.save()...")

try:
    saved_name = default_storage.save(f'images/{image_path.name}', test_image)
    print(f"[OK] File saved successfully!")
    print(f"    Saved name: {saved_name}")
    
    # Get URL
    url = default_storage.url(saved_name)
    print(f"[OK] URL: {url[:80]}...")
    
    # Cleanup
    default_storage.delete(saved_name)
    print(f"[OK] File deleted")
    
except Exception as e:
    print(f"[FAIL] Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n[DEBUG] Test complete - SUCCESS!")
