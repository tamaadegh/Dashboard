from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from nxtbn.core.admin_permissions import CommonPermissions
from nxtbn.core.paginator import NxtbnPagination

from nxtbn.tax.models import TaxClass, TaxClassTranslation, TaxRate
from nxtbn.tax.api.dashboard.serializers import (
    TaxClassSerializer, 
    TaxClassDetailSerializer,
    TaxRateSerializer
)

from rest_framework import filters as drf_filters
import django_filters
from django_filters import rest_framework as filters

from nxtbn.users import UserRole

class TaxClassView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = TaxClass
    queryset = TaxClass.objects.all()
    serializer_class = TaxClassSerializer
    pagination_class = NxtbnPagination


class TaxClassDetailsView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = TaxClass
    queryset = TaxClass.objects.all()
    serializer_class = TaxClassDetailSerializer
    lookup_field = 'id'

class TaxRateListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = TaxClass
    serializer_class = TaxRateSerializer
    queryset = TaxRate.objects.all()
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter
    ]
    filterset_fields = ['tax_class', 'country', 'state', 'is_active']
    search_fields = ['country', 'state', 'rate']


class TaxRateRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = TaxClass
    serializer_class = TaxRateSerializer
    queryset = TaxRate.objects.all()
    lookup_field = 'id'
