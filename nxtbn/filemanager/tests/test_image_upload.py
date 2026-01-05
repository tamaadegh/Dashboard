"""
Comprehensive tests for filemanager image upload functionality.
Tests the ImageSerializer with the new optimize_image_from_bytes method.
"""

import io
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from PIL import Image as PILImage
from rest_framework.test import APIRequestFactory

from nxtbn.filemanager.models import Image
from nxtbn.filemanager.api.dashboard.serializers import ImageSerializer
from nxtbn.users.models import User


class ImageSerializerTestCase(TestCase):
    """Test the ImageSerializer with new file handling logic"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.get(username='testuser')
        self.factory = APIRequestFactory()
    
    def create_test_image(self, filename='test.jpg', width=800, height=600, color='red', format='JPEG'):
        """Create a test image in memory"""
        img = PILImage.new('RGB', (width, height), color=color)
        img_io = io.BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        
        return SimpleUploadedFile(
            name=filename,
            content=img_io.getvalue(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_optimize_image_from_bytes_webp(self):
        """
        Test 1: Test optimize_image_from_bytes with WEBP format
        Verify that the method correctly creates a WEBP image from bytes
        """
        print("\n" + "="*80)
        print("TEST 1: optimize_image_from_bytes - WEBP format")
        print("="*80)
        
        # Create test image bytes
        img = PILImage.new('RGB', (800, 600), color='blue')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        image_bytes = img_io.getvalue()
        
        print(f"✓ Created test image: {len(image_bytes)} bytes")
        
        # Test the optimization method
        try:
            optimized = ImageSerializer.optimize_image_from_bytes(
                image_bytes,
                'test_image.jpg',
                max_size_kb=200,
                format='WEBP',
                max_dimension=800
            )
            
            self.assertIsNotNone(optimized)
            self.assertTrue(optimized.name.endswith('.webp'))
            
            # Read the optimized content
            optimized_content = optimized.read()
            self.assertGreater(len(optimized_content), 0)
            self.assertLess(len(optimized_content), 200 * 1024)  # Should be under 200KB
            
            print(f"✓ Optimized image created: {optimized.name}")
            print(f"✓ Size: {len(optimized_content)} bytes ({len(optimized_content)/1024:.1f}KB)")
            print("✅ TEST 1 PASSED\n")
            
        except Exception as e:
            print(f"❌ TEST 1 FAILED: {str(e)}\n")
            raise
    
    def test_optimize_image_from_bytes_png_thumbnail(self):
        """
        Test 2: Test optimize_image_from_bytes with PNG thumbnail
        Verify that small PNG thumbnails are created correctly
        """
        print("="*80)
        print("TEST 2: optimize_image_from_bytes - PNG thumbnail")
        print("="*80)
        
        # Create test image bytes
        img = PILImage.new('RGB', (1920, 1080), color='green')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        image_bytes = img_io.getvalue()
        
        print(f"✓ Created large test image: {len(image_bytes)} bytes")
        
        try:
            # Create small PNG thumbnail
            thumbnail = ImageSerializer.optimize_image_from_bytes(
                image_bytes,
                'large_image.jpg',
                max_size_kb=10,
                format='png',
                max_dimension=50
            )
            
            self.assertIsNotNone(thumbnail)
            self.assertTrue(thumbnail.name.endswith('.png'))
            
            # Read and verify size
            thumb_content = thumbnail.read()
            self.assertGreater(len(thumb_content), 0)
            self.assertLess(len(thumb_content), 15 * 1024)  # Should be under 15KB
            
            print(f"✓ Thumbnail created: {thumbnail.name}")
            print(f"✓ Size: {len(thumb_content)} bytes ({len(thumb_content)/1024:.1f}KB)")
            print("✅ TEST 2 PASSED\n")
            
        except Exception as e:
            print(f"❌ TEST 2 FAILED: {str(e)}\n")
            raise
    
    def test_optimize_image_from_bytes_multiple_calls(self):
        """
        Test 3: Test calling optimize_image_from_bytes multiple times with same bytes
        This is the core fix - verify we can process the same bytes twice
        """
        print("="*80)
        print("TEST 3: Multiple calls with same bytes (CRITICAL FIX TEST)")
        print("="*80)
        
        # Create test image bytes
        img = PILImage.new('RGB', (1024, 768), color='purple')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        image_bytes = img_io.getvalue()
        
        print(f"✓ Created test image: {len(image_bytes)} bytes")
        
        try:
            # First call - create main image
            print("  → Creating main image (WEBP)...")
            main_image = ImageSerializer.optimize_image_from_bytes(
                image_bytes,
                'test.jpg',
                max_size_kb=200,
                format='WEBP',
                max_dimension=800
            )
            
            self.assertIsNotNone(main_image)
            main_content = main_image.read()
            print(f"  ✓ Main image: {len(main_content)} bytes")
            
            # Second call - create thumbnail from SAME bytes
            print("  → Creating thumbnail (PNG) from same bytes...")
            thumbnail = ImageSerializer.optimize_image_from_bytes(
                image_bytes,  # Same bytes!
                'test.jpg',
                max_size_kb=10,
                format='png',
                max_dimension=50
            )
            
            self.assertIsNotNone(thumbnail)
            thumb_content = thumbnail.read()
            print(f"  ✓ Thumbnail: {len(thumb_content)} bytes")
            
            # Verify both were created successfully
            self.assertGreater(len(main_content), 0)
            self.assertGreater(len(thumb_content), 0)
            
            print("✅ TEST 3 PASSED - Can process same bytes multiple times!\n")
            
        except Exception as e:
            print(f"❌ TEST 3 FAILED: {str(e)}\n")
            raise
    
    def test_serializer_create_with_image(self):
        """
        Test 4: Test the full serializer create flow
        Verify that creating an Image through the serializer works end-to-end
        """
        print("="*80)
        print("TEST 4: Full serializer create flow")
        print("="*80)
        
        # Create uploaded file
        test_image = self.create_test_image(
            filename='serializer_test.jpg',
            width=1200,
            height=900,
            color='orange'
        )
        
        print(f"✓ Created uploaded file: {test_image.name}, {test_image.size} bytes")
        
        # Create mock request
        request = self.factory.post('/test/')
        request.user = self.user
        
        # Prepare data
        data = {
            'name': 'Serializer Test Image',
            'image': test_image,
            'image_alt_text': 'Test image for serializer'
        }
        
        try:
            # Create serializer and validate
            print("  → Validating serializer...")
            serializer = ImageSerializer(data=data, context={'request': request})
            
            self.assertTrue(serializer.is_valid(), f"Validation errors: {serializer.errors}")
            print("  ✓ Serializer validation passed")
            
            # Save (this triggers the create method)
            print("  → Saving image (triggers optimize_image_from_bytes)...")
            image = serializer.save()
            
            self.assertIsNotNone(image)
            self.assertIsNotNone(image.id)
            self.assertIsNotNone(image.image)
            self.assertIsNotNone(image.image_xs)
            
            print(f"  ✓ Image saved with ID: {image.id}")
            print(f"  ✓ Main image path: {image.image}")
            print(f"  ✓ Thumbnail path: {image.image_xs}")
            print("✅ TEST 4 PASSED\n")
            
        except Exception as e:
            print(f"❌ TEST 4 FAILED: {str(e)}\n")
            import traceback
            traceback.print_exc()
            raise
    
    def test_serializer_create_with_large_image(self):
        """
        Test 5: Test with a large image to verify optimization works
        """
        print("="*80)
        print("TEST 5: Large image optimization")
        print("="*80)
        
        # Create a large image
        test_image = self.create_test_image(
            filename='large_test.jpg',
            width=3840,  # 4K width
            height=2160,  # 4K height
            color='cyan'
        )
        
        print(f"✓ Created large image: {test_image.size} bytes ({test_image.size/1024/1024:.2f}MB)")
        
        # Create mock request
        request = self.factory.post('/test/')
        request.user = self.user
        
        data = {
            'name': 'Large Image Test',
            'image': test_image,
            'image_alt_text': 'Large test image'
        }
        
        try:
            serializer = ImageSerializer(data=data, context={'request': request})
            
            self.assertTrue(serializer.is_valid(), f"Validation errors: {serializer.errors}")
            print("  ✓ Validation passed")
            
            print("  → Processing large image (this may take a moment)...")
            image = serializer.save()
            
            self.assertIsNotNone(image)
            print(f"  ✓ Large image processed successfully")
            print(f"  ✓ Saved as: {image.image}")
            print("✅ TEST 5 PASSED\n")
            
        except Exception as e:
            print(f"❌ TEST 5 FAILED: {str(e)}\n")
            raise
    
    def test_serializer_handles_different_formats(self):
        """
        Test 6: Test with different image formats (JPEG, PNG)
        """
        print("="*80)
        print("TEST 6: Different image formats")
        print("="*80)
        
        formats = [
            ('test.jpg', 'JPEG', 'image/jpeg'),
            ('test.png', 'PNG', 'image/png'),
        ]
        
        request = self.factory.post('/test/')
        request.user = self.user
        
        for filename, pil_format, content_type in formats:
            print(f"\n  Testing {pil_format} format...")
            
            # Create image
            img = PILImage.new('RGB', (640, 480), color='yellow')
            img_io = io.BytesIO()
            img.save(img_io, format=pil_format)
            img_io.seek(0)
            
            test_image = SimpleUploadedFile(
                name=filename,
                content=img_io.getvalue(),
                content_type=content_type
            )
            
            data = {
                'name': f'Test {pil_format} Image',
                'image': test_image,
                'image_alt_text': f'Test {pil_format}'
            }
            
            try:
                serializer = ImageSerializer(data=data, context={'request': request})
                self.assertTrue(serializer.is_valid())
                
                image = serializer.save()
                self.assertIsNotNone(image)
                
                print(f"  ✓ {pil_format} processed successfully")
                
                # Clean up
                image.delete()
                
            except Exception as e:
                print(f"  ✗ {pil_format} failed: {str(e)}")
                raise
        
        print("\n✅ TEST 6 PASSED - All formats handled correctly\n")
    
    def test_error_handling_invalid_image(self):
        """
        Test 7: Test error handling with invalid image data
        """
        print("="*80)
        print("TEST 7: Error handling with invalid data")
        print("="*80)
        
        # Create a file that's not a valid image
        invalid_file = SimpleUploadedFile(
            name='not_an_image.jpg',
            content=b'This is not an image',
            content_type='image/jpeg'
        )
        
        request = self.factory.post('/test/')
        request.user = self.user
        
        data = {
            'name': 'Invalid Image Test',
            'image': invalid_file,
            'image_alt_text': 'Should fail'
        }
        
        try:
            serializer = ImageSerializer(data=data, context={'request': request})
            
            # Validation should pass (it's a file)
            self.assertTrue(serializer.is_valid())
            
            # But save should fail with ValidationError
            print("  → Attempting to save invalid image...")
            with self.assertRaises(Exception) as context:
                serializer.save()
            
            print(f"  ✓ Correctly raised error: {type(context.exception).__name__}")
            print("✅ TEST 7 PASSED - Invalid images are rejected\n")
            
        except AssertionError:
            # If it didn't raise an error, that's a problem
            print("❌ TEST 7 FAILED - Should have raised an error for invalid image\n")
            raise


class ImageModelIntegrationTestCase(TestCase):
    """Integration tests for Image model with storage backend"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='integration_user',
            email='integration@example.com',
            password='testpass123'
        )
    
    def setUp(self):
        self.user = User.objects.get(username='integration_user')
    
    def test_image_model_save_and_retrieve(self):
        """
        Test 8: Test full Image model save and retrieval
        """
        print("="*80)
        print("TEST 8: Image model save and retrieve")
        print("="*80)
        
        # Create test image
        img = PILImage.new('RGB', (500, 500), color='magenta')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        test_image = SimpleUploadedFile(
            name='model_test.jpg',
            content=img_io.getvalue(),
            content_type='image/jpeg'
        )
        
        try:
            # Create Image instance
            print("  → Creating Image instance...")
            image = Image.objects.create(
                created_by=self.user,
                name='Model Integration Test',
                image=test_image,
                image_alt_text='Integration test image'
            )
            
            self.assertIsNotNone(image.id)
            print(f"  ✓ Image created with ID: {image.id}")
            
            # Retrieve from database
            print("  → Retrieving from database...")
            retrieved = Image.objects.get(id=image.id)
            
            self.assertEqual(retrieved.name, 'Model Integration Test')
            self.assertIsNotNone(retrieved.image)
            
            print(f"  ✓ Retrieved image: {retrieved.name}")
            print(f"  ✓ Image path: {retrieved.image}")
            
            if retrieved.image_xs:
                print(f"  ✓ Thumbnail path: {retrieved.image_xs}")
            
            print("✅ TEST 8 PASSED\n")
            
        except Exception as e:
            print(f"❌ TEST 8 FAILED: {str(e)}\n")
            import traceback
            traceback.print_exc()
            raise


def run_all_tests():
    """Helper function to run all tests with nice output"""
    print("\n" + "="*80)
    print("FILEMANAGER IMAGE UPLOAD TEST SUITE")
    print("="*80)
    print("Testing the new optimize_image_from_bytes functionality")
    print("="*80 + "\n")
    
    import unittest
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(ImageSerializerTestCase))
    suite.addTests(loader.loadTestsFromTestCase(ImageModelIntegrationTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("="*80 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_all_tests()
