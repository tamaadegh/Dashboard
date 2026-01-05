from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
import logging

import django_filters
from django_filters.rest_framework import DjangoFilterBackend


from nxtbn.core.admin_permissions import CommonPermissions
from nxtbn.filemanager.models import Document, Image
from nxtbn.filemanager.api.dashboard.serializers import (
    DocumentSerializer,
    ImageSerializer,
)
from nxtbn.core.paginator import NxtbnPagination

logger = logging.getLogger(__name__)

class ImageFilter(django_filters.FilterSet):
    id = django_filters.BaseInFilter(field_name='id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Image
        fields = ['id', 'name']

class ImageListView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = Image
    serializer_class = ImageSerializer
    queryset = Image.objects.all().order_by('-created_at')
    pagination_class = NxtbnPagination
    filter_backends = [ DjangoFilterBackend,]
    filterset_class = ImageFilter
    
    def create(self, request, *args, **kwargs):
        """Override create to add detailed error logging"""
        try:
            logger.info(f"[IMAGE UPLOAD] Starting upload request from user: {request.user}")
            logger.info(f"[IMAGE UPLOAD] Request data keys: {list(request.data.keys())}")
            
            # Get file info if present
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                logger.info(f"[IMAGE UPLOAD] File name: {image_file.name}, size: {image_file.size} bytes, content_type: {image_file.content_type}")
            
            response = super().create(request, *args, **kwargs)
            logger.info(f"[IMAGE UPLOAD] Upload successful, ID: {response.data.get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"[IMAGE UPLOAD] Upload failed: {type(e).__name__}: {str(e)}", exc_info=True)
            # Re-raise to let DRF handle the response
            raise


class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = Image
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    pagination_class = NxtbnPagination
    lookup_field = "id"


class DocumentListView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = Document
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
    pagination_class = NxtbnPagination


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = Document
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = NxtbnPagination
    lookup_field = "id"
