from django.contrib import admin

from nxtbn.tax.models import TaxClass, TaxRate

class TaxRateInline(admin.TabularInline):
    model = TaxRate
    extra = 1

class TaxClassAdmin(admin.ModelAdmin):
    inlines = [TaxRateInline]

admin.site.register(TaxClass, TaxClassAdmin)