#!/usr/bin/env python
"""
Test with logging enabled
"""
import os
import sys
import django
from pathlib import Path
import logging

# Setup logging FIRST
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage

print("\n[DEBUG] Testing with logging enabled...")

# Use first JPEG
pic_dir = Path(__file__).resolve().parent / 'picsImages'
real_images = [f for f in pic_dir.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg'}]

if not real_images:
    print("[FAIL] No JPEG images")
    sys.exit(1)

image_path = real_images[0]
with open(image_path, 'rb') as f:
    content = f.read()

print(f"\n[START] Saving {image_path.name} ({len(content)} bytes)")

test_image = SimpleUploadedFile(image_path.name, content, content_type='image/jpeg')

try:
    saved_name = default_storage.save(f'images/{image_path.name}', test_image)
    print(f"\n[OK] Saved as: {saved_name}")
    
    url = default_storage.url(saved_name)
    print(f"[OK] URL: {url[:80]}...")
    
    default_storage.delete(saved_name)
    print(f"[OK] Deleted")
    
except Exception as e:
    print(f"\n[FAIL] Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n[OK] Test complete!")
