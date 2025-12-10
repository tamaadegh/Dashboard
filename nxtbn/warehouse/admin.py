from django.contrib import admin
from nxtbn.warehouse.models import Stock, StockReservation, Warehouse


admin.site.register(Stock)
admin.site.register(Warehouse)
admin.site.register(StockReservation)