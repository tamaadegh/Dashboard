import uuid
from django.db import models


class PaymentTransaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_UNKNOWN = 'unknown'

    CHANNEL_MTN = 'mtn-gh'
    CHANNEL_VODAFONE = 'vodafone-gh'
    CHANNEL_TIGO = 'tigo-gh'

    CHANNEL_CHOICES = [
        (CHANNEL_MTN, 'MTN Ghana'),
        (CHANNEL_VODAFONE, 'Vodafone / Telecel'),
        (CHANNEL_TIGO, 'AirtelTigo'),
    ]

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_UNKNOWN, 'Unknown'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_reference = models.CharField(max_length=128, unique=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_msisdn = models.CharField(max_length=32)
    customer_email = models.EmailField(blank=True, null=True)
    channel = models.CharField(max_length=30, choices=CHANNEL_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    hubtel_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    external_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    raw_initial_response = models.JSONField(blank=True, null=True)
    raw_callback_response = models.JSONField(blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PaymentTransaction({self.client_reference} - {self.status})"
