import random
from decimal import Decimal
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import build_currency_amount, normalize_amount_currencywise
from nxtbn.discount import PromoCodeType
from nxtbn.discount.tests import PromoCodeFactory
from nxtbn.home.base_tests import BaseTestCase
from nxtbn.product.models import Product
from nxtbn.product.tests import ProductFactory, ProductTypeFactory, ProductVariantFactory
from babel.numbers import get_currency_precision

from django.test.utils import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderCreateWithDiscountManually(BaseTestCase): # admin_order_create
    def setUp(self):
        super().setUp()
        self.adminLogin()

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))

        self.test_cases = {
            '2': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50.29,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': '100.00',
                },
            },
            '3': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50.290,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': '140.000',
                },
            },
            '0': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': 100,
                },
            },
        }

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def _run_fixed_discount_test(self):
        """
        Run discount calculation test for fixed discount type
        """

        currency = settings.BASE_CURRENCY

        product_type = ProductTypeFactory(
            name=f"{currency} Product Type physical",
            track_stock=False,
            taxable=False,
            physical_product=True,
        )

        product = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant = ProductVariantFactory(
            product=product,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_price'], currency),
            cost_per_unit=50.00,
            weight_value=self.test_cases[self.precision]['variant_weight_value'],
        )

        order_payload = {
            "shipping_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "billing_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "custom_discount_amount": self.test_cases[self.precision]['custom_discount_amount'],
            "variants": [
                {
                    "alias": variant.alias,
                    "quantity": self.test_cases[self.precision]['variant_order_quantity'],
                }
            ]
        }

        subtotal = Decimal(
            self.test_cases[self.precision]['variant_price'] * self.test_cases[self.precision]['variant_order_quantity']
        )

        total_discount = Decimal(self.test_cases[self.precision]['custom_discount_amount']['price'])
        expected_total = subtotal - total_discount

        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(subtotal, currency, locale='en_US')
        expected_total_discount_fr = build_currency_amount(total_discount, currency, locale='en_US')

        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json')

        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_estimate_response.data['total'], expected_total_fr)
        self.assertEqual(order_estimate_response.data['discount'], expected_total_discount_fr)

        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_response.data['total'], expected_total_fr)
        self.assertEqual(order_response.data['discount'], expected_total_discount_fr)

    def test_order_discount_calculation_fixed(self):
        """
        Test order discount calculation for fixed amount discount
        """
        self._run_fixed_discount_test()




class TestOrderCreateWithDiscountManuallyAsCustomer(BaseTestCase): # as customer to check permssion of the serializer field: custom_discount_amount
    def setUp(self):
        super().setUp()
        self.customerLogin()

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))

        self.test_cases = {
            '2': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50.29,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': '100.00',
                },
            },
            '3': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50.290,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': '140.000',
                },
            },
            '0': {
                'input_weight_min': 0,
                'input_weight_max': 5,
                'variant_price': 50,
                'variant_weight_value': 100,
                'variant_order_quantity': 40,
                'custom_discount_amount': {
                    'name': 'Custom Discount',
                    'price': 100,
                },
            },
        }

        self.order_api_url = reverse('order_create')
        self.order_estimate_api_url = reverse('order_estimate')

    def _run_fixed_discount_test(self):
        """
        Run discount calculation test for fixed discount type
        """

        currency = settings.BASE_CURRENCY

        product_type = ProductTypeFactory(
            name=f"{currency} Product Type physical",
            track_stock=False,
            taxable=False,
            physical_product=True,
        )

        product = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant = ProductVariantFactory(
            product=product,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_price'], currency),
            cost_per_unit=50.00,
            weight_value=self.test_cases[self.precision]['variant_weight_value'],
        )

        order_payload = {
            "shipping_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "billing_address": {
                "country": self.country,
                "state": self.state,
                "street_address": "123 Main St",
                "city": "New York",
                "postal_code": "10001",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "1234567890"
            },
            "custom_discount_amount": self.test_cases[self.precision]['custom_discount_amount'],
            "variants": [
                {
                    "alias": variant.alias,
                    "quantity": self.test_cases[self.precision]['variant_order_quantity'],
                }
            ]
        }

        subtotal = Decimal(
            self.test_cases[self.precision]['variant_price'] * self.test_cases[self.precision]['variant_order_quantity']
        )

        total_discount = Decimal(self.test_cases[self.precision]['custom_discount_amount']['price'])
        expected_total = subtotal - total_discount

        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(subtotal, currency, locale='en_US')
        expected_total_discount_fr = build_currency_amount(total_discount, currency, locale='en_US')

        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json')

        self.permissionDenied(order_estimate_response)

        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json')
        self.permissionDenied(order_response)

    def test_order_discount_calculation_fixed(self):
        """
        Test order discount calculation for fixed amount discount
        """
        self._run_fixed_discount_test()
