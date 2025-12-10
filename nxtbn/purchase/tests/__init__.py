import factory
from faker import Faker
from nxtbn.product.tests import ProductVariantFactory, SupplierFactory
from nxtbn.purchase.models import PurchaseOrder, PurchaseOrderItem
from nxtbn.users.tests import UserFactory
from nxtbn.warehouse.tests import WarehouseFactory


fake = Faker()

class PurchaseOrderFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PurchaseOrder

    supplier = factory.SubFactory(
        SupplierFactory
    )
    destination = factory.SubFactory(
        WarehouseFactory
    )
    expected_delivery_date = factory.Faker('date_this_year', before_today=False, after_today=True)
    created_by = factory.SubFactory(
        UserFactory
    )
    total_cost = factory.Faker('pydecimal', left_digits=7, right_digits=2, positive=True)



class PurchaseOrderItemFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PurchaseOrderItem

    purchase_order = factory.SubFactory(PurchaseOrderFactory)
    variant = factory.SubFactory(
        ProductVariantFactory
    )
    ordered_quantity = factory.Faker('random_int', min=1, max=100)
    received_quantity = factory.Faker('random_int', min=0, max=50)
    rejected_quantity = factory.Faker('random_int', min=0, max=10)
    unit_cost = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
