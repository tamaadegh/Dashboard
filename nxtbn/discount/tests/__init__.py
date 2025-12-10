import random
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory
from faker import Faker

from nxtbn.users.tests import UserFactory
from nxtbn.product.tests import ProductFactory
from nxtbn.discount.models import PromoCode, PromoCodeCustomer, PromoCodeProduct

fake = Faker()

class PromoCodeFactory(DjangoModelFactory):
    class Meta:
        model = PromoCode

    code = factory.LazyAttribute(lambda _: fake.lexify(text="PROMO??????").upper())
    description = factory.Faker("sentence")
    code_type = factory.Faker("random_element", elements=["PERCENTAGE", "FIXED"])
    value = factory.LazyAttribute(lambda _: Decimal(random.uniform(1, 50)))
    expiration_date = factory.LazyAttribute(
        lambda _: timezone.now() + timedelta(days=random.randint(1, 365))
    )
    is_active = factory.Faker("boolean", chance_of_getting_true=80)
    min_purchase_amount = factory.LazyAttribute(
        lambda _: Decimal(random.uniform(10, 500)) if fake.boolean() else None
    )
    min_purchase_period = factory.LazyAttribute(
        lambda _: timedelta(days=random.randint(7, 30)) if fake.boolean() else None
    )
    redemption_limit = factory.LazyAttribute(
        lambda _: random.randint(1, 100) if fake.boolean() else None
    )
    new_customers_only = factory.Faker("boolean", chance_of_getting_true=20)
    usage_limit_per_customer = factory.Faker("random_int", min=1, max=10)




class PromoCodeCustomerFactory(DjangoModelFactory):
    class Meta:
        model = PromoCodeCustomer

    promo_code = factory.SubFactory(PromoCodeFactory)
    customer = factory.SubFactory(UserFactory)


class PromoCodeProductFactory(DjangoModelFactory):
    class Meta:
        model = PromoCodeProduct

    promo_code = factory.SubFactory(PromoCodeFactory)
    product = factory.SubFactory(ProductFactory)
