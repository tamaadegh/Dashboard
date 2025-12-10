from django.conf import settings
import graphene
from graphene_django import DjangoObjectType
from graphene import relay
from nxtbn.core.utils import apply_exchange_rate
from django.utils.translation import get_language

from nxtbn.product.storefront_types import ProductVariantType


class CartItemType(graphene.ObjectType):
    product_variant = graphene.Field(ProductVariantType)
    quantity = graphene.Int()
    subtotal = graphene.String()


class CartType(graphene.ObjectType):
    items = graphene.List(CartItemType)
    total = graphene.String()