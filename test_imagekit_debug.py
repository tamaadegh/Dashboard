#!/usr/bin/env python
"""
Debug test script to diagnose ImageKit upload issues
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
django.setup()

print("\n[DEBUG] Testing ImageKit client directly...")

from imagekitio import ImageKit
from django.conf import settings
import io

# Create client
client = ImageKit(
    private_key=settings.IMAGEKIT_PRIVATE_KEY,
    public_key=settings.IMAGEKIT_PUBLIC_KEY,
    url_endpoint=settings.IMAGEKIT_URL_ENDPOINT,
)

print(f"[OK] ImageKit client created")
print(f"    Endpoint: {settings.IMAGEKIT_URL_ENDPOINT}")

# Test with small content
print(f"\n[DEBUG] Testing with small text file...")
small_content = b"Test content"
print(f"    Content size: {len(small_content)} bytes")

try:
    print(f"    Calling upload_file...")
    response = client.upload_file(
        file=small_content,
        file_name="test_small.txt",
    )
    print(f"[OK] Small file upload successful")
    print(f"    File ID: {response.file_id}")
except Exception as e:
    print(f"[FAIL] Small file upload failed: {str(e)}")
    import traceback
    traceback.print_exc()

# Test with real image
print(f"\n[DEBUG] Testing with real image...")
pic_dir = Path(__file__).resolve().parent / 'picsImages'
real_images = [f for f in pic_dir.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg'}]

if real_images:
    image_path = real_images[0]
    print(f"    Using: {image_path.name}")
    print(f"    Size: {image_path.stat().st_size / 1024:.1f} KB")
    
    with open(image_path, 'rb') as f:
        content = f.read()
    
    try:
        print(f"    Calling upload_file...")
        response = client.upload_file(
            file=content,
            file_name=image_path.name,
        )
        print(f"[OK] Image upload successful")
        print(f"    File ID: {response.file_id}")
    except Exception as e:
        print(f"[FAIL] Image upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print(f"    No JPEG images found")

print(f"\n[DEBUG] Test complete")
