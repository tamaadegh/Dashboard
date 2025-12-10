from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from nxtbn.discount.models import PromoCode
from nxtbn.product.models import Product
from nxtbn.users import UserRole

class VariantQuantitySerializer(serializers.Serializer):
    alias = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)

class PriceAndNameSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.CharField()

class ShippingAddressSerializer(serializers.Serializer):
    city = serializers.CharField(required=False)
    postal_code = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    street_address = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)

class OrderEstimateSerializer(serializers.Serializer):
    shipping_address = ShippingAddressSerializer(required=False)
    billing_address = ShippingAddressSerializer(required=False)
    shipping_address_id = serializers.IntegerField(required=False)
    billing_address_id = serializers.IntegerField(required=False)

    shipping_method_id = serializers.IntegerField(required=False)
    custom_shipping_amount = PriceAndNameSerializer(required=False) # Only staff can set custom shipping amount

    custom_discount_amount = PriceAndNameSerializer(required=False)
    promocode = serializers.CharField(required=False)
    variants = serializers.ListSerializer(child=VariantQuantitySerializer(), required=True)
    customer_id = serializers.IntegerField(required=False)
    note = serializers.CharField(required=False)

    def validate_variants(self, value):
        if len(value) == 0:
            raise serializers.ValidationError("You must add one or more products to your cart.")
        return value
    
    def validate_custom_shipping_amount(self, value):
        if self.context['request'].user.is_staff:
            return value
        raise PermissionDenied("Only staff can set custom shipping amount.")
    
    def validate_custom_discount_amount(self, value):
        if self.context['request'].user.is_staff:
            return value
        raise PermissionDenied("Only staff can set custom discount amount.")