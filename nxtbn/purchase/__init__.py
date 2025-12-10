from django.db import models

class PurchaseStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending'
    CANCELLED = 'CANCELLED', 'Cancelled'
    RECEIVED_AND_CLOSED = 'RECEIVED_AND_CLOSED', 'Received and Closed' # Stock has been updated and purchase order is closed