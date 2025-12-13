#!/usr/bin/env python
"""
ImageKit Upload Verification Script

This script helps verify that images are being uploaded to ImageKit correctly
by performing checks against the API.

Usage:
    python verify_imagekit.py
"""

import os
import sys
import json
from datetime import datetime

# Add Django to path
if __name__ == '__main__':
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nxtbn.settings')
    django.setup()

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from PIL import Image as PILImage
import io


class ImageKitVerifier:
    """Verify ImageKit integration"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_section(self, title):
        """Print formatted section"""
        print(f"\n{title}")
        print("-" * 70)
    
    def check(self, test_name, condition, details=""):
        """Record a check result"""
        status = "✅ PASS" if condition else "❌ FAIL"
        
        result = {
            'name': test_name,
            'passed': condition,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        print(f"{status} | {test_name}")
        if details:
            print(f"       └─ {details}")
        
        if condition:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        self.print_section("Summary")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {percentage:.1f}%")
        
        print("\n" + "="*70)
        if self.failed == 0:
            print("✅ All checks passed!")
        else:
            print(f"⚠️  {self.failed} check(s) failed - review details above")
        print("="*70)
    
    def verify_configuration(self):
        """Verify ImageKit is configured"""
        self.print_section("1. Configuration Check")
        
        private_key = getattr(settings, 'IMAGEKIT_PRIVATE_KEY', '')
        public_key = getattr(settings, 'IMAGEKIT_PUBLIC_KEY', '')
        url_endpoint = getattr(settings, 'IMAGEKIT_URL_ENDPOINT', '')
        
        self.check(
            "Private Key configured",
            bool(private_key),
            f"Key length: {len(private_key) if private_key else 0}"
        )
        
        self.check(
            "Public Key configured",
            bool(public_key),
            f"Key length: {len(public_key) if public_key else 0}"
        )
        
        self.check(
            "URL Endpoint configured",
            bool(url_endpoint),
            f"Endpoint: {url_endpoint}"
        )
        
        self.check(
            "Storage backend is ImageKit",
            getattr(settings, 'DEFAULT_FILE_STORAGE', '') == 'nxtbn.core.imagekit_storage.ImageKitStorage',
            f"Backend: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}"
        )
    
    def verify_upload_capability(self):
        """Verify upload capability"""
        self.print_section("2. Upload Capability Check")
        
        try:
            # Create test image
            image = PILImage.new('RGB', (100, 100), color='red')
            image_io = io.BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            
            test_file = SimpleUploadedFile(
                'verification_test.jpg',
                image_io.getvalue(),
                content_type='image/jpeg'
            )
            
            # Try to upload
            saved_path = default_storage.save('images/verification_test.jpg', test_file)
            
            self.check(
                "File upload successful",
                bool(saved_path),
                f"Saved path: {saved_path}"
            )
            
            # Try to get URL
            try:
                url = default_storage.url(saved_path)
                self.check(
                    "URL generation successful",
                    bool(url) and url.startswith('http'),
                    f"URL: {url[:60]}..."
                )
                
                # Check if endpoint is in URL
                endpoint = getattr(settings, 'IMAGEKIT_URL_ENDPOINT', '')
                if endpoint:
                    endpoint_domain = endpoint.replace('https://', '').replace('http://', '').split('/')[0]
                    url_domain = url.replace('https://', '').replace('http://', '').split('/')[0]
                    self.check(
                        "URL contains ImageKit endpoint",
                        endpoint_domain in url_domain or endpoint in url,
                        f"Endpoint: {endpoint_domain}, URL domain: {url_domain}"
                    )
            except Exception as e:
                self.check("URL generation successful", False, str(e))
            
            # Cleanup
            try:
                default_storage.delete(saved_path)
                self.check("File cleanup successful", True, "Test file deleted")
            except Exception as e:
                self.check("File cleanup successful", False, str(e))
                
        except Exception as e:
            self.check("File upload successful", False, str(e))
    
    def verify_storage_backend(self):
        """Verify storage backend implementation"""
        self.print_section("3. Storage Backend Check")
        
        try:
            from nxtbn.core.imagekit_storage import ImageKitStorage
            
            self.check(
                "ImageKitStorage class imports",
                ImageKitStorage is not None,
                "ImageKitStorage class found"
            )
            
            # Check methods exist
            methods = ['_save', 'delete', 'exists', 'url']
            for method in methods:
                has_method = hasattr(ImageKitStorage, method)
                self.check(
                    f"ImageKitStorage.{method} method exists",
                    has_method,
                    f"Method: {method}"
                )
        except ImportError as e:
            self.check("ImageKitStorage class imports", False, str(e))
    
    def verify_models(self):
        """Verify model integration"""
        self.print_section("4. Model Integration Check")
        
        try:
            from nxtbn.filemanager.models import Image
            from nxtbn.product.models import Product
            
            self.check(
                "Image model imports",
                Image is not None,
                "Image model found"
            )
            
            self.check(
                "Product model imports",
                Product is not None,
                "Product model found"
            )
            
            # Check Image has expected fields
            image_fields = [f.name for f in Image._meta.get_fields()]
            self.check(
                "Image.image field exists",
                'image' in image_fields,
                f"Fields: {', '.join(image_fields)}"
            )
            
            self.check(
                "Image.image_xs field exists",
                'image_xs' in image_fields,
                "XS variant field found"
            )
            
            # Check Product-Image relationship
            product_fields = [f.name for f in Product._meta.get_fields()]
            self.check(
                "Product.images relationship exists",
                'images' in product_fields or any('image' in f.name.lower() for f in Product._meta.get_fields()),
                "Product-Image relationship found"
            )
            
        except ImportError as e:
            self.check("Model imports", False, str(e))
    
    def verify_settings(self):
        """Verify Django settings"""
        self.print_section("5. Django Settings Check")
        
        # Check default file storage
        default_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', '')
        self.check(
            "DEFAULT_FILE_STORAGE set",
            bool(default_storage),
            f"Storage: {default_storage}"
        )
        
        # Check media settings
        media_root = getattr(settings, 'MEDIA_ROOT', '')
        media_url = getattr(settings, 'MEDIA_URL', '')
        
        self.check(
            "MEDIA_ROOT configured",
            bool(media_root),
            f"Path: {media_root}"
        )
        
        self.check(
            "MEDIA_URL configured",
            bool(media_url),
            f"URL: {media_url}"
        )
    
    def run_all_checks(self):
        """Run all verification checks"""
        self.print_header("ImageKit Integration Verification")
        
        print(f"\nStarting verification at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.verify_configuration()
        self.verify_storage_backend()
        self.verify_models()
        self.verify_settings()
        self.verify_upload_capability()
        
        self.print_summary()
        
        return self.failed == 0


def main():
    """Main entry point"""
    verifier = ImageKitVerifier()
    success = verifier.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
