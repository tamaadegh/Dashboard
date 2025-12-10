import random
from django.db.models import Sum
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from nxtbn.product.models import ProductVariant
from nxtbn.users.models import User
from nxtbn.order.models import OrderLineItem
from nxtbn.warehouse.models import Warehouse, Stock, StockReservation, StockTransfer, StockTransferItem

fake = Faker()


class WarehouseFactory(DjangoModelFactory):
    class Meta:
        model = Warehouse

    name = factory.Faker("company")
    location = factory.Faker("address")
    is_default = factory.Faker("boolean")


class StockFactory(DjangoModelFactory):
    class Meta:
        model = Stock

    warehouse = factory.SubFactory(WarehouseFactory)
    product_variant = factory.SubFactory("nxtbn.product.tests.ProductVariantFactory") 
    quantity = factory.Faker("random_int", min=0, max=100)
    reserved = factory.LazyAttribute(lambda obj: random.randint(0, obj.quantity))


class StockReservationFactory(DjangoModelFactory):
    class Meta:
        model = StockReservation

    stock = factory.SubFactory(StockFactory)
    quantity = factory.LazyAttribute(lambda obj: random.randint(1, obj.stock.quantity - obj.stock.reserved))
    purpose = factory.Faker("sentence", nb_words=3)
    order_line = factory.SubFactory("nxtbn.order.tests.OrderLineItemFactory") 


class StockTransferFactory(DjangoModelFactory):
    class Meta:
        model = StockTransfer

    from_warehouse = factory.SubFactory(WarehouseFactory)
    to_warehouse = factory.SubFactory(WarehouseFactory)
    status = factory.Faker("random_element", elements=["Pending", "Completed", "Cancelled"]) 
    created_by = factory.SubFactory("nxtbn.users.tests.UserFactory") 

class StockTransferItemFactory(DjangoModelFactory):
    class Meta:
        model = StockTransferItem

    stock_transfer = factory.SubFactory(StockTransferFactory)
    variant = factory.SubFactory("nxtbn.product.tests.ProductVariantFactory") 
    quantity = factory.Faker("random_int", min=1, max=50)
