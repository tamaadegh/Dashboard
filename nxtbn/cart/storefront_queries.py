from django.conf import settings
import graphene
from nxtbn.cart.utils import get_or_create_cart
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import apply_exchange_rate
from nxtbn.cart.storefront_types import (
    CartItemType,
    CartType,
)
from nxtbn.product.models import ProductVariant
from nxtbn.core.currency.backend import currency_Backend



class CartQuery(graphene.ObjectType):
    cart = graphene.Field(CartType)

    def resolve_cart(self, info):
        # Get the cart (for guest or authenticated user)
        cart, is_guest = get_or_create_cart(info.context)

        exchange_rate = 1.0
        if settings.IS_MULTI_CURRENCY:
            exchange_rate = currency_Backend().get_exchange_rate(info.context.currency)
        
        info.context.exchange_rate = exchange_rate

        items = []
        total = 0
        
        if is_guest:
            # Handle guest cart
            for product_variant_id, item in cart.items():
                try:
                    product_variant = ProductVariant.objects.get(id=product_variant_id)
                    subtotal = product_variant.price * item['quantity']
                    total += subtotal
                    items.append(CartItemType(
                        product_variant=product_variant,
                        quantity=item['quantity'],
                        subtotal=apply_exchange_rate(subtotal, exchange_rate, info.context.currency, 'en_US')
                    ))
                except ProductVariant.DoesNotExist:
                    continue  # Optionally, handle missing product variants
        else:
            # Handle authenticated user's cart
            cart_items = cart.items.all()  # Assuming cart has a reverse relation to CartItem
            for cart_item in cart_items:
                product_variant = cart_item.variant
                subtotal = product_variant.price * cart_item.quantity
                total += subtotal
                items.append(CartItemType(
                    product_variant=product_variant,
                    quantity=cart_item.quantity,
                    subtotal=apply_exchange_rate(subtotal, exchange_rate, info.context.currency, 'en_US')
                ))

        # Return the unified response for both guest and authenticated users
        return CartType(items=items, total=apply_exchange_rate(total, exchange_rate, info.context.currency, 'en_US'))