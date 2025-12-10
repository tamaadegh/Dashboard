from django.db import models

from nxtbn.core.models import AbstractBaseModel
from nxtbn.product.models import ProductVariant, Supplier
from nxtbn.purchase import PurchaseStatus
from nxtbn.users.models import User
from nxtbn.warehouse.models import Warehouse



class PurchaseOrder(AbstractBaseModel):
    """Represents a purchase order from a supplier"""    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    destination = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=PurchaseStatus.choices, default=PurchaseStatus.DRAFT)
    expected_delivery_date = models.DateField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']


    
    def __str__(self):
        return f"PO-{self.id} ({self.status})"

class PurchaseOrderItem(models.Model):
    """Line items for a purchase order"""
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    
    ordered_quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField(default=0)
    rejected_quantity = models.PositiveIntegerField(default=0)
    
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ['purchase_order', 'variant']
    
    def __str__(self):
        return f"{self.variant.name} - {self.ordered_quantity}"
