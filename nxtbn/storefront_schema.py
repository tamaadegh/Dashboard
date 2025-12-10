import graphene

from nxtbn.cart.storefront_mutation import CartMutation
from nxtbn.order.storefront_mutation import OrderMutation
from nxtbn.order.storefront_queries import OrderQuery
from nxtbn.users.storefront_mutation import UserMutation

from nxtbn.product.storefront_queries import ProductQuery
from nxtbn.cart.storefront_queries import CartQuery



class Query(ProductQuery, CartQuery):
    pass

class Mutation(CartMutation, OrderMutation, UserMutation, OrderQuery):
    pass

storefront_schema = graphene.Schema(query=Query, mutation=Mutation)
