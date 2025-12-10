from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException

from nxtbn.core.admin_permissions import CommonPermissions, GranularPermission
from nxtbn.core.enum_perms import PermissionsEnum
from nxtbn.payment.models import Payment
from nxtbn.payment.api.dashboard.serializers import PaymentCreateSerializer, RefundSerializer
from nxtbn.users import UserRole

class RefundAPIView(generics.UpdateAPIView):
    permission_classes = (GranularPermission, )
    model = Payment
    required_perm = PermissionsEnum.CAN_INITIATE_PAYMENT_REFUND
    
    queryset = Payment.objects.all()
    serializer_class = RefundSerializer


    def get_object(self):
        order_alias = self.kwargs.get('order_alias')
        return get_object_or_404(Payment, order__alias=order_alias)
    
class PaymentCreateAPIView(generics.CreateAPIView):
    permission_classes = (CommonPermissions, )
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer