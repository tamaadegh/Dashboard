import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from django_countries.fields import CountryField

from nxtbn.tax.models import TaxClass, TaxRate

faker = Faker()

class TaxClassFactory(DjangoModelFactory):
    """
    Factory for the TaxClass model.
    """
    class Meta:
        model = TaxClass

    name = factory.LazyAttribute(lambda _: faker.word().capitalize())


class TaxRateFactory(DjangoModelFactory):
    """
    Factory for the TaxRate model.
    """
    class Meta:
        model = TaxRate

    country = factory.LazyAttribute(lambda _: faker.country_code())
    state = factory.LazyAttribute(lambda _: faker.state_abbr() if faker.boolean() else None)
    rate = factory.LazyAttribute(lambda _: Decimal(faker.random_int(min=1, max=25)))
    tax_class = factory.SubFactory(TaxClassFactory)
    is_active = factory.LazyAttribute(lambda _: faker.boolean(chance_of_getting_true=80))
