import graphene
from graphene_django import DjangoObjectType
from nxtbn.order.models import Address

class AddressGraphType(DjangoObjectType):
    db_id = graphene.Int(source='id')
    class Meta:
        model = Address
        fields = (
            'id',
            'first_name',
            'last_name',
            'street_address',
            'city',
            'postal_code',
            'country',
            'phone_number',
            'email',
            'address_type',
        )
