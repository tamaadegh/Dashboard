from django.contrib import admin
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('client_reference', 'customer_msisdn', 'amount', 'status', 'created_at')
    search_fields = ('client_reference', 'customer_msisdn', 'hubtel_transaction_id')
    readonly_fields = ('raw_initial_response', 'raw_callback_response')
