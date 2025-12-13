#!/usr/bin/env python
"""
Quick test script to verify ImageKit uploads with real images
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile

print("\n" + "="*70)
print("ImageKit Real Image Upload Test")
print("="*70 + "\n")

# Get real images
pic_dir = Path(__file__).resolve().parent / 'picsImages'
real_images = [f for f in pic_dir.iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png'}]

print(f"[INFO] Found {len(real_images)} real images in picsImages folder")

if not real_images:
    print("[FAIL] No images found!")
    sys.exit(1)

# Test with first real image
image_path = real_images[0]
print(f"[INFO] Using image: {image_path.name}")
print(f"[INFO] File size: {image_path.stat().st_size / 1024:.1f} KB")

try:
    # Load image
    with open(image_path, 'rb') as f:
        content = f.read()
    
    # Determine content type
    ext = image_path.suffix.lower()
    content_type = 'image/jpeg' if ext in {'.jpg', '.jpeg'} else 'image/png'
    
    # Create uploaded file
    test_image = SimpleUploadedFile(
        image_path.name,
        content,
        content_type=content_type
    )
    
    print(f"\n[INFO] Uploading to ImageKit...")
    
    saved_name = default_storage.save(f'images/{image_path.name}', test_image)
    
    print(f"[OK] Image uploaded successfully!")
    print(f"     Saved as: {saved_name}")
    
    # Get URL
    url = default_storage.url(saved_name)
    print(f"[OK] URL generated: {url[:80]}...")
    
    # Cleanup
    default_storage.delete(saved_name)
    print(f"[OK] Image deleted successfully")
        
except Exception as e:
    print(f"[FAIL] Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("Test completed successfully!")
print("="*70 + "\n")
