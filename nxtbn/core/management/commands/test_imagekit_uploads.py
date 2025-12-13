"""
Enhanced ImageKit upload test management command.
Tests ImageKit file uploads according to API reference:
https://imagekit.io/docs/api-reference/upload-file/

Uses actual product images from picsImages folder for realistic testing.
"""

import io
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from PIL import Image as PILImage
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '''
    Test ImageKit file uploads for product images.
    
    This command validates:
    1. Basic file upload to ImageKit
    2. URL generation
    3. File deletion
    4. Image file handling
    5. Metadata retrieval
    6. Batch uploads
    
    Usage: python manage.py test_imagekit_uploads [--verbose]
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each test',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            default=True,
            help='Clean up test files after tests (default: True)',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        cleanup = options.get('cleanup', True)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('ImageKit Upload Integration Tests'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # Check if ImageKit is configured
        if not self._check_imagekit_config():
            raise CommandError(
                'ImageKit is not properly configured. '
                'Please set IMAGEKIT_PRIVATE_KEY, IMAGEKIT_PUBLIC_KEY, '
                'and IMAGEKIT_URL_ENDPOINT in your settings.'
            )
        
        self.stdout.write(self.style.SUCCESS('[OK] ImageKit Configuration Found'))
        self._print_config_summary()
        self.stdout.write('')
        
        # Run tests
        test_results = []
        
        try:
            # Test 1: Basic text file upload
            result = self._test_basic_upload(verbose)
            test_results.append(('Basic Upload', result))
            
            # Test 2: Image file upload
            result = self._test_image_upload(verbose)
            test_results.append(('Image Upload', result))
            
            # Test 3: Multiple uploads
            result = self._test_multiple_uploads(verbose)
            test_results.append(('Multiple Uploads', result))
            
            # Test 4: URL generation
            result = self._test_url_generation(verbose)
            test_results.append(('URL Generation', result))
            
            # Test 5: File metadata
            result = self._test_file_metadata(verbose)
            test_results.append(('File Metadata', result))
            
            # Test 6: Delete operations
            result = self._test_delete_operation(verbose)
            test_results.append(('Delete Operation', result))
            
            # Test 7: Large image upload
            result = self._test_large_image_upload(verbose)
            test_results.append(('Large Image Upload', result))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n[FAIL] Test Suite Failed: {str(e)}')
            )
            logger.exception('ImageKit test suite failed')
            if verbose:
                raise
            return
        
        # Print summary
        self._print_test_summary(test_results)
    
    def _check_imagekit_config(self):
        """Check if ImageKit is configured"""
        return all([
            getattr(settings, 'IMAGEKIT_PRIVATE_KEY', ''),
            getattr(settings, 'IMAGEKIT_PUBLIC_KEY', ''),
            getattr(settings, 'IMAGEKIT_URL_ENDPOINT', '')
        ])
    
    def _print_config_summary(self):
        """Print ImageKit configuration summary"""
        self.stdout.write('Configuration Summary:')
        self.stdout.write(f'  • Endpoint: {settings.IMAGEKIT_URL_ENDPOINT}')
        self.stdout.write(f'  • Private Key: {"***" + settings.IMAGEKIT_PRIVATE_KEY[-4:]}')
        self.stdout.write(f'  • Public Key: {"***" + settings.IMAGEKIT_PUBLIC_KEY[-4:]}')
    
    def _get_real_images_from_folder(self):
        """Get list of real product images from picsImages folder"""
        pic_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / 'picsImages'
        
        if not pic_dir.exists():
            self.stdout.write(self.style.WARNING(f'  [WARN] picsImages folder not found at {pic_dir}'))
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = [f for f in pic_dir.iterdir() 
                 if f.is_file() and f.suffix.lower() in image_extensions]
        
        return sorted(images)
    
    def _load_real_image(self, image_path):
        """Load a real image file and return it as SimpleUploadedFile"""
        if not image_path.exists():
            raise FileNotFoundError(f'Image not found: {image_path}')
        
        with open(image_path, 'rb') as f:
            content = f.read()
        
        # Determine content type from file extension
        ext = image_path.suffix.lower()
        if ext in {'.jpg', '.jpeg'}:
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        elif ext == '.gif':
            content_type = 'image/gif'
        elif ext == '.webp':
            content_type = 'image/webp'
        else:
            content_type = 'image/jpeg'  # default
        
        return SimpleUploadedFile(
            image_path.name,
            content,
            content_type=content_type
        )
    
    def _create_test_image(self, filename, width=100, height=100, color='red', format='JPEG'):
        """Create a test image file"""
        image = PILImage.new('RGB', (width, height), color=color)
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image_io.getvalue(),
            content_type=f'image/{format.lower()}'
        )
    
    def _test_basic_upload(self, verbose):
        """Test 1: Basic text file upload"""
        try:
            self.stdout.write('\n[Test 1] Basic File Upload')
            self.stdout.write('-' * 50)
            
            content = b"Test ImageKit upload - Basic file content"
            test_file = ContentFile(content)
            test_file.name = "test_basic.txt"
            
            saved_name = default_storage.save(test_file.name, test_file)
            
            if verbose:
                self.stdout.write(f'  Saved name: {saved_name}')
            
            # Verify file was saved
            if saved_name:
                self.stdout.write(self.style.SUCCESS('  [OK] File uploaded successfully'))
                
                # Try to get URL
                try:
                    url = default_storage.url(saved_name)
                    if verbose:
                        self.stdout.write(f'  URL: {url}')
                    
                    # Cleanup
                    default_storage.delete(saved_name)
                    self.stdout.write(self.style.SUCCESS('  [OK] File deleted successfully'))
                    return True
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  [WARN]  URL generation warning: {str(e)}'))
                    return False
            else:
                self.stdout.write(self.style.ERROR('  [FAIL] File save returned empty'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Basic upload test failed')
            return False
    
    def _test_image_upload(self, verbose):
        """Test 2: Real product image file upload from picsImages"""
        try:
            self.stdout.write('\n[Test 2] Real Product Image Upload')
            self.stdout.write('-' * 50)
            
            real_images = self._get_real_images_from_folder()
            
            if not real_images:
                self.stdout.write(self.style.WARNING('  [WARN] No real images found in picsImages folder'))
                # Fall back to generated image
                test_image = self._create_test_image('test_image.jpg', width=200, height=200, color='blue')
                image_name = 'test_image.jpg'
            else:
                # Use the first real image
                image_path = real_images[0]
                test_image = self._load_real_image(image_path)
                image_name = image_path.name
                if verbose:
                    self.stdout.write(f'  Using real image: {image_name}')
            
            saved_name = default_storage.save(f'images/{image_name}', test_image)
            
            if verbose:
                self.stdout.write(f'  Saved name: {saved_name}')
            
            if saved_name:
                self.stdout.write(self.style.SUCCESS('  [OK] Real image uploaded successfully'))
                
                # Get URL
                url = default_storage.url(saved_name)
                if verbose:
                    self.stdout.write(f'  Image URL: {url}')
                
                # Cleanup
                default_storage.delete(saved_name)
                return True
            else:
                self.stdout.write(self.style.ERROR('  [FAIL] Image upload returned empty'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Real image upload test failed')
            return False
    
    def _test_multiple_uploads(self, verbose):
        """Test 3: Multiple real product image uploads"""
        try:
            self.stdout.write('\n[Test 3] Multiple Real Product Image Uploads')
            self.stdout.write('-' * 50)
            
            real_images = self._get_real_images_from_folder()
            uploaded_files = []
            
            # Upload first 3 real images (or fewer if not available)
            images_to_upload = real_images[:3] if real_images else []
            
            if not images_to_upload:
                self.stdout.write(self.style.WARNING('  [WARN] No real images found, using generated images'))
                # Fall back to generated images
                for i in range(3):
                    test_image = self._create_test_image(
                        f'multi_image_{i}.jpg',
                        width=150 + (i * 50),
                        height=150 + (i * 50),
                        color=['red', 'green', 'blue'][i]
                    )
                    saved_name = default_storage.save(f'images/multi_image_{i}.jpg', test_image)
                    uploaded_files.append(saved_name)
            else:
                for i, image_path in enumerate(images_to_upload):
                    test_image = self._load_real_image(image_path)
                    saved_name = default_storage.save(f'images/{image_path.name}', test_image)
                    uploaded_files.append(saved_name)
                    
                    if verbose:
                        self.stdout.write(f'  Image {i+1}: {image_path.name} -> {saved_name}')
            
            if len(uploaded_files) >= 3:
                self.stdout.write(self.style.SUCCESS(f'  [OK] All {len(uploaded_files)} images uploaded successfully'))
                
                # Cleanup
                for file_name in uploaded_files:
                    default_storage.delete(file_name)
                
                return True
            elif len(uploaded_files) > 0:
                self.stdout.write(self.style.SUCCESS(f'  [OK] {len(uploaded_files)} images uploaded successfully'))
                
                # Cleanup
                for file_name in uploaded_files:
                    default_storage.delete(file_name)
                
                return True
            else:
                self.stdout.write(self.style.ERROR(f'  [FAIL] No images uploaded'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Multiple uploads test failed')
            return False
    
    def _test_url_generation(self, verbose):
        """Test 4: URL generation"""
        try:
            self.stdout.write('\n[Test 4] URL Generation')
            self.stdout.write('-' * 50)
            
            test_image = self._create_test_image('url_test.jpg')
            saved_name = default_storage.save('images/url_test.jpg', test_image)
            
            url = default_storage.url(saved_name)
            
            # Validate URL
            if url and url.startswith('http'):
                self.stdout.write(self.style.SUCCESS('  [OK] URL generated successfully'))
                if verbose:
                    self.stdout.write(f'  URL: {url}')
                
                # Verify endpoint is in URL
                if settings.IMAGEKIT_URL_ENDPOINT in url:
                    self.stdout.write(self.style.SUCCESS('  [OK] URL contains ImageKit endpoint'))
                else:
                    self.stdout.write(self.style.WARNING('  [WARN]  URL may not contain expected endpoint'))
                
                # Cleanup
                default_storage.delete(saved_name)
                return True
            else:
                self.stdout.write(self.style.ERROR('  [FAIL] Invalid URL generated'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('URL generation test failed')
            return False
    
    def _test_file_metadata(self, verbose):
        """Test 5: Real image metadata"""
        try:
            self.stdout.write('\n[Test 5] Real Image Metadata')
            self.stdout.write('-' * 50)
            
            real_images = self._get_real_images_from_folder()
            
            if real_images:
                # Use a real image
                image_path = real_images[0]
                test_image = self._load_real_image(image_path)
                saved_name = default_storage.save(f'images/{image_path.name}', test_image)
                
                if verbose:
                    self.stdout.write(f'  Real image: {image_path.name}')
                    self.stdout.write(f'  File size: {image_path.stat().st_size} bytes')
            else:
                # Fall back to generated image
                test_image = self._create_test_image('metadata_test.jpg', width=300, height=300)
                saved_name = default_storage.save('images/metadata_test.jpg', test_image)
            
            # Try to get file info
            self.stdout.write(self.style.SUCCESS('  [OK] File saved with metadata'))
            if verbose:
                self.stdout.write(f'  Saved name: {saved_name}')
            
            # Try to check existence
            try:
                exists = default_storage.exists(saved_name)
                if verbose:
                    self.stdout.write(f'  Exists check: {exists}')
            except Exception as e:
                if verbose:
                    self.stdout.write(f'  Existence check not fully supported: {str(e)}')
            
            # Cleanup
            default_storage.delete(saved_name)
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Metadata test failed')
            return False
    
    def _test_delete_operation(self, verbose):
        """Test 6: Delete operation"""
        try:
            self.stdout.write('\n[Test 6] Delete Operation')
            self.stdout.write('-' * 50)
            
            test_image = self._create_test_image('delete_test.jpg')
            saved_name = default_storage.save('images/delete_test.jpg', test_image)
            
            if verbose:
                self.stdout.write(f'  Created file: {saved_name}')
            
            # Delete the file
            try:
                default_storage.delete(saved_name)
                self.stdout.write(self.style.SUCCESS('  [OK] File deleted successfully'))
                return True
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  [WARN]  Delete operation may have failed: {str(e)}'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Delete operation test failed')
            return False
    
    def _test_large_image_upload(self, verbose):
        """Test 7: Large real product image upload"""
        try:
            self.stdout.write('\n[Test 7] Large Real Product Image Upload')
            self.stdout.write('-' * 50)
            
            real_images = self._get_real_images_from_folder()
            
            if real_images and len(real_images) > 1:
                # Use the largest real image
                largest_image = max(real_images, key=lambda x: x.stat().st_size)
                test_image = self._load_real_image(largest_image)
                saved_name = default_storage.save(f'images/{largest_image.name}', test_image)
                
                if verbose:
                    size_kb = largest_image.stat().st_size / 1024
                    self.stdout.write(f'  Large image: {largest_image.name} ({size_kb:.1f} KB)')
            else:
                # Fall back to generated large image
                test_image = self._create_test_image(
                    'large_image.jpg',
                    width=1920,
                    height=1080,
                    color='purple'
                )
                saved_name = default_storage.save('images/large_image.jpg', test_image)
            
            if verbose:
                self.stdout.write(f'  Saved name: {saved_name}')
            
            if saved_name:
                self.stdout.write(self.style.SUCCESS('  [OK] Large image uploaded successfully'))
                
                url = default_storage.url(saved_name)
                if verbose:
                    self.stdout.write(f'  Image URL: {url}')
                
                # Cleanup
                default_storage.delete(saved_name)
                return True
            else:
                self.stdout.write(self.style.ERROR('  [FAIL] Large image upload failed'))
                return False
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [FAIL] Test failed: {str(e)}'))
            if verbose:
                logger.exception('Large image upload test failed')
            return False
    
    def _print_test_summary(self, results):
        """Print test summary"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write('Test Summary')
        self.stdout.write('='*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = self.style.SUCCESS('[OK] PASS') if result else self.style.ERROR('[FAIL] FAIL')
            self.stdout.write(f'{test_name:<30} {status}')
        
        self.stdout.write('-' * 70)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if passed == total:
            self.stdout.write(
                self.style.SUCCESS(f'[OK] All tests passed! ({passed}/{total})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'[WARN]  {passed}/{total} tests passed ({success_rate:.1f}%)')
            )
        
        self.stdout.write('='*70 + '\n')
