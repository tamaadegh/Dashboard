from django.db import models

from django.core.validators import MinValueValidator
from decimal import Decimal

from nxtbn.core.models import AbstractBaseModel, AbstractBaseUUIDModel
from nxtbn.product.models import ProductVariant
from nxtbn.users.models import User   



class Cart(AbstractBaseUUIDModel):
    """
    Represents a shopping cart. It can be associated with a user
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    
    def __str__(self):
        if self.user:
            return f"Cart({self.user.username})"
        return f"Cart({self.alias})"


class CartItem(AbstractBaseUUIDModel):
    """
    Represents an item within a shopping cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.variant.name} in Cart {self.cart.id}"