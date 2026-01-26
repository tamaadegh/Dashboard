from django.db import models

from nxtbn.core.models import AbstractBaseModel
from nxtbn.users.admin import User


class Image(AbstractBaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='image_created')
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='image_modified', null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    image_xs = models.ImageField(upload_to='images/xs/', null=True, blank=True)
    image_alt_text = models.CharField(max_length=255)

    def get_image_url(self, request):
        if self.image:
            url = self.image.url
            # If using Cloudinary, we can return the URL directly (or add transformations)
            if 'cloudinary.com' in url:
                return url
            return request.build_absolute_uri(url)
        return None

    def get_image_xs_url(self, request):
        if self.image_xs:
             url = self.image_xs.url
             if 'cloudinary.com' in url:
                return url
             return request.build_absolute_uri(url)
        
        if self.image:
            url = self.image.url
            if 'cloudinary.com' in url:
                # Cloudinary on-the-fly transformation for thumbnail
                # Insert /w_200,f_auto,q_auto/ after /upload/
                if '/upload/' in url:
                    return url.replace('/upload/', '/upload/w_200,f_auto,q_auto/')
                return url
            return request.build_absolute_uri(url)

        return None


class Document(AbstractBaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='document_created')
    last_modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='document_modified', null=True, blank=True)
    name = models.CharField(max_length=255)
    document = models.FileField()
    image_alt_text = models.CharField(max_length=255)