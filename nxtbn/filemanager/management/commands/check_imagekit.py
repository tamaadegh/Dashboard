"""
Django management command to check environment variables.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Check ImageKit environment variables'

    def handle(self, *args, **options):
        """Check environment variable configuration"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write("IMAGEKIT ENVIRONMENT VARIABLES CHECK")
        self.stdout.write("="*80 + "\n")

        # Check raw environment variables
        self.stdout.write("1. Raw Environment Variables (from os.environ):")
        self.stdout.write("-"*80)
        
        env_vars = {
            'IMAGEKIT_PRIVATE_KEY': os.environ.get('IMAGEKIT_PRIVATE_KEY'),
            'IMAGEKIT_PUBLIC_KEY': os.environ.get('IMAGEKIT_PUBLIC_KEY'),
            'IMAGEKIT_URL_ENDPOINT': os.environ.get('IMAGEKIT_URL_ENDPOINT'),
        }
        
        for key, value in env_vars.items():
            if value:
                # Show first and last 5 chars
                masked = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else value
                self.stdout.write(self.style.SUCCESS(f"✓ {key}: {masked}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {key}: NOT SET"))

        # Check Django settings
        self.stdout.write("\n2. Django Settings Values:")
        self.stdout.write("-"*80)
        
        settings_vars = {
            'IMAGEKIT_PRIVATE_KEY': settings.IMAGEKIT_PRIVATE_KEY,
            'IMAGEKIT_PUBLIC_KEY': settings.IMAGEKIT_PUBLIC_KEY,
            'IMAGEKIT_URL_ENDPOINT': settings.IMAGEKIT_URL_ENDPOINT,
        }
        
        for key, value in settings_vars.items():
            if value:
                masked = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else value
                self.stdout.write(self.style.SUCCESS(f"✓ {key}: {masked}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ {key}: Empty string"))

        # Check IS_IMAGEKIT flag
        self.stdout.write("\n3. Configuration Check:")
        self.stdout.write("-"*80)
        
        is_imagekit = settings.IS_IMAGEKIT
        if is_imagekit:
            self.stdout.write(self.style.SUCCESS(f"✓ IS_IMAGEKIT: True (ImageKit is configured)"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ IS_IMAGEKIT: False (ImageKit NOT configured)"))
        
        # Check storage backend
        storage_backend = getattr(settings, 'STORAGE_BACKEND', 'NOT SET')
        self.stdout.write(f"Storage Backend: {storage_backend}")
        
        # Summary
        self.stdout.write("\n" + "="*80)
        self.stdout.write("SUMMARY")
        self.stdout.write("="*80)
        
        all_set = all([
            env_vars['IMAGEKIT_PRIVATE_KEY'],
            env_vars['IMAGEKIT_PUBLIC_KEY'],
            env_vars['IMAGEKIT_URL_ENDPOINT']
        ])
        
        if all_set and is_imagekit:
            self.stdout.write(self.style.SUCCESS("\n✓ ImageKit is properly configured!"))
        else:
            self.stdout.write(self.style.ERROR("\n✗ ImageKit is NOT properly configured"))
            self.stdout.write("\nTo fix this:")
            self.stdout.write("  LOCAL: Make sure .env file exists with ImageKit credentials")
            self.stdout.write("  PRODUCTION: Set environment variables in your deployment platform")
            self.stdout.write("")
            self.stdout.write("Required variables:")
            self.stdout.write("  - IMAGEKIT_PRIVATE_KEY=private_xxx...")
            self.stdout.write("  - IMAGEKIT_PUBLIC_KEY=public_xxx...")
            self.stdout.write("  - IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id")
        
        self.stdout.write("")
