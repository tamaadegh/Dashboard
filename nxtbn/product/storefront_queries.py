from django.conf import settings
import graphene
from nxtbn.cart.utils import get_or_create_cart
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import apply_exchange_rate
from nxtbn.product.storefront_types import (
    CategoryHierarchicalType,
    ProductGraphType,
    ImageType,
    CategoryType,
    SupplierType,
    ProductTypeType,
    CollectionType,
    ProductTagType,
    TaxClassType,
)
from nxtbn.product.models import Product, Image, Category, ProductVariant, Supplier, ProductType, Collection, ProductTag, TaxClass
from graphene_django.filter import DjangoFilterConnectionField
from nxtbn.core.currency.backend import currency_Backend



class ProductQuery(graphene.ObjectType):
    product = graphene.Field(ProductGraphType, slug=graphene.String())
    products = DjangoFilterConnectionField(ProductGraphType)

    categories = DjangoFilterConnectionField(CategoryType)
    categories_hierarchical = DjangoFilterConnectionField(CategoryHierarchicalType)

    collections = DjangoFilterConnectionField(CollectionType)
    tags = DjangoFilterConnectionField(ProductTagType)

    def resolve_product(root, info, slug):
        exchange_rate = 1.0
        if settings.IS_MULTI_CURRENCY:
            exchange_rate = currency_Backend().get_exchange_rate(info.context.currency)
        
        info.context.exchange_rate = exchange_rate
        
        try:
            return Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return None

    def resolve_products(root, info, **kwargs):
        exchange_rate = 1.0
        if settings.IS_MULTI_CURRENCY:
            exchange_rate = currency_Backend().get_exchange_rate(info.context.currency)
        
        info.context.exchange_rate = exchange_rate

        return Product.objects.filter(status=PublishableStatus.PUBLISHED).order_by('-created_at')
    
    def resolve_categories_hierarchical(root, info, **kwargs):
        return Category.objects.filter(parent=None)