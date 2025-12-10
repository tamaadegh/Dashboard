from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.db import transaction
from nxtbn.tax.models import TaxClass, TaxClassTranslation, TaxRate


class TaxRateSerializer(serializers.ModelSerializer):
    full_country_name = serializers.SerializerMethodField()

    class Meta:
        model = TaxRate
        ref_name = 'tax_rate_get'
        fields = ('id', 'country', 'full_country_name', 'state', 'rate', 'is_active', 'tax_class' )
        extra_kwargs = {
            'tax_class': {'write_only': True} 
        }

    def get_full_country_name(self, obj):
        return obj.get_country_display()            
    

class TaxClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxClass
        ref_name = 'tax_class_get'
        fields = '__all__'
    

class TaxClassDetailSerializer(serializers.ModelSerializer):
    tax_rates = TaxRateSerializer(many=True, read_only=True)

    class Meta:
        model = TaxClass
        ref_name = 'tax_class_detail_get'
        fields = ('id', 'name', 'tax_rates',)

