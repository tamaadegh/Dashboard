# test case for single currency mode
import random
import sys
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import normalize_amount_currencywise
from nxtbn.home.base_tests import BaseTestCase
from nxtbn.product.models import Product, ProductType
from rest_framework.test import APIClient
from nxtbn.product.tests import ProductFactory, ProductTypeFactory, ProductVariantFactory
from nxtbn.tax.tests import TaxClassFactory, TaxRateFactory

# ======================================================================================================================
# Test Case for Order Create API with a single product/variant in a single currency mode.
# Ensures accuracy in calculations for Taxable, and non-trackable stock products.
# ======================================================================================================================

from django.test.utils import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class OrderCreateTaxableProductNoTrackingStockAPI(BaseTestCase): # Single currency mode either USD, JPY, KWD
    
    """
        Test Case for Order Create API with multiple currencies: USD, JPY, KWD.

        This test suite ensures the accuracy of calculations and multi-precision handling for different currencies.
        It covers tax calculation and non-trackable stock products in a single currency mode.
        TODO: Add support for multi-currency mode.
    """

    def setUp(self):
        super().setUp()
        self.adminLogin()

        # Define common properties
        self.country = 'US'
        self.state = 'NY'

        # Tax class
        self.tax_class = TaxClassFactory()

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def _test_order_for_currency(self, currency, params):
        """
        Helper method to test order create and estimate for a specific currency.
        Dynamically creates a variant based on provided params.
        """
        # Set up tax rate
        tax_rate = TaxRateFactory(
            tax_class=self.tax_class,
            is_active=True,
            rate=params['tax_rate'],
            country=self.country,
            state=self.state,
        )

        # Create product type and product
        product_type = ProductTypeFactory(
            name=f"{currency} Product Type non trackable and taxable",
            track_stock=False,
            taxable=True,
        )
        product = ProductFactory(
            product_type=product_type,
            tax_class=self.tax_class,
            status=PublishableStatus.PUBLISHED,
        )

        # Create variant
        variant = ProductVariantFactory(
            product=product,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(params['price'], currency),
            # stock=params['stock'],
            cost_per_unit=params['cost_per_unit'],
        )

        # Payload for order
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
            "variants": [
                {
                    "alias": variant.alias,
                    "quantity": 3,
                }
            ]
        }

        # Estimate Test
        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY,})
        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_estimate_response.data['total'], params['total'])
        self.assertEqual(order_estimate_response.data['estimated_tax'], params['tax'])

        # Order Create Test
        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY,})
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_response.data['total'], params['total'])
        self.assertEqual(order_response.data['estimated_tax'], params['tax'])

    def test_order_for_all_currencies(self):
        """
        Test order creation and estimation for all currencies: USD, JPY, KWD.
        """
        # USD Test
        if settings.BASE_CURRENCY == 'USD':
            self._test_order_for_currency(
                "USD",
                {
                    # Expected output
                    "subtotal": "$60.78",
                    "total": "$69.90",
                    "tax": "$9.12",

                    # Variant creation parameters
                    "price": 20.26,
                    "cost_per_unit": 50.00,
                    "tax_rate": 15,  # 15%
                    # "stock": 10,
                },
            )

        # JPY Test
        if settings.BASE_CURRENCY == 'JPY':
            self._test_order_for_currency(
                "JPY",
                {
                    # Expected output
                    "subtotal": "¥6,000",
                    "total": "¥6,900",
                    "tax": "¥900",

                    # Variant creation parameters
                    "price": 2000,
                    "cost_per_unit": 5000,
                    "tax_rate": 15,  # 15%
                    # "stock": 10,
                },
            )

        if settings.BASE_CURRENCY == 'KWD':
            self._test_order_for_currency(
                "KWD",
                {
                    # Expected output
                    "subtotal": "KWD60.702",
                    "total": "KWD69.807",
                    "tax": "KWD9.105",

                    # Variant creation parameters
                    "price": 20.234,
                    "cost_per_unit": 15.500,
                    "tax_rate": 15,  # 15%
                    # "stock": 10,
                },
            )

        # if not USD, JPY, KWD, skip the test as these 3 currencies are enough to test multi-currency handling as they have different precision


# ======================================================================================================================
# Test Case for Order Create API with multiple products/variants in a single currency mode.
# Ensures accuracy in calculations for mixed tax rates, non-taxable products, and non-trackable stock products.
# ======================================================================================================================



