from rest_framework import serializers
from .models import PaymentTransaction


class InitiatePaymentSerializer(serializers.Serializer):
    msisdn = serializers.CharField(max_length=32)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    channel = serializers.ChoiceField(choices=[c[0] for c in PaymentTransaction.CHANNEL_CHOICES])
    customer_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)

    def validate_msisdn(self, value):
        # Ensure country code present (Ghana = 233)
        v = value.strip()
        if not v.startswith('233'):
            raise serializers.ValidationError('MSISDN must include country code (e.g. 233...)')
        return v


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'client_reference', 'customer_name', 'customer_msisdn', 'customer_email',
            'channel', 'amount', 'status', 'hubtel_transaction_id', 'external_transaction_id',
            'raw_initial_response', 'raw_callback_response', 'payment_date', 'created_at', 'updated_at'
        ]
