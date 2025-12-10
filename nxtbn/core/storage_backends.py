from imagekitio import ImageKit
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

class ImageKitStorage(Storage):
    def __init__(self, **kwargs):
        try:
            self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.IMAGEKIT_URL_ENDPOINT
            )
        except Exception as e:
            logger.error("Failed to initialize ImageKit client: %s", str(e))
            raise

    def _save(self, name, content):
        try:
            # Ensure we're at the start of the file
            if hasattr(content, 'seek'):
                content.seek(0)
                
            # Upload the file to ImageKit
            response = self.imagekit.upload_file(
                file=content,
                file_name=name,
                options={
                    "use_unique_file_name": True,  # Changed to True to avoid conflicts
                    "folder": "/test-uploads/"    # Using a test folder
                }
            )
            logger.info("File uploaded to ImageKit: %s", response['name'])
            return response['name']
        except Exception as e:
            logger.error("Error uploading file %s to ImageKit: %s", name, str(e))
            raise

    def exists(self, name):
        try:
            # Since we're using unique file names, we can assume it doesn't exist
            return False
        except Exception as e:
            logger.error("Error checking if file %s exists in ImageKit: %s", name, str(e))
            return False

    def url(self, name):
        try:
            # Construct the URL from the endpoint and file name
            return f"{settings.IMAGEKIT_URL_ENDPOINT}/test-uploads/{name.split('/')[-1]}"
        except Exception as e:
            logger.error("Error generating URL for %s: %s", name, str(e))
            raise

    def delete(self, name):
        try:
            # Extract file ID from URL or use name as file ID
            file_id = name.split('/')[-1]  # Get the last part of the path
            response = self.imagekit.delete_file(file_id=file_id)
            logger.info("File %s deleted from ImageKit", name)
            return True
        except Exception as e:
            logger.error("Error deleting file %s from ImageKit: %s", name, str(e))
            return False

    def open(self, name, mode='rb'):
        try:
            # For reading, we'll use the URL and make a request
            import requests
            from io import BytesIO
            
            url = self.url(name)
            response = requests.get(url)
            response.raise_for_status()
            
            return ContentFile(response.content, name=name)
        except Exception as e:
            logger.error("Error opening file %s from ImageKit: %s", name, str(e))
            raise