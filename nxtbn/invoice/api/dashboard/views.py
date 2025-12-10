from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from nxtbn.core.admin_permissions import IsStoreStaff
from nxtbn.invoice.api.dashboard.serializers import OrderInvoiceSerializer
from nxtbn.order.models import Order
from nxtbn.users import UserRole


class OrderInvoiceAPIView(generics.RetrieveAPIView):
    permission_classes = (IsStoreStaff,)
    queryset = Order.objects.all()
    serializer_class = OrderInvoiceSerializer
    lookup_field = 'alias'