
"""
Custom storage backend for ImageKit integration.
Handles media file uploads and serving from ImageKit CDN.
"""
import logging
from django.conf import settings
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


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
        # Import ImageKit here to avoid import errors at module load time
        try:
            from imagekitio import ImageKit
            # Try to import BadRequestException, fallback to generic Exception
            try:
                from imagekitio.exceptions import BadRequestException
                self.BadRequestException = BadRequestException
            except ImportError:
                # Older versions might not have exceptions module
                self.BadRequestException = Exception
        except ImportError as e:
            raise ImproperlyConfigured(
                'ImageKit storage requires imagekitio. Install with: pip install imagekitio'
            ) from e
        
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
            logger.info(f'[_save] Starting upload for: {name}')
            
            file_data = content.read()
            logger.info(f'[_save] Read {len(file_data)} bytes from content')
            
            # Upload to ImageKit
            logger.info(f'[_save] Calling ImageKit upload_file...')
            response = self.client.upload_file(
                file=file_data,
                file_name=name,
            )
            logger.info(f'[_save] upload_file returned response type: {type(response)}')
            
            # ImageKit response is an object with attributes, not a dict
            # The response object has: file_id, name, url, file_path, etc.
            if hasattr(response, 'response_metadata'):
                logger.info(f'[_save] Response metadata: {response.response_metadata}')
            
            # Extract file_id or file_path for storage reference
            file_reference = None
            if hasattr(response, 'file_id'):
                file_reference = response.file_id
                logger.info(f'[_save] Using file_id: {file_reference}')
            elif hasattr(response, 'file_path'):
                file_reference = response.file_path
                logger.info(f'[_save] Using file_path: {file_reference}')
            elif hasattr(response, 'url'):
                # Extract path from URL as fallback
                file_reference = response.url.split(self.url_endpoint)[-1].lstrip('/')
                logger.info(f'[_save] Extracted from URL: {file_reference}')
            else:
                file_reference = name
                logger.warning(f'[_save] Could not extract file reference, using original name: {name}')
            
            logger.info(f'Successfully uploaded {name} to ImageKit, reference: {file_reference}')
            return file_reference
        
        except self.BadRequestException as e:
            error_msg = f'ImageKit BadRequest: {str(e)}'
            logger.error(f'ImageKit upload failed for {name}: {error_msg}', exc_info=True)
            raise Exception(error_msg) from e
        except AttributeError as e:
            error_msg = f'ImageKit response parsing error for {name}: {str(e)}'
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f'Unexpected ImageKit error for {name}: {str(e)}'
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e

    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's suitable for use on the target storage system
        and available for the given file name.
        
        For ImageKit, we don't need to check for duplicate files since each upload
        gets a unique file_id. Just return the name as-is.
        """
        return name

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
