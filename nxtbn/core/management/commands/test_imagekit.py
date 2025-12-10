from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test ImageKit file upload and management'

    def handle(self, *args, **options):
        try:
            self.stdout.write("\n=== Starting ImageKit Integration Test ===\n")
            
            # Test 1: File Upload
            test_content = b"Test file content for ImageKit integration"
            test_file = ContentFile(test_content)
            test_file.name = "test_file.txt"
            
            self.stdout.write("1. Testing file upload...")
            saved_name = default_storage.save(test_file.name, test_file)
            self.stdout.write(
                self.style.SUCCESS(f"✅ File uploaded successfully as: {saved_name}")
            )
            
            # Test 2: File Exists
            exists = default_storage.exists(saved_name)
            self.stdout.write(
                self.style.SUCCESS(f"2. File exists check: {exists}")
            )
            
            # Test 3: Get File URL
            file_url = default_storage.url(saved_name)
            self.stdout.write(
                self.style.SUCCESS(f"3. File URL: {file_url}")
            )
            
            # Test 4: Read File Content
            try:
                with default_storage.open(saved_name) as f:
                    content = f.read()
                    self.stdout.write(
                        self.style.SUCCESS(f"4. File content: {content.decode()}")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error reading file: {str(e)}")
                )
                logger.exception("Error reading file")
            
            # Test 5: Delete File
            try:
                default_storage.delete(saved_name)
                self.stdout.write(
                    self.style.SUCCESS("5. ✅ Test file deleted successfully")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error deleting file: {str(e)}")
                )
                logger.exception("Error deleting file")
            
            self.stdout.write("\n=== Test Completed ===\n")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n❌ Test failed: {str(e)}")
            )
            logger.exception("ImageKit test failed")
            raise