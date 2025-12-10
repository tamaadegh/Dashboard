from django.db import models
from django.forms import ValidationError
from django.db.models import Sum

from nxtbn.core.enum_perms import PermissionsEnum
from nxtbn.core.models import AbstractBaseModel
from nxtbn.order.models import Order, OrderLineItem
from nxtbn.product.models import ProductVariant
from nxtbn.users.models import User
from nxtbn.warehouse import StockMovementStatus


class Warehouse(AbstractBaseModel):
    name = models.CharField(max_length=255, unique=True, help_text="Warehouse name. e.g. 'Main Warehouse' or 'Warehouse A' or 'store-1'")
    location = models.CharField(max_length=255)
    is_default = models.BooleanField(
        default=False,
        help_text="Only one warehouse can be default"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Stock(AbstractBaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="warehouse_stocks")
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(
        default=0,
        help_text=(
            "Quantity of this product variant that is reserved for specific purposes: "
            "1. Pending Orders: Items reserved for orders that have been placed but not yet fulfilled. "
            "2. Blocked Stock: Inventory set aside for quality control, specific customer allocation, or planned events. "
            "3. Pre-booked Stock: Stock promised to a customer or distributor but not yet shipped."
        )
    )
    incoming = models.IntegerField(
        default=0, help_text="Quantity of this product variant that is expected to arrive because of purchase order or return or transfer"
    )

    class Meta:
        unique_together = ('warehouse', 'product_variant')

    def clean(self):
        # Check if a Stock instance with the same warehouse and product_variant already exists
        if Stock.objects.filter(warehouse=self.warehouse, product_variant=self.product_variant).exists():
            raise ValidationError(
                f"A stock record with this warehouse and product variant already exists: "
                f"{self.warehouse.name} - {self.product_variant.sku}"
            )

    def __str__(self):
        return f"{self.product_variant.sku} in {self.warehouse.name}"
    
   
    
    def available_for_new_order(self):
        return self.quantity - self.reserved



class StockReservation(AbstractBaseModel):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="reservations")
    quantity = models.PositiveIntegerField()
    purpose = models.CharField(max_length=50, help_text="Purpose of the reservation. e.g. 'Pending Order', 'Blocked Stock', 'Pre-booked Stock'")
    order_line = models.ForeignKey(OrderLineItem, on_delete=models.CASCADE, related_name="stock_reservations", null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} reserved for {self.purpose}"
    
    def delete(self, *args, **kwargs):
        stock = self.stock
        super().delete(*args, **kwargs)

        total_reserved = stock.reservations.aggregate(total=Sum('quantity'))['total'] or 0
        if stock.reserved != total_reserved:
            stock.reserved = total_reserved
            stock.save(update_fields=['reserved'])


class StockTransfer(AbstractBaseModel):
    """Tracks transfers of inventory between warehouses"""    
    from_warehouse = models.ForeignKey(Warehouse, related_name='transfers_out', on_delete=models.PROTECT)
    to_warehouse = models.ForeignKey(Warehouse, related_name='transfers_in', on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=StockMovementStatus.choices, default=StockMovementStatus.PENDING)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        permissions = [
            (PermissionsEnum.CAN_RECEIVE_TRANSFERRED_STOCK, "Can receive transferred stock"),
            (PermissionsEnum.CAN_MARK_STOCK_TRANSFER_AS_COMPLETED, "Can mark stock transfer as completed"),
        ]
    
    def __str__(self):
        return f"Transfer {self.id} - {self.from_warehouse} to {self.to_warehouse}"

class StockTransferItem(AbstractBaseModel):
    """Line items for a stock transfer"""
    stock_transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField() # quantity that is being transferred

    # fill only when the transfer started receiving
    received_quantity = models.PositiveIntegerField(default=0)
    rejected_quantity = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.variant.name} - {self.quantity}"