import graphene



class VariantQuantityInput(graphene.InputObjectType):
    alias = graphene.String(required=True)
    quantity = graphene.Int(required=True)


class PriceAndNameInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.String(required=True)


class ShippingAddressInput(graphene.InputObjectType):
    city = graphene.String()
    postal_code = graphene.String()
    country = graphene.String()
    state = graphene.String()
    street_address = graphene.String()
    email = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    phone_number = graphene.String()


class OrderEstimateInput(graphene.InputObjectType):
    shipping_address = ShippingAddressInput()
    billing_address = ShippingAddressInput()
    shipping_address_id = graphene.Int()
    billing_address_id = graphene.Int()

    shipping_method_id = graphene.Int()
    promocode = graphene.String()
    variants = graphene.List(VariantQuantityInput, required=True)
    note = graphene.String()
    create_order = graphene.Boolean(default_value=False) # if false, it will eastimate the order only
