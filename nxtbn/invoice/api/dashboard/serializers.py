from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction

from nxtbn.core.api.dashboard.serializers import SiteSettingsSerializer
from nxtbn.core.models import SiteSettings
from nxtbn.order.api.dashboard.serializers import OrderLineItemSerializer
from nxtbn.order.api.storefront.serializers import AddressSerializer
from nxtbn.order.models import Order, OrderLineItem



class OrderInvoiceSerializer(serializers.ModelSerializer):
    billing_address = AddressSerializer()
    shipping_address = AddressSerializer()
    company_info = serializers.SerializerMethodField()
    items = OrderLineItemSerializer(source='line_items', many=True)
    total_price = serializers.SerializerMethodField()
    payment_method = serializers.CharField(source='get_payment_method')

    class Meta:
        model = Order
        fields = [
            'id',
            'alias',
            'billing_address',
            'shipping_address',
            'company_info', 
            'items',
            'total_price',
            'currency',
            'customer_currency',
            'payment_method',
            'total_discounted_amount',
            'total_shipping_cost',
            'total_tax'
        ]

    def get_company_info(self, obj):
        site_id = self.context['request'].site_id if hasattr(self.context['request'], 'site_id') else getattr(settings, 'SITE_ID', 1)
        site_settings = SiteSettings.objects.get(site__id=site_id)
        return SiteSettingsSerializer(site_settings).data
    
    def get_total_price(self, obj):
        return obj.humanize_total_price()

