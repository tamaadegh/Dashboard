from django.dispatch import receiver
from nxtbn.cart.utils import remove_ordered_items_from_cart
from nxtbn.core.signal_initiators import order_created

@receiver(order_created)
def handle_post_order_create(sender, order, request, **kwargs):
    remove_ordered_items_from_cart(order, request=request)
   
