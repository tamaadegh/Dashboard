from django.shortcuts import get_object_or_404
import graphene
from graphql import GraphQLError
from graphene_django.types import DjangoObjectType
from nxtbn.product.models import ProductVariant
from nxtbn.cart.models import Cart, CartItem 
from nxtbn.core.currency.backend import currency_Backend
from nxtbn.product.storefront_types import  ProductVariantType 
from nxtbn.cart.storefront_types import CartType
from nxtbn.cart.utils import get_or_create_cart, save_guest_cart  

class CartItemUpdateInput(graphene.InputObjectType):
    product_variant_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)

class AddToCartMutation(graphene.Mutation):
    class Arguments:
        input = CartItemUpdateInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    cart = graphene.Field(CartType)

    def mutate(self, info, input):
        try:
            product_variant = ProductVariant.objects.get(id=input.product_variant_id)
        except ProductVariant.DoesNotExist:
            raise GraphQLError("Product variant not found")

        cart, is_guest = get_or_create_cart(info.context)

        if not is_guest:
            # Authenticated user - Add or update the cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                variant=product_variant
            )
            if not created:
                cart_item.quantity += input.quantity
                cart_item.save()
            else:
                cart_item.quantity = input.quantity
                cart_item.save()
            return AddToCartMutation(success=True, message="Item added to cart", cart=cart)

        else:
            # Guest user - Add item to session cart
            cart_data = info.context.session.get('cart', {})
            if str(input.product_variant_id) in cart_data:
                cart_data[str(input.product_variant_id)]['quantity'] += input.quantity
            else:
                cart_data[str(input.product_variant_id)] = {
                    'quantity': input.quantity,
                    'price': str(product_variant.price)  # Ensure JSON serializable
                }
            save_guest_cart(info.context, cart_data)
            return AddToCartMutation(success=True, message="Item added to cart", cart=None)





# Mutation for updating cart item
class UpdateCartItemMutation(graphene.Mutation):
    class Arguments:
        input = CartItemUpdateInput(required=True)

    message = graphene.String()

    def mutate(self, info, input):
        # Extract input data
        product_variant_id = input.product_variant_id
        quantity = input.quantity

        if quantity < 1:
            raise Exception("Quantity must be at least 1.")

        # Fetch product variant
        product_variant = get_object_or_404(ProductVariant, id=product_variant_id)

        # Get or create the cart
        cart, is_guest = get_or_create_cart(info.context)

        if not is_guest:
            # Authenticated user
            try:
                cart_item = CartItem.objects.get(cart=cart, variant=product_variant)
                cart_item.quantity = quantity
                cart_item.save()
                return UpdateCartItemMutation(message="Cart item updated successfully.")
            except CartItem.DoesNotExist:
                raise Exception("Item not found in cart.")
        else:
            # Guest user
            cart = info.context.session.get('cart', {})
            if str(product_variant_id) in cart:
                cart[str(product_variant_id)]['quantity'] = quantity
                save_guest_cart(info.context, cart)
                return UpdateCartItemMutation(message="Cart item updated successfully.")
            else:
                raise Exception("Item not found in cart.")
            



class RemoveFromCartMutation(graphene.Mutation):
    class Arguments:
        product_variant_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    cart = graphene.Field(CartType)  # Assuming you have CartType for the cart object

    def mutate(self, info, product_variant_id):
        # Retrieve the product variant by ID
        product_variant = ProductVariant.objects.get(id=product_variant_id)
        
        cart, is_guest = get_or_create_cart(info.context)

        if not is_guest:
            # Authenticated user
            try:
                cart_item = CartItem.objects.get(cart=cart, variant=product_variant)
                cart_item.delete()
                return RemoveFromCartMutation(
                    success=True,
                    message="Item removed from cart successfully.",
                    cart=cart  # Returning updated cart object
                )
            except CartItem.DoesNotExist:
                raise GraphQLError("Item not found in cart.")
        else:
            # Guest user
            cart = info.context.session.get('cart', {})
            if str(product_variant_id) in cart:
                del cart[str(product_variant_id)]
                save_guest_cart(info.context, cart)
                return RemoveFromCartMutation(
                    success=True,
                    message="Item removed from cart successfully.",
                    cart=cart  # Returning updated cart
                )
            else:
                raise GraphQLError("Item not found in cart.")


class CartMutation(graphene.ObjectType):
    add_to_cart = AddToCartMutation.Field()
    update_cart_item = UpdateCartItemMutation.Field()
    remove_from_cart = RemoveFromCartMutation.Field()

