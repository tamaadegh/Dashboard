import graphene

from nxtbn.order.storefront_types import AddressGraphType
from nxtbn.order.models import Address


class OrderQuery(graphene.ObjectType):
    addresses = graphene.List(AddressGraphType)
    address = graphene.Field(AddressGraphType, id=graphene.Int(required=True))

    def resolve_addresses(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        return Address.objects.filter(user=user)

    def resolve_address(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        try:
            address = Address.objects.get(id=id, user=user)
        except Address.DoesNotExist:
            raise Exception("Address not found")
        
        return address
