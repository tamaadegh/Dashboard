from rest_framework import serializers
from nxtbn.discount.models import PromoCode, PromoCodeCustomer, PromoCodeProduct, PromoCodeTranslation, PromoCodeUsage
from nxtbn.product.models import Product
from nxtbn.users.models import User


class PromoCodeCountedSerializer(serializers.ModelSerializer):
    total_redemptions = serializers.IntegerField(read_only=True, source='get_total_redemptions')
    total_applicable_products = serializers.IntegerField(read_only=True, source='get_total_applicable_products')
    total_specific_customers = serializers.IntegerField(read_only=True, source='get_total_specific_customers')
    class Meta:
        model = PromoCode
        exclude = ('applicable_products', 'specific_customers',)

class PromoCodeBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ('id', 'code', 'code_type', 'value', 'is_active', 'expiration_date',)

class AttachPromoCodeEntitiesSerializer(serializers.Serializer):
    promo_code = serializers.CharField()
    product_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )
    customer_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def validate_promo_code(self, value):
        try:
            return PromoCode.objects.get(code=value)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Promo code does not exist.")

    def validate_product_ids(self, value):
        products = Product.objects.filter(id__in=value)
        if len(products) != len(value):
            raise serializers.ValidationError("Some products do not exist.")
        return products

    def validate_customer_ids(self, value):
        customers = User.objects.filter(id__in=value)
        if len(customers) != len(value):
            raise serializers.ValidationError("Some customers do not exist.")
        return customers

    def create(self, validated_data):
        promo_code = validated_data['promo_code']

        # Attach products
        products = validated_data.get('product_ids', [])
        for product in products:
            PromoCodeProduct.objects.get_or_create(promo_code=promo_code, product=product)

        # Attach customers
        customers = validated_data.get('customer_ids', [])
        for customer in customers:
            PromoCodeCustomer.objects.get_or_create(promo_code=promo_code, customer=customer)

        return promo_code
    

class PromoCodeProductSerializer(serializers.ModelSerializer):
    promo_code = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = PromoCodeProduct
        fields = ['promo_code', 'product']

    def get_promo_code(self, obj):
        return {
            'id': obj.promo_code.id,
            'code': obj.promo_code.code,
        }

    def get_product(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
        }

class PromoCodeCustomerSerializer(serializers.ModelSerializer):
    promo_code = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = PromoCodeCustomer
        fields = ['promo_code', 'customer']

    def get_promo_code(self, obj):
        return {
            'id': obj.promo_code.id,
            'code': obj.promo_code.code,
        }

    def get_customer(self, obj):
        return {
            'id': obj.customer.id,
            'name': obj.customer.full_name() if obj.customer.first_name else obj.customer.username,
        }



class PromoCodeUsageSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    promocode = serializers.SerializerMethodField()

    class Meta:
        model = PromoCodeUsage
        fields = ['id', 'customer', 'promocode', 'order', 'applied_at']

    def get_customer(self, obj):
        if obj.user:
            return obj.user.username
        elif obj.order and obj.order.phone_number:
            return obj.order.phone_number
        return None
    
    def get_promocode(self, obj):
        return obj.promo_code.code

