
from django.db.models import Q
from nxtbn.core.admin_permissions import CommonPermissions
from nxtbn.order import AddressType
from nxtbn.shipping.api.dashboard.serializers import (
    ShippingMethodSerializer,
    ShippingMethodTranslationSerializer, 
    ShppingMethodDetailSeralizer,
    ShippingRateSerializer
)
from nxtbn.shipping.models import ShippingMethod, ShippingMethodTranslation, ShippingRate
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets

from nxtbn.users.models import User

class CustomerEligibleShippingMethodstAPI(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = ShippingMethod
    serializer_class = ShippingMethodSerializer

    def get_queryset(self):
        country = self.request.query_params.get('country')
        region = self.request.query_params.get('region')
        city = self.request.query_params.get('city')

        # Start by getting all ShippingMethods
        queryset = ShippingMethod.objects.all()

        # Filter ShippingMethods based on related ShippingRate location data
        if country or region or city:
            queryset = queryset.filter(
                rates__in=ShippingRate.objects.filter(
                    Q(country__iexact=country) | Q(country__isnull=True),
                    Q(region__iexact=region) | Q(region__isnull=True),
                    Q(city__iexact=city) | Q(city__isnull=True)
                )
            ).distinct()

        return queryset
    
class ShippingMethodstListAPI(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = ShippingMethod
    serializer_class = ShippingMethodSerializer
    queryset = ShippingMethod.objects.all()


class ShippingMethodDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = ShippingMethod
    serializer_class = ShppingMethodDetailSeralizer
    queryset = ShippingMethod.objects.all()
    lookup_field = 'id'


class ShippingRateListCreateView(generics.ListCreateAPIView):
    permission_classes = (CommonPermissions, )
    model = ShippingRate
    serializer_class = ShippingRateSerializer
    queryset = ShippingRate.objects.all()


class ShippingRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (CommonPermissions, )
    model = ShippingRate
    serializer_class = ShippingRateSerializer
    queryset = ShippingRate.objects.all()
    lookup_field = 'id'

# ==================================================================
# Translation Views
# ==================================================================

class ShippingMethodTranslationViewSet(viewsets.ModelViewSet):
    permission_classes = (CommonPermissions, )
    model = ShippingMethodTranslation
    """
    A viewset for viewing and editing ShippingMethod translations.
    """
    serializer_class = ShippingMethodTranslationSerializer
    queryset = ShippingMethodTranslation.objects.all()
    