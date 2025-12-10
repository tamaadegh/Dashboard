from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.core.utils import to_currency_subunit
from nxtbn.order import OrderAuthorizationStatus, OrderChargeStatus, OrderStatus
from nxtbn.order.models import Order
from nxtbn.payment import PaymentMethod
from nxtbn.payment.models import Payment

class RefundSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(write_only=True, max_digits=4, decimal_places=2)
    class Meta:
        model = Payment
        fields = ['amount']

    def update(self, instance, validated_data):
        amount = validated_data.get('amount', '') # if null, then full refund, if amount, partial refund
        instance.refund_payment(amount)
        return instance

class BasicPaymentSerializer(serializers.ModelSerializer):
    payment_amount = serializers.CharField(source='humanize_payment_amount')
    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_method',
            'payment_amount',
            'paid_at',
            'is_successful',
            'payment_status',
            'transaction_id',
            'payment_status',
            'created_at',
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    order = serializers.CharField(write_only=True)
    payment_amount = serializers.DecimalField(required=True, max_digits=10, decimal_places=3)
    force_it = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Payment
        fields = [
            'order',
            'payment_method',
            'transaction_id',
            'payment_amount',
            'paid_at',
            'force_it',
        ]
        read_only_fields = ['order', 'user']  # You might want to set some fields as read-only

    def validate_order(self, value):
        try:
            order = Order.objects.get(alias=value)  # Assuming order has an alias field
        except Order.DoesNotExist:
            raise serializers.ValidationError(f"Order with alias '{value}' does not exist.")
        return order
    
    def create(self, validated_data):
        forice_it = validated_data.pop('force_it', False)
        order = validated_data.get('order')

        if order.status == OrderStatus.CANCELLED:
            raise serializers.ValidationError(_("Cancelled orders cannot be paid for."))

        if validated_data['payment_method'] == PaymentMethod.CASH_ON_DELIVERY:
            if order.status != OrderStatus.DELIVERED:
                raise serializers.ValidationError(_("If cash on delivery payment method is selected, the order must be delivered first."))

        order_total_subunit = order.total_price

        validated_data['user'] = order.user
        validated_data['currency'] = order.currency
        validated_data['payment_amount'] =  to_currency_subunit(validated_data['payment_amount'], order.currency)
        validated_data['is_successful'] = True

    
        if validated_data['payment_amount'] < order_total_subunit:
            if not forice_it:
                raise serializers.ValidationError(_("Payment amount is less than the total order price."))
        
            order.charge_status = OrderChargeStatus.PARTIAL
            order.authorization_status = OrderAuthorizationStatus.PARTIAL

        if validated_data['payment_amount'] > order_total_subunit:
            if not forice_it:
                raise serializers.ValidationError(_("Payment amount exceeds the total order price."))
            order.charge_status = OrderChargeStatus.OVERCHARGED
        
        if validated_data['payment_amount'] == order_total_subunit:
            order.charge_status = OrderChargeStatus.FULL
            order.authorization_status = OrderAuthorizationStatus.FULL

        payment = Payment.objects.create(**validated_data)
        order.save()

        return payment