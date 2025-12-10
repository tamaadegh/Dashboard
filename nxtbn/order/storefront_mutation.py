import graphene

from nxtbn.order.proccesor.storefront_mutation import OrderProcessMutation
from nxtbn.order import AddressType
from nxtbn.order.models import Address
from nxtbn.order.storefront_types import AddressGraphType



class CreateAddressMutation(graphene.Mutation):
    address = graphene.Field(AddressGraphType)

    class Arguments:
        street_address = graphene.String(required=True)
        city = graphene.String(required=True)
        state = graphene.String(required=True)
        postal_code = graphene.String(required=True)
        country = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        phone_number = graphene.String()
        email = graphene.String()
        address_type = graphene.String(default_value=AddressType.DSA_DBA)

    def mutate(self, info, street_address, city, state, postal_code, country, first_name, last_name, 
               phone_number=None, email=None, address_type=AddressType.DSA_DBA):
        # Get the current user from the context
        user = info.context.user

        # Check if the user is authenticated
        if not user.is_authenticated:
            raise Exception("User is not authenticated")

        # Create the Address instance
        address = Address.objects.create(
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            address_type=address_type
        )

        return CreateAddressMutation(address=address)


class OrderMutation(graphene.ObjectType):
    order_process = OrderProcessMutation.Field()
    create_address = CreateAddressMutation.Field()


