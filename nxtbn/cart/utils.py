
from nxtbn.product.models import ProductVariant
from nxtbn.cart.models import Cart, CartItem

from django.shortcuts import get_object_or_404

def get_or_create_cart(request):
    """
    Retrieves the cart for the authenticated user or creates a new guest cart.
    Returns a tuple: (cart_object, is_guest)
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart, False
    else:
        # For guest users, retrieve the cart from the session
        cart = request.session.get('cart', {})
        return cart, True

def save_guest_cart(request, cart):
    """
    Saves the guest cart back to the session.
    """
    request.session['cart'] = cart
    request.session.modified = True

def merge_carts(request, user):
    """
    Merges the guest cart stored in the session with the authenticated user's cart.
    """
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return

    cart, created = Cart.objects.get_or_create(user=user)

    for product_variant_id, item in session_cart.items():
        product_variant = get_object_or_404(ProductVariant, id=product_variant_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=product_variant
        )
        if not created:
            cart_item.quantity += item.get('quantity', 1)
            cart_item.save()
        else:
            cart_item.quantity = item.get('quantity', 1)
            cart_item.save()

    # Clear the session cart after merging
    request.session['cart'] = {}



def remove_ordered_items_from_cart(order, request=None):
    """
    Remove items from the cart that have been ordered.
    If is_guest is True, cart is from the session, and request is required to modify the session.
    """
    if request is None: # If request is not provided, we can't modify the session cart
        return
    
    cart, is_guest = get_or_create_cart(request)
    if is_guest and request:
        # Guest user: Handle session cart
        for item in order.line_items.all():
            product_variant_id = str(item.variant.id)
            if product_variant_id in cart:
                del cart[product_variant_id]  # Remove ordered item from session cart
        
        # Save updated guest cart back to the session
        request.session['cart'] = cart
        request.session.modified = True

    else:
        # Authenticated user: Handle cart stored in the database
        for item in order.line_items.all():  # Assuming 'order.items' gives you the ordered items
            try:
                cart_item = CartItem.objects.get(cart=cart, variant=item.variant)
                cart_item.delete()  # Remove the cart item corresponding to the ordered product
            except CartItem.DoesNotExist:
                continue  # Ignore if the item is not in the cart (already removed or wasn't added)
