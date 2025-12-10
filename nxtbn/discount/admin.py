from django.contrib import admin
from django.utils.html import format_html
from nxtbn.discount import PromoCodeType
from nxtbn.discount.models import (
    PromoCode,
    PromoCodeUsage,
    PromoCodeCustomer,
    PromoCodeProduct
)
from nxtbn.users.models import User
from nxtbn.product.models import Product
from nxtbn.order.models import Order

class PromoCodeCustomerInline(admin.TabularInline):
    """
    Inline admin for associating specific customers with a PromoCode.
    """
    model = PromoCodeCustomer
    extra = 1
    autocomplete_fields = ['customer']
    verbose_name = "Eligible Customer"
    verbose_name_plural = "Eligible Customers"


class PromoCodeProductInline(admin.TabularInline):
    """
    Inline admin for associating specific products with a PromoCode.
    """
    model = PromoCodeProduct
    extra = 1
    autocomplete_fields = ['product']
    verbose_name = "Applicable Product"
    verbose_name_plural = "Applicable Products"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing PromoCodes.
    """
    list_display = [
        'code',
        'code_type',
        'value_display',
        'is_active',
        'expiration_date',
        'redemption_limit',
        'get_total_redemptions',
    ]
    list_filter = [
        'is_active',
        'code_type',
        'expiration_date',
    ]
    search_fields = [
        'code',
        'description',
    ]
    ordering = ['-created_at']
    inlines = [
        PromoCodeCustomerInline,
        PromoCodeProductInline,
    ]
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'code_type', 'value', 'expiration_date', 'is_active')
        }),
        ('Advanced options', {
            'fields': ('min_purchase_amount', 'min_purchase_period', 'redemption_limit', 'new_customers_only', 'usage_limit_per_customer')
        }),
    )

    def value_display(self, obj):
        """
        Display value with appropriate formatting based on code_type.
        """
        if obj.code_type == PromoCodeType.PERCENTAGE:
            return f"{obj.value}%"
        else:
            return f"${obj.value}"
    value_display.short_description = 'Value'

    def get_total_redemptions(self, obj):
        """
        Display total redemptions for the PromoCode.
        """
        return obj.get_total_redemptions()
    get_total_redemptions.short_description = 'Total Redemptions'


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing PromoCode usages.
    """
    list_display = [
        'promo_code',
        'user',
        'order_link',
        'applied_at',
    ]
    list_filter = [
        'applied_at',
        'promo_code__code',
    ]
    search_fields = [
        'promo_code__code',
        'user__username',
        'order__id',
    ]
    readonly_fields = [
        'promo_code',
        'user',
        'order',
        'applied_at',
    ]
    ordering = ['-applied_at']

    def order_link(self, obj):
        """
        Provide a link to the associated order in the admin.
        """
        url = f"/admin/order/order/{obj.order.id}/change/"
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'


@admin.register(PromoCodeCustomer)
class PromoCodeCustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for managing PromoCodeCustomer relationships.
    """
    list_display = ['promo_code', 'customer']
    search_fields = [
        'promo_code__code',
        'customer__username',
        'customer__email',
    ]
    autocomplete_fields = ['promo_code', 'customer']


@admin.register(PromoCodeProduct)
class PromoCodeProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing PromoCodeProduct relationships.
    """
    list_display = ['promo_code', 'product']
    search_fields = [
        'promo_code__code',
        'product__name',
    ]
    autocomplete_fields = ['promo_code', 'product']
