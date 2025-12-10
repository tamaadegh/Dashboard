import random
from django.conf import settings
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from nxtbn.core.utils import normalize_amount_currencywise
from nxtbn.filemanager.tests import ImageFactory
from nxtbn.product.models import (
    Supplier, Color, Category, Collection, ProductTag, ProductType, Product, ProductVariant
)
from nxtbn.users.models import User
from nxtbn.filemanager.models import Image
from nxtbn.tax.models import TaxClass
from nxtbn.users.tests import UserFactory

fake = Faker()




# Supplier Factory
class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Faker("company")
    description = factory.Faker("catch_phrase")


# Color Factory
class ColorFactory(DjangoModelFactory):
    class Meta:
        model = Color

    name = factory.Faker("color_name")
    code = factory.Faker("hex_color")


# Category Factory
class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name =  factory.LazyAttribute(lambda o: f"{fake.word()} {fake.word()}")
    description = factory.Faker("sentence")
    # parent = factory.Maybe(
    #     factory.Faker("boolean"),
    #     yes_declaration=factory.SubFactory('self'),
    #     no_declaration=None
    # )

# Collection Factory
class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = Collection

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    is_active = True
    created_by = factory.SubFactory(UserFactory)
    last_modified_by = factory.SubFactory(UserFactory)
    # image = factory.SubFactory(ImageFactory, nullable=True)


# Product Tag Factory
class ProductTagFactory(DjangoModelFactory):
    class Meta:
        model = ProductTag

    name = factory.Faker("word")


# Product Type Factory
class ProductTypeFactory(DjangoModelFactory):
    class Meta:
        model = ProductType

    name = factory.LazyAttribute(lambda o: f"{fake.word()} {fake.word()}")
    taxable = fake.boolean()
    physical_product = fake.boolean()
    track_stock = fake.boolean()
    has_variant = fake.boolean()


# Product Factory
class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.LazyAttribute(lambda o: f"{fake.word()} {fake.word()}")
    summary = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    created_by = factory.SubFactory(UserFactory)
    last_modified_by = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    supplier = factory.SubFactory(SupplierFactory)
    product_type = factory.SubFactory(ProductTypeFactory)

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.images.add(*extracted)
        else:
            # Add random images
            for _ in range(3):
                self.images.add(ImageFactory())


# Product Variant Factory
class ProductVariantFactory(DjangoModelFactory):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    name = factory.Faker("word")
    sku = factory.Faker("ean13")
    price = normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY)
    cost_per_unit = normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY)
    currency = settings.BASE_CURRENCY
    # stock = factory.Faker("random_int", min=0, max=100)
    track_inventory = fake.boolean()