"""
Custom storage backend for ImageKit integration.
Handles media file uploads and serving from ImageKit CDN.
"""
import logging
from django.conf import settings
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

try:
    from imagekitio import ImageKit
    from imagekitio.exceptions import BadRequestError
except ImportError:
    ImageKit = None
    logger.warning("imagekitio not installed. Install with: pip install imagekitio")


class ImageKitStorage(Storage):
    """
    Django storage backend for ImageKit.
    Uploads files to ImageKit and serves them via CDN.
    
    Required environment variables:
    - IMAGEKIT_PRIVATE_KEY
    - IMAGEKIT_PUBLIC_KEY
    - IMAGEKIT_URL_ENDPOINT
    """

    def __init__(self):
        if not ImageKit:
            raise ImproperlyConfigured(
                'ImageKit storage requires imagekitio. Install with: pip install imagekitio'
            )
        
        self.private_key = getattr(settings, 'IMAGEKIT_PRIVATE_KEY', '')
        self.public_key = getattr(settings, 'IMAGEKIT_PUBLIC_KEY', '')
        self.url_endpoint = getattr(settings, 'IMAGEKIT_URL_ENDPOINT', '')
        
        if not all([self.private_key, self.public_key, self.url_endpoint]):
            raise ImproperlyConfigured(
                'ImageKit storage requires IMAGEKIT_PRIVATE_KEY, '
                'IMAGEKIT_PUBLIC_KEY, and IMAGEKIT_URL_ENDPOINT settings.'
            )
        
        self.client = ImageKit(
            private_key=self.private_key,
            public_key=self.public_key,
            url_endpoint=self.url_endpoint,
        )

    def _open(self, name, mode='rb'):
        """Open a file from ImageKit."""
        # ImageKit doesn't support direct file opening via URL; 
        # this is primarily for uploads and URL serving.
        raise NotImplementedError(
            'Direct file opening from ImageKit is not supported. '
            'Use file.url to access the CDN URL.'
        )

    def _save(self, name, content):
        """Upload a file to ImageKit."""
        try:
            file_data = content.read()
            
            # Upload to ImageKit
            response = self.client.upload_file(
                file=file_data,
                file_name=name,
            )
            
            logger.info(f'Uploaded {name} to ImageKit: {response.file_id}')
            return response.file_id or name
        
        except BadRequestError as e:
            logger.error(f'ImageKit upload failed for {name}: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Unexpected error uploading {name} to ImageKit: {str(e)}')
            raise

    def delete(self, name):
        """Delete a file from ImageKit."""
        try:
            self.client.delete_file(file_id=name)
            logger.info(f'Deleted {name} from ImageKit')
        except Exception as e:
            logger.error(f'Failed to delete {name} from ImageKit: {str(e)}')
            # Don't raise; deletion failures shouldn't break the app

    def exists(self, name):
        """Check if file exists in ImageKit."""
        # ImageKit doesn't provide direct existence checks via API.
        # Always assume files exist if uploaded (optimistic).
        return bool(name)

    def listdir(self, path):
        """List files in ImageKit folder."""
        # ImageKit API doesn't support directory listing directly.
        raise NotImplementedError('ImageKit storage does not support directory listing.')

    def size(self, name):
        """Get file size from ImageKit."""
        # ImageKit API doesn't expose file size directly via file ID.
        return 0

    def url(self, name):
        """Return the public CDN URL for a file."""
        # Construct ImageKit CDN URL
        # name is typically the file_id or file path
        return f'{self.url_endpoint}/{name}'

    def get_accessed_time(self, name):
        """Not supported by ImageKit."""
        raise NotImplementedError('ImageKit storage does not support accessed time.')

    def get_created_time(self, name):
        """Not supported by ImageKit."""
        raise NotImplementedError('ImageKit storage does not support created time.')

    def get_modified_time(self, name):
        """Not supported by ImageKit."""
        raise NotImplementedError('ImageKit storage does not support modified time.')
