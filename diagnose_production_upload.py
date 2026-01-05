#!/usr/bin/env python
"""
Production Image Upload Diagnostic Tool
Run this in production to diagnose upload issues.

Usage:
  # Linux/Mac:
  python manage.py shell < diagnose_production_upload.py
  
  # Windows PowerShell:
  Get-Content diagnose_production_upload.py | python manage.py shell
  
  # Or directly:
  python diagnose_production_upload.py
"""

import os
import sys

def main():
    """Main diagnostic function"""
    print("\n" + "="*80)
    print("PRODUCTION IMAGE UPLOAD DIAGNOSTIC")
    print("="*80 + "\n")

    # Step 1: Check Django settings
    print("1. Checking Django Configuration...")
    print("-"*80)
    from django.conf import settings

    print(f"DEBUG: {settings.DEBUG}")
    print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
    print(f"IS_IMAGEKIT: {getattr(settings, 'IS_IMAGEKIT', False)}")

    # Check ImageKit credentials
    has_private_key = bool(getattr(settings, 'IMAGEKIT_PRIVATE_KEY', ''))
    has_public_key = bool(getattr(settings, 'IMAGEKIT_PUBLIC_KEY', ''))
    has_endpoint = bool(getattr(settings, 'IMAGEKIT_URL_ENDPOINT', ''))
    
    print(f"IMAGEKIT_PRIVATE_KEY: {'***SET***' if has_private_key else 'NOT SET'}")
    print(f"IMAGEKIT_PUBLIC_KEY: {'***SET***' if has_public_key else 'NOT SET'}")
    print(f"IMAGEKIT_URL_ENDPOINT: {getattr(settings, 'IMAGEKIT_URL_ENDPOINT', 'NOT SET')}")
    
    # Check STORAGES (Django 4.2+)
    storages_config = getattr(settings, 'STORAGES', {})
    if storages_config:
        default_backend = storages_config.get('default', {}).get('BACKEND', 'NOT SET')
        print(f"STORAGES['default']['BACKEND']: {default_backend}")

    print()

    # Step 2: Check storage backend
    print("2. Checking Storage Backend...")
    print("-"*80)
    try:
        from django.core.files.storage import default_storage
        storage_class = type(default_storage).__name__
        storage_module = type(default_storage).__module__
        
        print(f"Storage class: {storage_class}")
        print(f"Storage module: {storage_module}")
        
        # Check if using ImageKit
        is_imagekit_storage = 'imagekit' in storage_module.lower()
        if is_imagekit_storage:
            print("✓ Using ImageKit storage")
            if hasattr(default_storage, 'client'):
                print("✓ ImageKit client initialized")
            else:
                print("✗ ImageKit client NOT initialized")
        else:
            print(f"ℹ Using {storage_class} (not ImageKit)")
    except Exception as e:
        print(f"✗ Storage backend error: {e}")

    print()

    # Step 3: Test image optimization
    print("3. Testing Image Optimization...")
    print("-"*80)
    try:
        from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
        from PIL import Image as PILImage
        import io
        
        # Create test image
        img = PILImage.new('RGB', (100, 100), color='blue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        image_bytes = img_io.getvalue()
        
        print(f"Created test image: {len(image_bytes)} bytes")
        
        # Test main image optimization
        print("  → Testing WEBP optimization...")
        main_image = ImageSerializer.optimize_image_from_bytes(
            image_bytes,
            'test.jpg',
            max_size_kb=200,
            format='WEBP',
            max_dimension=800
        )
        main_content = main_image.read()
        print(f"  ✓ Main image: {len(main_content)} bytes")
        
        # Test thumbnail optimization
        print("  → Testing PNG thumbnail...")
        thumbnail = ImageSerializer.optimize_image_from_bytes(
            image_bytes,
            'test.jpg',
            max_size_kb=10,
            format='png',
            max_dimension=50
        )
        thumb_content = thumbnail.read()
        print(f"  ✓ Thumbnail: {len(thumb_content)} bytes")
        
        print("✓ Image optimization works correctly")
        
    except Exception as e:
        print(f"✗ Image optimization failed: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Step 4: Test storage upload
    print("4. Testing Storage Upload...")
    print("-"*80)
    try:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.files.storage import default_storage
        from PIL import Image as PILImage
        import io
        
        # Create test image
        img = PILImage.new('RGB', (200, 200), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        test_file = SimpleUploadedFile(
            'diagnostic_test.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        print(f"Created test file: {test_file.size} bytes")
        
        # Try to save
        print("  → Uploading to storage...")
        saved_path = default_storage.save('diagnostic/test_upload.jpg', test_file)
        print(f"  ✓ Saved to: {saved_path}")
        
        # Get URL
        url = default_storage.url(saved_path)
        print(f"  ✓ URL: {url}")
        
        # Cleanup
        print("  → Cleaning up...")
        default_storage.delete(saved_path)
        print("  ✓ Test file deleted")
        
        print("✓ Storage upload works correctly")
        
    except Exception as e:
        print(f"✗ Storage upload failed: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Step 5: Test full serializer flow
    print("5. Testing Full Serializer Flow...")
    print("-"*80)
    try:
        from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
        from nxtbn.users.models import User
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image as PILImage
        import io
        
        # Get a user
        user = User.objects.first()
        if not user:
            print("✗ No users found in database")
        else:
            print(f"Using user: {user.email}")
            
            # Create test image
            img = PILImage.new('RGB', (300, 300), color='green')
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)
            
            test_file = SimpleUploadedFile(
                'serializer_diagnostic.jpg',
                img_io.getvalue(),
                content_type='image/jpeg'
            )
            
            # Create mock request
            class MockRequest:
                def __init__(self, user):
                    self.user = user
            
            # Test serializer
            print("  → Validating serializer...")
            serializer = ImageSerializer(
                data={
                    'name': 'Diagnostic Test Image',
                    'image': test_file,
                    'image_alt_text': 'Diagnostic test'
                },
                context={'request': MockRequest(user)}
            )
            
            if serializer.is_valid():
                print("  ✓ Serializer validation passed")
                
                print("  → Saving image...")
                image = serializer.save()
                
                print(f"  ✓ Image saved with ID: {image.id}")
                print(f"  ✓ Main image: {image.image}")
                if image.image_xs:
                    print(f"  ✓ Thumbnail: {image.image_xs}")
                
                print("✓ Full serializer flow works correctly")
                
                # Cleanup
                print("  → Cleaning up test image...")
                image.delete()
                print("  ✓ Test image deleted")
                
            else:
                print(f"✗ Serializer validation failed: {serializer.errors}")
                
    except Exception as e:
        print(f"✗ Serializer flow failed: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Summary
    print("="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    print()
    print("If all steps passed (✓), the image upload system is working correctly.")
    print("If any step failed (✗), check the error messages above.")
    print()
    print("Common issues:")
    print("  - ImageKit credentials not set → Check environment variables")
    print("  - Storage upload fails → Check network connectivity to ImageKit")
    print("  - Serializer fails → Check the detailed error traceback")
    print()


if __name__ == '__main__':
    # Running directly
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    django.setup()
    main()
else:
    # Running via Django shell
    main()
