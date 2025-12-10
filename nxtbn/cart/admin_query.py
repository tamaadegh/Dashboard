import graphene
from graphene_django.filter import DjangoFilterConnectionField

from nxtbn.cart.models import Cart
from nxtbn.cart.admin_types import CartItemType, CartType
from nxtbn.core.admin_permissions import gql_store_admin_required


class AdminCartQuery(graphene.ObjectType):
    carts = DjangoFilterConnectionField(CartType)
    
    cart_by_user = graphene.Field(CartType, user_id=graphene.ID(required=True))
    
    items_in_cart = graphene.List(CartItemType, cart_id=graphene.ID(required=True))

    @gql_store_admin_required
    def resolve_carts(self, info, **kwargs):
        return Cart.objects.all()

    @gql_store_admin_required
    def resolve_cart_by_user(self, info, user_id):
        try:
            return Cart.objects.get(user_id=user_id)
        except Cart.DoesNotExist:
            return None

    @gql_store_admin_required
    def resolve_items_in_cart(self, info, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            return cart.items.all()
        except Cart.DoesNotExist:
            return None
