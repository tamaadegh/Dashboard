#!/usr/bin/env python
"""
Check if ImageKit settings are actually configured
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
django.setup()

from django.conf import settings

print("\n[DEBUG] Checking ImageKit Configuration...")
print(f"IMAGEKIT_PRIVATE_KEY: {'SET' if settings.IMAGEKIT_PRIVATE_KEY else 'NOT SET'}")
print(f"IMAGEKIT_PUBLIC_KEY: {'SET' if settings.IMAGEKIT_PUBLIC_KEY else 'NOT SET'}")
print(f"IMAGEKIT_URL_ENDPOINT: {'SET' if settings.IMAGEKIT_URL_ENDPOINT else 'NOT SET'}")

if settings.IMAGEKIT_PRIVATE_KEY and settings.IMAGEKIT_PUBLIC_KEY and settings.IMAGEKIT_URL_ENDPOINT:
    print(f"\n[OK] All ImageKit settings are configured!")
    print(f"    Endpoint: {settings.IMAGEKIT_URL_ENDPOINT}")
else:
    print(f"\n[FAIL] ImageKit settings are not properly configured!")
    print(f"    Private key set: {bool(settings.IMAGEKIT_PRIVATE_KEY)}")
    print(f"    Public key set: {bool(settings.IMAGEKIT_PUBLIC_KEY)}")
    print(f"    URL endpoint set: {bool(settings.IMAGEKIT_URL_ENDPOINT)}")

print(f"\nDEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

from django.core.files.storage import default_storage
print(f"default_storage type: {type(default_storage).__name__}")
print(f"default_storage class: {default_storage.__class__.__module__}.{default_storage.__class__.__name__}")
