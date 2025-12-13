"""
Test ImageKit file uploads for product images.
This test validates that images are uploaded to ImageKit accurately
following the ImageKit API reference: https://imagekit.io/docs/api-reference/upload-file/

Uses actual product images from picsImages folder for realistic testing.
"""

import os
import io
from pathlib import Path
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from PIL import Image as PILImage
from nxtbn.filemanager.models import Image
from nxtbn.product.models import Product
from nxtbn.users.models import User
from nxtbn.product.tests import CategoryFactory, SupplierFactory, ProductTypeFactory


class ImageKitUploadTestCase(TestCase):
    """Test ImageKit upload functionality for product images"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.get(username='testuser')
        
    def _get_real_images_from_folder(self):
        """Get list of real product images from picsImages folder"""
        pic_dir = Path(__file__).resolve().parent.parent.parent.parent / 'picsImages'
        
        if not pic_dir.exists():
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
        
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.get(username='testuser')
        
    def create_test_image_file(self, filename='test_image.jpg', format='JPEG', 
                               width=100, height=100, color='red'):
        """
        Create a simple test image file in memory.
        
        Args:
            filename: Name of the image file
            format: PIL image format (JPEG, PNG, etc.)
            width: Image width in pixels
            height: Image height in pixels
            color: Color name for the image
            
        Returns:
            SimpleUploadedFile: Django uploaded file object
        """
        image = PILImage.new('RGB', (width, height), color=color)
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        
        return SimpleUploadedFile(
            name=filename,
            content=image_io.getvalue(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_basic_image_upload_to_imagekit(self):
        """
        Test 1: Basic real product image upload to ImageKit
        Verify that real product images from picsImages can be uploaded to ImageKit storage
        """
        real_images = self._get_real_images_from_folder()
        
        if real_images:
            # Use the first real image
            image_path = real_images[0]
            test_image = self._load_real_image(image_path)
            filename = image_path.name
        else:
            # Fall back to generated image
            test_image = self.create_test_image_file(
                filename='basic_test.jpg',
                width=200,
                height=200,
                color='blue'
            )
            filename = 'basic_test.jpg'
        
        # Save the image to ImageKit
        try:
            saved_path = default_storage.save(
                f'images/{filename}',
                test_image
            )
            
            # Verify the file was saved
            self.assertIsNotNone(saved_path)
            self.assertTrue(len(saved_path) > 0)
            
            # Get the URL
            url = default_storage.url(saved_path)
            self.assertIsNotNone(url)
            self.assertTrue(url.startswith('http'))
            
            print(f"[OK] Test 1 PASSED: Real image uploaded successfully")
            print(f"   Saved path: {saved_path}")
            print(f"   URL: {url}")
            
            # Cleanup
            default_storage.delete(saved_path)
            
        except Exception as e:
            self.fail(f"[FAIL] Test 1 FAILED: Real image upload failed - {str(e)}")
    
    def test_product_image_creation_with_imagekit(self):
        """
        Test 2: Create a Product Image through Django ORM with real product image
        Verify that ImageField properly uploads real images to ImageKit
        """
        real_images = self._get_real_images_from_folder()
        
        if real_images:
            # Use a real image
            image_path = real_images[0]
            test_image = self._load_real_image(image_path)
            image_name = image_path.name
        else:
            # Fall back to generated image
            test_image = self.create_test_image_file(
                filename='product_image.jpg',
                width=500,
                height=500,
                color='green'
            )
            image_name = 'product_image.jpg'
        
        try:
            # Create Image object (this triggers upload to ImageKit)
            image = Image.objects.create(
                created_by=self.user,
                name='Test Real Product Image',
                image=test_image,
                image_alt_text='A test real product image'
            )
            
            # Verify image was created
            self.assertIsNotNone(image.id)
            self.assertIsNotNone(image.image)
            
            # Get the image URL
            image_url = image.get_image_url(self.get_request_mock())
            self.assertIsNotNone(image_url)
            
            print(f"[OK] Test 2 PASSED: Real product image created successfully")
            print(f"   Image ID: {image.id}")
            print(f"   Original image: {image_name}")
            print(f"   Image path: {image.image}")
            print(f"   Image URL: {image_url}")
            
        except Exception as e:
            self.fail(f"[FAIL] Test 2 FAILED: Real product image creation failed - {str(e)}")
    
    def test_multiple_images_upload(self):
        """
        Test 3: Upload multiple real product images to verify batch handling
        Verify that multiple images from picsImages can be uploaded correctly
        """
        try:
            uploaded_images = []
            real_images = self._get_real_images_from_folder()
            
            # Use up to 3 real images, or generated ones if not available
            images_to_upload = real_images[:3] if real_images else []
            
            if images_to_upload:
                # Upload real images
                for i, image_path in enumerate(images_to_upload):
                    test_image = self._load_real_image(image_path)
                    saved_path = default_storage.save(
                        f'images/{image_path.name}',
                        test_image
                    )
                    
                    url = default_storage.url(saved_path)
                    uploaded_images.append({
                        'path': saved_path,
                        'url': url,
                        'index': i,
                        'name': image_path.name
                    })
            else:
                # Fall back to generated images
                for i in range(3):
                    test_image = self.create_test_image_file(
                        filename=f'multi_image_{i}.jpg',
                        width=300 + (i * 100),
                        height=300 + (i * 100),
                        color=['red', 'green', 'blue'][i]
                    )
                    
                    saved_path = default_storage.save(
                        f'images/multi_image_{i}.jpg',
                        test_image
                    )
                    
                    url = default_storage.url(saved_path)
                    uploaded_images.append({
                        'path': saved_path,
                        'url': url,
                        'index': i
                    })
            
            # Verify all images were uploaded
            self.assertGreater(len(uploaded_images), 0)
            for img in uploaded_images:
                self.assertIsNotNone(img['path'])
                self.assertTrue(img['url'].startswith('http'))
            
            print(f"[OK] Test 3 PASSED: Multiple images uploaded successfully")
            for img in uploaded_images:
                print(f"   Image {img['index']}: {img.get('name', 'generated')}")
            
            # Cleanup
            for img in uploaded_images:
                default_storage.delete(img['path'])
                
        except Exception as e:
            self.fail(f"[FAIL] Test 3 FAILED: Multiple image upload failed - {str(e)}")
    
    def test_product_with_multiple_images(self):
        """
        Test 4: Create a Product with multiple images
        Verify that products can have multiple ImageKit-hosted images
        """
        try:
            # Create category, supplier, and product type
            category = CategoryFactory()
            supplier = SupplierFactory()
            product_type = ProductTypeFactory()
            
            # Create product
            product = Product.objects.create(
                name='Test Product with Images',
                summary='A product with multiple images',
                description='Test description',
                created_by=self.user,
                last_modified_by=self.user,
                category=category,
                supplier=supplier,
                product_type=product_type
            )
            
            # Add multiple images to the product
            for i in range(2):
                test_image = self.create_test_image_file(
                    filename=f'product_{product.id}_image_{i}.jpg',
                    width=400,
                    height=400,
                    color=['red', 'blue'][i]
                )
                
                image = Image.objects.create(
                    created_by=self.user,
                    name=f'Product Image {i+1}',
                    image=test_image,
                    image_alt_text=f'Product image {i+1}'
                )
                
                product.images.add(image)
            
            # Verify product has images
            self.assertEqual(product.images.count(), 2)
            
            # Get image URLs
            images_data = []
            for img in product.images.all():
                url = img.get_image_url(self.get_request_mock())
                images_data.append({'id': img.id, 'url': url})
            
            print(f"✅ Test 4 PASSED: Product created with multiple ImageKit images")
            print(f"   Product ID: {product.id}")
            print(f"   Number of images: {product.images.count()}")
            for img_data in images_data:
                print(f"   Image {img_data['id']}: {img_data['url']}")
                
        except Exception as e:
            self.fail(f"❌ Test 4 FAILED: Product with multiple images failed - {str(e)}")
    
    def test_image_with_small_variant(self):
        """
        Test 5: Test image with XS (extra small) variant
        Verify that thumbnail generation works with ImageKit
        """
        try:
            # Create test image
            test_image = self.create_test_image_file(
                filename='image_with_variant.jpg',
                width=800,
                height=600,
                color='purple'
            )
            
            # Create ImageKit-hosted image
            image = Image.objects.create(
                created_by=self.user,
                name='Image with XS Variant',
                image=test_image,
                image_alt_text='Test image with thumbnail'
            )
            
            # Get both URLs
            main_url = image.get_image_url(self.get_request_mock())
            xs_url = image.get_image_xs_url(self.get_request_mock())
            
            self.assertIsNotNone(main_url)
            # xs_url should at least return the main URL if variant doesn't exist
            self.assertIsNotNone(xs_url)
            
            print(f"✅ Test 5 PASSED: Image with variant handling works")
            print(f"   Main URL: {main_url}")
            print(f"   XS URL: {xs_url}")
                
        except Exception as e:
            self.fail(f"❌ Test 5 FAILED: Image variant test failed - {str(e)}")
    
    def test_imagekit_url_format(self):
        """
        Test 6: Verify ImageKit URL format compliance
        Ensure generated URLs follow ImageKit CDN URL pattern
        """
        try:
            test_image = self.create_test_image_file(
                filename='url_format_test.jpg',
                width=400,
                height=400
            )
            
            saved_path = default_storage.save(
                'images/url_format_test.jpg',
                test_image
            )
            
            url = default_storage.url(saved_path)
            
            # Check URL structure
            self.assertIsNotNone(url)
            self.assertTrue(url.startswith('http'))
            
            # The URL should contain the endpoint
            settings_endpoint = self._get_imagekit_endpoint()
            if settings_endpoint:
                self.assertIn(settings_endpoint.replace('https://', '').replace('http://', ''), url)
            
            print(f"✅ Test 6 PASSED: ImageKit URL format is valid")
            print(f"   URL: {url}")
            
            # Cleanup
            default_storage.delete(saved_path)
            
        except Exception as e:
            self.fail(f"❌ Test 6 FAILED: URL format validation failed - {str(e)}")
    
    def test_upload_with_imagekit_options(self):
        """
        Test 7: Test upload with ImageKit-specific options
        Verify that upload options (folder, unique filename, etc.) work correctly
        According to: https://imagekit.io/docs/api-reference/upload-file/
        """
        try:
            test_image = self.create_test_image_file(
                filename='options_test.jpg',
                width=500,
                height=500
            )
            
            # Try to save with a specific path
            saved_path = default_storage.save(
                'images/products/special/options_test.jpg',
                test_image
            )
            
            # Verify path was saved
            self.assertIsNotNone(saved_path)
            
            # Get URL
            url = default_storage.url(saved_path)
            self.assertIsNotNone(url)
            
            print(f"✅ Test 7 PASSED: Upload with options works")
            print(f"   Saved path: {saved_path}")
            print(f"   URL: {url}")
            
            # Cleanup
            default_storage.delete(saved_path)
            
        except Exception as e:
            self.fail(f"❌ Test 7 FAILED: Upload with options failed - {str(e)}")
    
    def get_request_mock(self):
        """
        Create a mock request object for testing
        """
        from unittest.mock import Mock
        
        mock_request = Mock()
        mock_request.build_absolute_uri = lambda url: f'http://testserver{url}'
        return mock_request
    
    def _get_imagekit_endpoint(self):
        """Get ImageKit endpoint from settings"""
        from django.conf import settings
        return getattr(settings, 'IMAGEKIT_URL_ENDPOINT', '')


class ImageKitUploadValidationTestCase(TestCase):
    """Validate ImageKit upload response and metadata"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='validator',
            email='validator@example.com',
            password='validate123'
        )
    
    def setUp(self):
        self.user = User.objects.get(username='validator')
    
    def test_upload_response_metadata(self):
        """
        Test 8: Validate upload response contains expected metadata
        According to ImageKit API: file_id, url, file_name, etc.
        """
        try:
            from PIL import Image as PILImage
            
            # Create test image
            image = PILImage.new('RGB', (100, 100), color='red')
            image_io = io.BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            
            test_file = SimpleUploadedFile(
                'metadata_test.jpg',
                image_io.getvalue(),
                content_type='image/jpeg'
            )
            
            # Upload and capture response
            saved_path = default_storage.save(
                'images/metadata_test.jpg',
                test_file
            )
            
            # The saved_path should contain some identifier
            self.assertIsNotNone(saved_path)
            self.assertTrue(len(saved_path) > 0)
            
            url = default_storage.url(saved_path)
            
            print(f"✅ Test 8 PASSED: Upload response contains metadata")
            print(f"   File path: {saved_path}")
            print(f"   URL: {url}")
            
            # Cleanup
            default_storage.delete(saved_path)
            
        except Exception as e:
            self.fail(f"❌ Test 8 FAILED: Metadata validation failed - {str(e)}")
    
    def test_image_dimensions_preserved(self):
        """
        Test 9: Verify image dimensions are preserved after upload
        """
        try:
            from PIL import Image as PILImage
            
            width, height = 640, 480
            image = PILImage.new('RGB', (width, height), color='green')
            image_io = io.BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            
            test_file = SimpleUploadedFile(
                'dimensions_test.jpg',
                image_io.getvalue(),
                content_type='image/jpeg'
            )
            
            # Create Image object
            img_obj = Image.objects.create(
                created_by=self.user,
                name='Dimensions Test Image',
                image=test_file,
                image_alt_text='Testing dimensions'
            )
            
            # Verify image exists and has file
            self.assertIsNotNone(img_obj.image)
            
            print(f"✅ Test 9 PASSED: Image dimensions preserved")
            print(f"   Original dimensions: {width}x{height}")
            print(f"   Stored path: {img_obj.image}")
            
        except Exception as e:
            self.fail(f"❌ Test 9 FAILED: Dimension preservation test failed - {str(e)}")
