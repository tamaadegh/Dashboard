import graphene
from graphene import relay

from graphene_django.types import DjangoObjectType
from nxtbn.cart.models import Cart, CartItem
from nxtbn.users.admin_types import AdminUserType


class CartItemType(DjangoObjectType):
    db_id = graphene.ID(source='id')
    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'variant', 'quantity', 'created_at', 'last_modified')


class CartType(DjangoObjectType):
    user = AdminUserType()
    total_items = graphene.Int()
    db_id = graphene.ID(source='id')
    abandoned_at = graphene.DateTime()
    class Meta:
        model = Cart
        fields = '__all__'
        interfaces = (relay.Node,)
        filter_fields = {
            'user__id': ['exact'],
        }

    def resolve_total_items(self, info):
        return sum(item.quantity for item in self.items.all())
    
    def resolve_abandoned_at(self, info):
        if self.last_modified:
            return self.last_modified
        return self.created_at


