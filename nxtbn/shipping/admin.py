from django.contrib import admin
from nxtbn.shipping.models import ShippingMethod, ShippingRate


admin.site.register(ShippingMethod)
admin.site.register(ShippingRate)
