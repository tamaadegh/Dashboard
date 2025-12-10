from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.order.models import Address, Order, OrderLineItem
from nxtbn.payment import PaymentMethod
from nxtbn.payment.models import Payment
from nxtbn.payment.payment_manager import PaymentManager

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        # fields = '__all__'
        exclude=['user']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLineItem
        exclude = ('order',)

class OrderSerializer(serializers.ModelSerializer):
    line_item = OrderItemSerializer(many=True)
    payment_method = serializers.CharField(source='get_payment_method')
    class Meta:
        model = Order
        fields = '__all__'
        ref_name = 'order_storefront_get'