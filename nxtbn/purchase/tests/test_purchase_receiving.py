import random
from decimal import Decimal
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import build_currency_amount, normalize_amount_currencywise
from nxtbn.home.base_tests import BaseTestCase
from nxtbn.order.proccesor.views import get_shipping_rate_instance
from nxtbn.product import WeightUnits
from nxtbn.product.models import Product
from rest_framework.test import APIClient
from nxtbn.product.tests import ProductFactory, ProductTypeFactory, ProductVariantFactory, SupplierFactory
from nxtbn.purchase import PurchaseStatus
from nxtbn.purchase.models import PurchaseOrderItem
from nxtbn.purchase.tests import PurchaseOrderFactory, PurchaseOrderItemFactory
from nxtbn.shipping.models import ShippingRate
from nxtbn.shipping.tests import ShippingMethodFactory, ShippingRateFactory
from nxtbn.tax.tests import TaxClassFactory, TaxRateFactory
from babel.numbers import get_currency_precision, format_currency


from django.test.utils import override_settings

from nxtbn.warehouse.models import Stock
from nxtbn.warehouse.tests import StockFactory, WarehouseFactory


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PurchangeOrderReceivingTest(BaseTestCase):
   
    def setUp(self):
        super().setUp()
        self.adminLogin()

        self.supplier = SupplierFactory()
        self.warehouse = WarehouseFactory()
        self.product = ProductFactory()
        self.product_variant_one = ProductVariantFactory(
            product=self.product,
            price=Decimal('100.00'),
            cost_per_unit=Decimal('100.00')
        )
        self.product_variant_two = ProductVariantFactory(
            product=self.product,
            price=Decimal('100.00'),
            cost_per_unit=Decimal('100.00')
        )
        self.product_variant_three = ProductVariantFactory(
            product=self.product,
            price=Decimal('100.00'),
            cost_per_unit=Decimal('100.00')
        )
        self.product_variant_four = ProductVariantFactory(
            product=self.product,
            price=Decimal('100.00'),
            cost_per_unit=Decimal('100.00')
        )

        self.purchange = PurchaseOrderFactory(
            supplier=self.supplier,
            destination=self.warehouse,
            created_by=self.user,
            status=PurchaseStatus.DRAFT
        )

        # Purchase Order Items

        self.purchage_item_one = PurchaseOrderItemFactory(
            purchase_order=self.purchange,
            variant=self.product_variant_one,
            ordered_quantity=10,
            received_quantity=0,
            rejected_quantity=0,
            unit_cost=Decimal('100.00')
        )
        self.purchage_item_two = PurchaseOrderItemFactory(
            purchase_order=self.purchange,
            variant=self.product_variant_two,
            ordered_quantity=8,
            received_quantity=0,
            rejected_quantity=0,
            unit_cost=Decimal('100.00')
        )
        self.purchage_item_three = PurchaseOrderItemFactory(
            purchase_order=self.purchange,
            variant=self.product_variant_three,
            ordered_quantity=3,
            received_quantity=0,
            rejected_quantity=0,
            unit_cost=Decimal('100.00')
        )
        self.purchage_item_four = PurchaseOrderItemFactory(
            purchase_order=self.purchange,
            variant=self.product_variant_four,
            ordered_quantity=250,
            received_quantity=0,
            rejected_quantity=0,
            unit_cost=Decimal('100.00')
        )

        # # stock
        # self.stock_one = StockFactory(
        #     warehouse=self.warehouse,
        #     product_variant=self.product_variant_one,
        #     quantity=0,
        #     reserved=0,
        #     incoming=0
        # )
        # self.stock_two = StockFactory(
        #     warehouse=self.warehouse,
        #     product_variant=self.product_variant_two,
        #     quantity=0,
        #     reserved=0,
        #     incoming=0
        # )
        # self.stock_three = StockFactory(
        #     warehouse=self.warehouse,
        #     product_variant=self.product_variant_three,
        #     quantity=0,
        #     reserved=0,
        #     incoming=0
        # )
        self.stock_four = StockFactory(
            warehouse=self.warehouse,
            product_variant=self.product_variant_four,
            quantity=10,
            reserved=0,
            incoming=2
        )


       

    def test_purchange_receiving_update(self):

        # Mark the purchase as ordered
        mark_as_ordered_url = reverse('purchaseorder-mark-as-ordered', kwargs={'pk': self.purchange.pk})
        response = self.auth_client.patch(mark_as_ordered_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

  

        # validate stock incomming as purchase  marked as ordered
        stock_four = Stock.objects.get(pk=self.stock_four.pk)
        self.assertEqual(stock_four.incoming, 252)
        self.stock_three = Stock.objects.get(product_variant=self.product_variant_three, warehouse=self.warehouse)
        self.assertEqual(self.stock_three.incoming, 3)



        url = reverse('inventory-receiving', kwargs={'pk': self.purchange.pk})
        data_with_exed = { # expect error coz received_quantity is more than ordered_quantity
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 10,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 800, # error will be raised here
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 250,
                    'rejected_quantity': 0
                }
            ]
        }
        response = self.auth_client.put(url, data_with_exed, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        

    
        success_data = { # expect is successfull
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 5,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 200,
                    'rejected_quantity': 5
                }
            ]
        }
        response = self.auth_client.put(url, success_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # validate purchase order items
        purchase_item_four = PurchaseOrderItem.objects.get(pk=self.purchage_item_four.pk)
        self.assertEqual(purchase_item_four.received_quantity, 200)
        self.assertEqual(purchase_item_four.rejected_quantity, 5)


        reject_less_than_current_reject_data = { # expect Error
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 5,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 200,
                    'rejected_quantity': 3 # Previousely we rejected 5 but we now trying to reject 4 which should raise error.
                }
            ]
        }

        less_response = self.auth_client.put(url, reject_less_than_current_reject_data, format='json')
        self.assertEqual(less_response.status_code, status.HTTP_400_BAD_REQUEST)

        receive_less_than_current_reject_data = { # expect is Error
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 5,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 199, # Previousely we received 200 but we now trying to receive 199 which should raise error.
                    'rejected_quantity': 5
                }
            ]
        }

        receive_less_response = self.auth_client.put(url, receive_less_than_current_reject_data, format='json')
        self.assertEqual(receive_less_response.status_code, status.HTTP_400_BAD_REQUEST)

        receive_more_than_ordered_data = { # expect is Error
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 11, # Previousely we ordered 10 but we now trying to receive 11 which should raise error.
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 200,
                    'rejected_quantity': 5
                }
            ]
        }

        receive_more_response = self.auth_client.put(url, receive_more_than_ordered_data, format='json')
        self.assertEqual(receive_more_response.status_code, status.HTTP_400_BAD_REQUEST)

        receive_more_than_adjusted_data = { # expect is Error
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 5,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 200,
                    'rejected_quantity': 51 # Previousely we ordered 250 and received 200 but we now trying to reject 51 which should raise error.
                }
            ]
        }

        receive_more_adjusted_response = self.auth_client.put(url, receive_more_than_adjusted_data, format='json')
        self.assertEqual(receive_more_adjusted_response.status_code, status.HTTP_400_BAD_REQUEST)

        reject_more_than_adjusted_data = { # expect is Error
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 5,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 4,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 200,
                    'rejected_quantity': 250 # Previousely we ordered 250 and received 200 but we now trying to reject 250 which should raise error.
                }
            ]
        }

        reject_more_adjusted_response = self.auth_client.put(url, reject_more_than_adjusted_data, format='json')
        self.assertEqual(reject_more_adjusted_response.status_code, status.HTTP_400_BAD_REQUEST)

        # Mark the purchase as received and closed
        url_mark_as_received = reverse('purchaseorder-mark-as-received', kwargs={'pk': self.purchange.pk})
        response = self.auth_client.patch(url_mark_as_received, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # expect error because received quantity + rejected quantity and ordered quantity are not equal

        final_draft_data = { # expect success
            'items': [
                {
                    'id': self.purchage_item_one.pk,
                    'received_quantity': 10,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_two.pk,
                    'received_quantity': 8,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_three.pk,
                    'received_quantity': 3,
                    'rejected_quantity': 0
                },
                {
                    'id': self.purchage_item_four.pk,
                    'received_quantity': 210, 
                    'rejected_quantity': 40
                }
            ]
        }

        final_draft_response = self.auth_client.put(url, final_draft_data, format='json')
        self.assertEqual(final_draft_response.status_code, status.HTTP_200_OK)

        purchase_item_four = PurchaseOrderItem.objects.get(pk=self.purchage_item_four.pk)
        self.assertEqual(purchase_item_four.received_quantity, 210)
        self.assertEqual(purchase_item_four.rejected_quantity, 40)


        # Mark the purchase as received and closed
        url_mark_as_received = reverse('purchaseorder-mark-as-received', kwargs={'pk': self.purchange.pk})
        response = self.auth_client.patch(url_mark_as_received, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # validate stock incomming as purchase  marked as received
        stock_four = Stock.objects.get(pk=self.stock_four.pk)
        self.assertEqual(stock_four.incoming, 2)
        self.assertEqual(stock_four.quantity, 220)


        # as it is closed now we can not update it, so try to update it and expect error
        final_draft_response = self.auth_client.put(url, final_draft_data, format='json')
        self.assertEqual(final_draft_response.status_code, status.HTTP_400_BAD_REQUEST)