from rest_framework import generics
from django.utils.translation import gettext_lazy as _

import django_filters
from django_filters.rest_framework import DjangoFilterBackend


from nxtbn.core.admin_permissions import CommonPermissions
from nxtbn.filemanager.models import Document, Image
from nxtbn.filemanager.api.dashboard.serializers import (
    DocumentSerializer,
    ImageSerializer,
)
from nxtbn.core.paginator import NxtbnPagination

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
