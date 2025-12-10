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
import datetime
from django.test.utils import override_settings
from nxtbn.warehouse.models import Stock
from nxtbn.warehouse.tests import StockFactory, WarehouseFactory
from datetime import date


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class PurchageCreateUpdateAPITest(BaseTestCase):
   
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

       

    def test_purchase_create_update(self):
        """Test case for create purchase order"""
        purchase_create_url = reverse('purchaseorder-list')

        payload = {
            "supplier": self.supplier.id,
            "destination": self.warehouse.id,
            "expected_delivery_date": (datetime.datetime.now()+datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
            "items": [
                {
                    "ordered_quantity": 0,
                    "unit_cost": self.product_variant_one.cost_per_unit,
                    "variant": self.product_variant_one.id
                },
                {
                    "ordered_quantity": 5,
                    "unit_cost": self.product_variant_two.cost_per_unit,
                    "variant": self.product_variant_two.id
                },
                {
                    "ordered_quantity": 0,
                    "unit_cost": self.product_variant_three.cost_per_unit,
                    "variant": self.product_variant_three.id
                },
                {
                    "ordered_quantity": 100,
                    "unit_cost": self.product_variant_four.cost_per_unit,
                    "variant": self.product_variant_four.id
                },
            ]
        }
        response_purchase_create = self.auth_client.post(purchase_create_url, payload, format='json')
        self.assertEqual(response_purchase_create.status_code, status.HTTP_201_CREATED)


        purchase_order_id = response_purchase_create.json()['id']
        purchase_detail_url = reverse('purchaseorder-detail', kwargs={'pk': purchase_order_id})

        updated_payload = {
            "supplier": self.supplier.id,
            "destination": self.warehouse.id,
            "expected_delivery_date": (datetime.datetime.now()+datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
            "items": [
                {
                    "ordered_quantity": 10,
                    "unit_cost": self.product_variant_one.cost_per_unit,
                    "variant": self.product_variant_one.id
                },
                {
                    "ordered_quantity": 300,
                    "unit_cost": self.product_variant_two.cost_per_unit,
                    "variant": self.product_variant_two.id
                },
            ]
        }
        response_purchase_update = self.auth_client.put(purchase_detail_url, updated_payload, format='json')
        self.assertEqual(response_purchase_update.status_code, status.HTTP_200_OK)
        
        purchase_detail_response = self.auth_client.get(purchase_detail_url, format='json')
        self.assertEqual(len(purchase_detail_response.json()["items"]), 2)

        self.assertEqual(purchase_detail_response.json()["items"][0]["ordered_quantity"], 10)
        self.assertEqual(purchase_detail_response.json()["items"][1]["ordered_quantity"], 300)
        self.assertEqual(purchase_detail_response.json()["items"][0]['variant']['id'], self.product_variant_one.id)

       
        with self.assertRaises(PurchaseOrderItem.DoesNotExist):
            PurchaseOrderItem.objects.get(purchase_order_id=purchase_order_id, variant=self.product_variant_three.id)


    def test_puchase_create_with_blank_items(self):
        purchase_create_url = reverse('purchaseorder-list')

        payload = {
            "supplier": self.supplier.id,
            "destination": self.warehouse.id,
            "expected_delivery_date": (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d'), # invalid date
            "items": [] # blank item
        }
        response_purchase_create = self.auth_client.post(purchase_create_url, payload, format='json')
        self.assertEqual(response_purchase_create.status_code, status.HTTP_400_BAD_REQUEST)