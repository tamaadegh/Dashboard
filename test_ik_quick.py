#!/usr/bin/env python
"""Quick test of ImageKit API"""

import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')

import django
django.setup()

from django.conf import settings
from imagekitio import ImageKit
import io

print("Testing ImageKit integration...")
print(f"Endpoint: {settings.IMAGEKIT_URL_ENDPOINT}")
print(f"Has private key: {bool(settings.IMAGEKIT_PRIVATE_KEY)}")
print(f"Has public key: {bool(settings.IMAGEKIT_PUBLIC_KEY)}")

# Try to create a client
try:
    ik = ImageKit(
        private_key=settings.IMAGEKIT_PRIVATE_KEY,
        public_key=settings.IMAGEKIT_PUBLIC_KEY,
        url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
    )
    print("\n[OK] ImageKit client created successfully")
    print(f"Methods: {[m for m in dir(ik) if 'upload' in m.lower() or 'file' in m.lower()]}")
except Exception as e:
    print(f"\n[FAIL] Error creating ImageKit client: {e}")
    sys.exit(1)

# Test simple upload
try:
    test_data = b"Test content"
    response = ik.upload_file(
        file=test_data,
        file_name="test_quick.txt"
    )
    print(f"\n[OK] Upload successful!")
    print(f"Response: {response}")
    print(f"File ID: {response.file_id if hasattr(response, 'file_id') else 'N/A'}")
except Exception as e:
    print(f"\n[FAIL] Error uploading file: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
