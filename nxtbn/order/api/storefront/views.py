import os
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions  import AllowAny
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

from nxtbn.core.paginator import NxtbnPagination
from nxtbn.order.api.dashboard.views import ReturnRequestAPIView
from nxtbn.order.api.storefront.serializers import  OrderSerializer
from nxtbn.order.models import Order
from nxtbn.order import OrderStatus
from django.conf import settings

from nxtbn.order.proccesor.views import OrderProccessorAPIView
from nxtbn.payment import PaymentStatus
from nxtbn.payment.models import Payment
from nxtbn.payment.payment_manager import PaymentManager
from nxtbn.payment.utils import check_plugin_directory
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class OrderListView(generics.ListAPIView):
    pagination_class = NxtbnPagination
    serializer_class = OrderSerializer

    def get_queryset(self):
        return  Order.objects.filter(id=self.request.user)

class OrderEastimateAPIView(OrderProccessorAPIView):
    permission_classes = [AllowAny]
    create_order = False # Eastimate order does not create order

class OrderCreateAPIView(OrderProccessorAPIView):
    permission_classes = [AllowAny]
    create_order = True # Eastimate and Create Order with eastimated result
    broadcast_on_order_create = True # Broadcast order created signal
    order_source = 'storefront'
    collect_user_agent = True


class OrderReturnRequestAPIView(ReturnRequestAPIView):
    def get_queryset(self):
        return super().get_queryset().filter(order__order_user=self.request.user)