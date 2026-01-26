from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from nxtbn import settings
from nxtbn.filemanager.models import Image, Document
import logging

from PIL import Image as PILImage
from io import BytesIO
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = ("id", "created_by", "last_modified_by")

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by"] = request.user
        validated_data["last_modified_by"] = request.user

        # Optimize the image before saving (ONLY if not using Cloudinary)
        # Cloudinary handles optimization automatically on their end + we want to save bandwidth/processing time here.
        if "image" in validated_data and not getattr(settings, 'IS_CLOUDINARY', False):
            original_image_file = validated_data["image"]
            original_filename = original_image_file.name
            
            try:
                logger.info(f"Starting local image optimization: {original_filename}")
                
                # Read the uploaded file into memory once
                image_data = original_image_file.read()
                logger.info(f"Read {len(image_data)} bytes from uploaded file")
                
                # Create main optimized image
                logger.info("Creating main optimized image...")
                validated_data["image"] = self.optimize_image_from_bytes(
                    image_data, 
                    original_filename,
                    max_size_kb=settings.IMAGE_COMPRESS_MAX,
                    format="WEBP",
                    max_dimension=800
                )
                logger.info("Main image created successfully")
                
                # Create thumbnail from the same data
                logger.info("Creating thumbnail...")
                validated_data["image_xs"] = self.optimize_image_from_bytes(
                    image_data,
                    original_filename,
                    max_size_kb=10,
                    format="png",
                    max_dimension=50
                )
                logger.info("Thumbnail created successfully")
                
            except Exception as e:
                logger.error(f"Image processing failed: {type(e).__name__}: {str(e)}", exc_info=True)
                raise serializers.ValidationError(f"Image processing failed: {str(e)}")
        
        # If Cloudinary is enabled, just let it upload directly without local PIL processing
        # This is CRITICAL for speed and to avoid "Broken Pipe" on large files
        elif "image" in validated_data and getattr(settings, 'IS_CLOUDINARY', False):
             logger.info("Cloudinary enabled: Skipping local optimization to allow direct fast upload.")
        
        logger.info("Calling super().create() to save to database/storage...")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context["request"]
        validated_data["last_modified_by"] = request.user

        # Optimize the image if it is being updated (ONLY if not using Cloudinary)
        if "image" in validated_data and not getattr(settings, 'IS_CLOUDINARY', False):
            validated_data["image"] = self.optimize_image(validated_data["image"])
        elif "image" in validated_data and getattr(settings, 'IS_CLOUDINARY', False):
             logger.info("Cloudinary enabled: Skipping local optimization for update.")
        
        return super().update(instance, validated_data)

    @staticmethod
    def optimize_image_from_bytes(image_bytes, original_filename, max_size_kb=200, format="WEBP", max_dimension=800):
        """
        Optimize an image from raw bytes.
        This method is used to create multiple versions from the same source data.
        """
        # Open image from bytes
        img = PILImage.open(BytesIO(image_bytes))
        img = img.convert("RGB")  # Convert to RGB for compatibility

        # Adjust dimension based on image type
        if format.lower() == "png":
            max_dimension = min(max_dimension, 64)  # Reduce size for PNG to keep it small

        img.thumbnail((max_dimension, max_dimension), PILImage.Resampling.LANCZOS)

        # Use a buffer to store the optimized image
        buffer = BytesIO()

        if format.lower() == "png":
            # Reduce colors using quantization (important for PNG)
            img = img.convert("P", palette=PILImage.ADAPTIVE, colors=32)  # Limit colors to 32
            img.save(buffer, format="PNG", optimize=True)
        else:
            quality = 85
            img.save(buffer, format=format, optimize=True, quality=quality)

            # Reduce quality iteratively for WebP/JPEG if size is too large
            while buffer.tell() > max_size_kb * 1024 and quality > 10:
                quality -= 5
                buffer = BytesIO()  # Reset buffer
                img.save(buffer, format=format, optimize=True, quality=quality)

        buffer.seek(0)

        # Extract base filename without extension
        base_name = original_filename.rsplit('.', 1)[0] if '.' in original_filename else original_filename
        
        # Return the new image as a ContentFile
        return ContentFile(buffer.read(), name=f"{base_name}.{format.lower()}")

    @staticmethod
    def optimize_image(image_file, max_size_kb=settings.IMAGE_COMPRESS_MAX, format="WEBP", max_dimension=800):
        """
        Optimize an image by resizing and converting it to the specified format while maintaining the aspect ratio.
        Ensures the image file size is below max_size_kb.
        """
        img = PILImage.open(image_file)
        img = img.convert("RGB")  # Convert to RGB for compatibility

        # Adjust dimension based on image type (smaller for PNG to ensure < 2023 bytes)
        if format.lower() == "png":
            max_dimension = 64  # Reduce size for PNG to keep it small

        img.thumbnail((max_dimension, max_dimension), PILImage.Resampling.LANCZOS)

        # Use a buffer to store the optimized image
        buffer = BytesIO()

        if format.lower() == "png":
            # Reduce colors using quantization (important for PNG)
            img = img.convert("P", palette=PILImage.ADAPTIVE, colors=32)  # Limit colors to 32
            img.save(buffer, format="PNG", optimize=True)
        else:
            quality = 85
            img.save(buffer, format=format, optimize=True, quality=quality)

            # Reduce quality iteratively for WebP/JPEG if size is too large
            while buffer.tell() > max_size_kb * 1024 and quality > 10:
                quality -= 5
                buffer = BytesIO()  # Reset buffer
                img.save(buffer, format=format, optimize=True, quality=quality)

        buffer.seek(0)

        # Return the new image as a ContentFile
        return ContentFile(buffer.read(), name=f"{image_file.name.split('.')[0]}.{format.lower()}")




class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_by",
            "last_modified_by",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["last_modified_by"] = self.context["request"].user
        return super().create(validated_data)
