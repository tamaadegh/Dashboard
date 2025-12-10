import random
from decimal import Decimal
from django.conf import settings
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from nxtbn.shipping.models import ShippingMethod, ShippingRate
from nxtbn.core import CurrencyTypes

fake = Faker()

# Shipping Method Factory
class ShippingMethodFactory(DjangoModelFactory):
    class Meta:
        model = ShippingMethod

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    carrier = factory.Faker("company")

# Shipping Rate Factory
class ShippingRateFactory(DjangoModelFactory):
    class Meta:
        model = ShippingRate

    shipping_method = factory.SubFactory(ShippingMethodFactory)
    country = factory.Faker("country_code")  # Generates a random ISO 3166-1 alpha-2 country code
    region = factory.Faker("word")
    city = factory.Faker("word")
    weight_min = factory.LazyFunction(lambda: Decimal(random.uniform(0.5, 10)).quantize(Decimal("0.01")))
    weight_max = factory.LazyAttribute(lambda o: o.weight_min + Decimal(random.uniform(1, 10)).quantize(Decimal("0.01")))
    rate = factory.LazyFunction(lambda: Decimal(random.uniform(5, 100)).quantize(Decimal("0.01")))
    incremental_rate = factory.LazyFunction(lambda: Decimal(random.uniform(0, 10)).quantize(Decimal("0.01")))
    currency = factory.LazyFunction(lambda: random.choice(CurrencyTypes.values))