@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class OrderCreateTaxableMultiVariantNoTrackingStockAPI(BaseTestCase):
    """
        Test Case for Order Create API with multiple products/variants in a single currency mode.
        Ensures accuracy in calculations for mixed tax rates, non-taxable products, and non-trackable stock products.
    """

    def setUp(self):
        super().setUp()
        self.adminLogin()
        # Define common properties
        self.country = 'US'
        self.state = 'NY'

        # Tax classes
        self.tax_class_15 = TaxClassFactory()
        self.tax_class_5 = TaxClassFactory()

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def _test_order_with_multi_variant(self, currency, params):
        """
        Helper method to test order creation and estimation for multiple variants.
        """
        # Set up tax rates
        TaxRateFactory(
            tax_class=self.tax_class_15,
            is_active=True,
            rate=15,  # 15%
            country=self.country,
            state=self.state,
        )

        TaxRateFactory(
            tax_class=self.tax_class_5,
            is_active=True,
            rate=5,  # 5%
            country=self.country,
            state=self.state,
        )

        # Create products
        product_1 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non trackable, taxable 15%",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_15,
            status=PublishableStatus.PUBLISHED,
        )

        product_2 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non trackable, non-taxable",
                track_stock=False,
                taxable=False,
            ),
            tax_class=None,
            status=PublishableStatus.PUBLISHED,
        )

        product_3 = ProductFactory(
            product_type=ProductTypeFactory(
                name=f"{currency} Product Type non trackable, taxable 5%",
                track_stock=False,
                taxable=True,
            ),
            tax_class=self.tax_class_5,
            status=PublishableStatus.PUBLISHED,
        )

        # Create variants
        variant_1 = ProductVariantFactory(
            product=product_1,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(params['variant_1']['price'], currency),
            # stock=params['variant_1']['stock'],
            cost_per_unit=params['variant_1']['cost_per_unit'],
        )

        variant_2 = ProductVariantFactory(
            product=product_2,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(params['variant_2']['price'], currency),
            # stock=params['variant_2']['stock'],
            cost_per_unit=params['variant_2']['cost_per_unit'],
        )

        variant_3 = ProductVariantFactory(
            product=product_3,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(params['variant_3']['price'], currency),
            # stock=params['variant_3']['stock'],
            cost_per_unit=params['variant_3']['cost_per_unit'],
        )

        # Payload for order
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
            "variants": [
                {"alias": variant_1.alias, "quantity": 2},
                {"alias": variant_2.alias, "quantity": 3},
                {"alias": variant_3.alias, "quantity": 1},
            ]
        }

        # Estimate Test
        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_estimate_response.data['total'], params['total'])
        self.assertEqual(order_estimate_response.data['estimated_tax'], params['tax'])

        # Order Create Test
        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json', headers={'Accept-Currency': settings.BASE_CURRENCY})
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], params['subtotal'])
        self.assertEqual(order_response.data['total'], params['total'])
        self.assertEqual(order_response.data['estimated_tax'], params['tax'])

    def test_order_with_multi_variant(self):
        """
        Test order creation and estimation with multiple products/variants for single currency mode.
        """
        # USD Test
        if settings.BASE_CURRENCY == 'USD':
            self._test_order_with_multi_variant(
                "USD",
                {
                    "subtotal": "$235.50",
                    "total": "$252.78", # rounded to 2 decimal places, that is why it is not 252.775
                    "tax": "$17.28", # rounded to 2 decimal places, that is why it is not 17.275
                    "variant_1": {"price": 50.00, "cost_per_unit": 40.00, "stock": 10}, # will be ordered 2 times, Taxable 15%
                    "variant_2": {"price": 30.00, "cost_per_unit": 25.00, "stock": 10}, # will be ordered 3 times, Non-taxable
                    "variant_3": {"price": 45.50, "cost_per_unit": 35.00, "stock": 10}, # will be ordered 1 time, Taxable 5%
                },
            )

        # JPY Test
        if settings.BASE_CURRENCY == 'JPY':
            self._test_order_with_multi_variant(
                "JPY",
                {
                    "subtotal": "¥23,550", 
                    "total": "¥25,278", # rounded to 0 decimal places
                    "tax": "¥1,728", # rounded to 0 decimal places
                    "variant_1": {"price": 5000, "cost_per_unit": 4000, "stock": 10}, # will be ordered 2 times, Taxable 15%
                    "variant_2": {"price": 3000, "cost_per_unit": 2500, "stock": 10}, # will be ordered 3 times, Non-taxable
                    "variant_3": {"price": 4550, "cost_per_unit": 3500, "stock": 10}, # will be ordered 1 time, Taxable 5%
                },
            )

        # KWD Test
        if settings.BASE_CURRENCY == 'KWD':
            self._test_order_with_multi_variant(
                "KWD",
                {
                    "subtotal": "KWD235.500",
                    "total": "KWD252.775", # rounded to 3 decimal places, that is why it is not 252.78
                    "tax": "KWD17.275", # rounded to 3 decimal places, that is why it is not 17.28
                    "variant_1": {"price": 50.000, "cost_per_unit": 40.000, "stock": 10}, # will be ordered 2 times, Taxable 15%
                    "variant_2": {"price": 30.000, "cost_per_unit": 25.000, "stock": 10}, # will be ordered 3 times, Non-taxable
                    "variant_3": {"price": 45.500, "cost_per_unit": 35.000, "stock": 10}, # will be ordered 1 time, Taxable 5%
                },
            )

    # if not USD, JPY, KWD, skip the test as these 3 currencies are enough to test multi-currency handling as they have different precision