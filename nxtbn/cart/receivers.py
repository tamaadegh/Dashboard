from django.dispatch import receiver
from nxtbn.cart.utils import merge_carts

from nxtbn.core.signal_initiators import customer_logged_in

@receiver(customer_logged_in)
def handle_customer_logged_in(sender, user, request, **kwargs):
    """
    Signal handler that merges the guest cart with the authenticated customer's cart upon login.
    """
    merge_carts(request, user)
