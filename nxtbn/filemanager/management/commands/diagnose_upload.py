"""
Django management command to diagnose image upload system.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
import io


class Command(BaseCommand):
    help = 'Diagnose production image upload system'

    def handle(self, *args, **options):
        """Run diagnostic tests"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write("PRODUCTION IMAGE UPLOAD DIAGNOSTIC")
        self.stdout.write("="*80 + "\n")

        # Step 1: Check Django settings
        self.check_django_configuration()
        
        # Step 2: Check storage backend
        self.check_storage_backend()
        
        # Step 3: Test image optimization
        self.test_image_optimization()
        
        # Step 4: Test storage upload
        self.test_storage_upload()
        
        # Step 5: Test full serializer flow
        self.test_serializer_flow()
        
        # Summary
        self.print_summary()

    def check_django_configuration(self):
        """Step 1: Check Django Configuration"""
        self.stdout.write("\n1. Checking Django Configuration...")
        self.stdout.write("-"*80)
        
        self.stdout.write(f"DEBUG: {settings.DEBUG}")
        self.stdout.write(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')}")
        self.stdout.write(f"IS_IMAGEKIT: {getattr(settings, 'IS_IMAGEKIT', False)}")

        # Check ImageKit credentials
        has_private_key = bool(getattr(settings, 'IMAGEKIT_PRIVATE_KEY', ''))
        has_public_key = bool(getattr(settings, 'IMAGEKIT_PUBLIC_KEY', ''))
        has_endpoint = bool(getattr(settings, 'IMAGEKIT_URL_ENDPOINT', ''))
        
        self.stdout.write(f"IMAGEKIT_PRIVATE_KEY: {'***SET***' if has_private_key else 'NOT SET'}")
        self.stdout.write(f"IMAGEKIT_PUBLIC_KEY: {'***SET***' if has_public_key else 'NOT SET'}")
        self.stdout.write(f"IMAGEKIT_URL_ENDPOINT: {getattr(settings, 'IMAGEKIT_URL_ENDPOINT', 'NOT SET')}")
        
        # Check STORAGES (Django 4.2+)
        storages_config = getattr(settings, 'STORAGES', {})
        if storages_config:
            default_backend = storages_config.get('default', {}).get('BACKEND', 'NOT SET')
            self.stdout.write(f"STORAGES['default']['BACKEND']: {default_backend}")

    def check_storage_backend(self):
        """Step 2: Check Storage Backend"""
        self.stdout.write("\n2. Checking Storage Backend...")
        self.stdout.write("-"*80)
        
        try:
            storage_class = type(default_storage).__name__
            storage_module = type(default_storage).__module__
            
            self.stdout.write(f"Storage class: {storage_class}")
            self.stdout.write(f"Storage module: {storage_module}")
            
            # Check if using ImageKit
            is_imagekit_storage = 'imagekit' in storage_module.lower()
            if is_imagekit_storage:
                self.stdout.write(self.style.SUCCESS("✓ Using ImageKit storage"))
                if hasattr(default_storage, 'client'):
                    self.stdout.write(self.style.SUCCESS("✓ ImageKit client initialized"))
                else:
                    self.stdout.write(self.style.ERROR("✗ ImageKit client NOT initialized"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ Using {storage_class} (not ImageKit)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Storage backend error: {e}"))

    def test_image_optimization(self):
        """Step 3: Test Image Optimization"""
        self.stdout.write("\n3. Testing Image Optimization...")
        self.stdout.write("-"*80)
        
        try:
            from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
            
            # Create test image
            img = PILImage.new('RGB', (100, 100), color='blue')
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG')
            image_bytes = img_io.getvalue()
            
            self.stdout.write(f"Created test image: {len(image_bytes)} bytes")
            
            # Test main image optimization
            self.stdout.write("  → Testing WEBP optimization...")
            main_image = ImageSerializer.optimize_image_from_bytes(
                image_bytes, 'test.jpg', max_size_kb=200, format='WEBP', max_dimension=800
            )
            main_content = main_image.read()
            self.stdout.write(f"  ✓ Main image: {len(main_content)} bytes")
            
            # Test thumbnail optimization
            self.stdout.write("  → Testing PNG thumbnail...")
            thumbnail = ImageSerializer.optimize_image_from_bytes(
                image_bytes, 'test.jpg', max_size_kb=10, format='png', max_dimension=50
            )
            thumb_content = thumbnail.read()
            self.stdout.write(f"  ✓ Thumbnail: {len(thumb_content)} bytes")
            
            self.stdout.write(self.style.SUCCESS("✓ Image optimization works correctly"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Image optimization failed: {e}"))
            import traceback
            traceback.print_exc()

    def test_storage_upload(self):
        """Step 4: Test Storage Upload"""
        self.stdout.write("\n4. Testing Storage Upload...")
        self.stdout.write("-"*80)
        
        try:
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
            
            self.stdout.write(f"Created test file: {test_file.size} bytes")
            
            # Try to save
            self.stdout.write("  → Uploading to storage...")
            saved_path = default_storage.save('diagnostic/test_upload.jpg', test_file)
            self.stdout.write(f"  ✓ Saved to: {saved_path}")
            
            # Get URL
            url = default_storage.url(saved_path)
            self.stdout.write(f"  ✓ URL: {url}")
            
            # Cleanup
            self.stdout.write("  → Cleaning up...")
            default_storage.delete(saved_path)
            self.stdout.write("  ✓ Test file deleted")
            
            self.stdout.write(self.style.SUCCESS("✓ Storage upload works correctly"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Storage upload failed: {e}"))
            import traceback
            traceback.print_exc()

    def test_serializer_flow(self):
        """Step 5: Test Full Serializer Flow"""
        self.stdout.write("\n5. Testing Full Serializer Flow...")
        self.stdout.write("-"*80)
        
        try:
            from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
            from nxtbn.users.models import User
            
            # Get a user
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.ERROR("✗ No users found in database"))
                return
                
            self.stdout.write(f"Using user: {user.email}")
            
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
            self.stdout.write("  → Validating serializer...")
            serializer = ImageSerializer(
                data={
                    'name': 'Diagnostic Test Image',
                    'image': test_file,
                    'image_alt_text': 'Diagnostic test'
                },
                context={'request': MockRequest(user)}
            )
            
            if serializer.is_valid():
                self.stdout.write("  ✓ Serializer validation passed")
                
                self.stdout.write("  → Saving image...")
                image = serializer.save()
                
                self.stdout.write(f"  ✓ Image saved with ID: {image.id}")
                self.stdout.write(f"  ✓ Main image: {image.image}")
                if image.image_xs:
                    self.stdout.write(f"  ✓ Thumbnail: {image.image_xs}")
                
                self.stdout.write(self.style.SUCCESS("✓ Full serializer flow works correctly"))
                
                # Cleanup
                self.stdout.write("  → Cleaning up test image...")
                image.delete()
                self.stdout.write("  ✓ Test image deleted")
                
            else:
                self.stdout.write(self.style.ERROR(f"✗ Serializer validation failed: {serializer.errors}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Serializer flow failed: {e}"))
            import traceback
            traceback.print_exc()

    def print_summary(self):
        """Print diagnostic summary"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write("DIAGNOSTIC COMPLETE")
        self.stdout.write("="*80)
        self.stdout.write("")
        self.stdout.write("If all steps passed (✓), the image upload system is working correctly.")
        self.stdout.write("If any step failed (✗), check the error messages above.")
        self.stdout.write("")
        self.stdout.write("Common issues:")
        self.stdout.write("  - ImageKit credentials not set → Check environment variables")
        self.stdout.write("  - Storage upload fails → Check network connectivity to ImageKit")
        self.stdout.write("  - Serializer fails → Check the detailed error traceback")
        self.stdout.write("")
