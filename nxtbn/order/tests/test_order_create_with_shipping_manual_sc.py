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
from nxtbn.product.tests import ProductFactory, ProductTypeFactory, ProductVariantFactory
from rest_framework.test import force_authenticate
from nxtbn.shipping.models import ShippingRate
from nxtbn.shipping.tests import ShippingMethodFactory, ShippingRateFactory
from nxtbn.tax.tests import TaxClassFactory
from babel.numbers import get_currency_precision, format_currency

from nxtbn.users import UserRole
from nxtbn.users.tests import UserFactory
from django.contrib.auth.hashers import make_password

from nxtbn.users.utils.jwt_utils import JWTManager



from django.test.utils import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class OrderCreateShippingRateManual(BaseTestCase): # as admin
    """
        Test case to ensure shipping rates are accurately calculated based on product weights, quantities, and regions.

        This test case calculates the following:

        1. **Subtotal**:
            - Variant One:
            - Price per unit: $50.29
            - Quantity: 40
            - Subtotal for Variant One: 50.29 * 40 = $2011.60
            - Variant Two:
            - Price per unit: $20.26
            - Quantity: 1
            - Subtotal for Variant Two: 20.26 * 1 = $20.26
            - **Total Subtotal**: $2011.60 + $20.26 = **$2031.86**

        2. **Shipping Cost**:
            - Variant One Weight:
            - Weight per unit: 100 grams
            - Quantity: 40
            - Total weight for Variant One: 100 * 40 = 4000 grams (4 kg)
            - Variant Two Weight:
            - Weight per unit: 578 grams
            - Quantity: 1
            - Total weight for Variant Two: 578 grams
            - **Total Weight**: 4 kg + 0.578 kg = **4.578 kg**
            - Shipping Method (DHL-DTH):
            - Weight Range: 0 to 5 kg
            - Base Rate: $15
            - Incremental Rate: $3 per kg (applies only for weight over 5 kg)
            - **Total Shipping Cost**: Since the total weight is 4.578 kg (within the 0-5 kg range), the shipping cost is simply the base rate of **$15** (no incremental rate applies).

        3. **Total**:
            - **Total** = Subtotal + Shipping Cost = $2031.86 + $15 = **$2046.86**

        The method ensures that:
        - Subtotal is correctly calculated by multiplying the price and quantity of each product variant.
        - Shipping cost is based on the total weight and the defined rate structure.
        - The total order cost is the sum of the subtotal and shipping cost.
    """
     
   
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.superAdminLogin()

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))


        self.test_cases = {
            '2': { # USD, EUR, BDT etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50.29,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.26,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount': {
                    'name': 'X-Example Shipping',
                    'price': 15, # $15 USD
                }
            },
            '3': { # KWD, OMR, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50.290,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.260,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount':  {
                    'name': 'X-Example Shipping',
                    'price': 300.000, # 300 KWD
                }
            },
            '0': { # JPY, KRW, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount': {
                    'name': 'X-Example Shipping',
                    'price': 2000, # 1500 JPY
                }
            },
        }

       
    
       

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def test_order_shipping_rate_calculation(self):
        """
        Test case to ensure shipping rates are accurately calculated based on product weights and regions.
        """
        currency = settings.BASE_CURRENCY

        # Create product type and products
        product_type = ProductTypeFactory(
            name=f"{currency} Product Type physical",
            track_stock=False,
            taxable=True,
            physical_product=True,
        )

        # Create products and variants
        product_one = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant_one = ProductVariantFactory(
            product=product_one,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_one_price'], currency),
            cost_per_unit=50.00,
            weight_value= self.test_cases[self.precision]['variant_one_wv'],
        )
        
        product_two = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant_two = ProductVariantFactory(
            product=product_two,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_two_price'], currency),
            cost_per_unit=50.00,
            weight_value=self.test_cases[self.precision]['variant_two_wv'],  # 578 grams
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
            'custom_shipping_amount': self.test_cases[self.precision]['custom_shipping_amount'],
            "variants": [
                {
                    "alias": variant_one.alias,
                    "quantity": self.test_cases[self.precision]['variant_one_oqty'],
                },
                {
                    "alias": variant_two.alias,
                    "quantity": self.test_cases[self.precision]['variant_two_oqty'],
                }
            ]
        }

        # Expected values
        total_weight = Decimal(
            (self.test_cases[self.precision]['variant_one_oqty'] * self.test_cases[self.precision]['variant_one_wv'] + self.test_cases[self.precision]['variant_two_oqty'] * self.test_cases[self.precision]['variant_two_wv']) / 1000
        )  # Expected 4.578

       

       

        shipping_cost = Decimal(self.test_cases[self.precision]['custom_shipping_amount']['price'])

        expected_subtotal = Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty'] +
            self.test_cases[self.precision]['variant_two_price'] * self.test_cases[self.precision]['variant_two_oqty']
        )
        expected_total = expected_subtotal + shipping_cost 


        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(expected_subtotal, currency, locale='en_US')
        expected_shipping_cost_fr = build_currency_amount(shipping_cost, currency, locale='en_US')

        

        # Estimate Test
        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json')


        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_estimate_response.data['total'], expected_total_fr)
        self.assertEqual(order_estimate_response.data['shipping_fee'], expected_shipping_cost_fr)

        # Order Create Test
        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_response.data['total'], expected_total_fr)
        self.assertEqual(order_response.data['shipping_fee'], expected_shipping_cost_fr)





class OrderCreateShippingRateManualAsCustomer(BaseTestCase): # as customer, to test customer can't set some fields in payload like custom_shipping_amount
   
   
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.customerLogin()

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))


        self.test_cases = {
            '2': { # USD, EUR, BDT etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50.29,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.26,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount': {
                    'name': 'X-Example Shipping',
                    'price': 15, # $15 USD
                }
            },
            '3': { # KWD, OMR, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50.290,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.260,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount':  {
                    'name': 'X-Example Shipping',
                    'price': 300.000, # 300 KWD
                }
            },
            '0': { # JPY, KRW, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'variant_one_price': 50,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
                'custom_shipping_amount': {
                    'name': 'X-Example Shipping',
                    'price': 2000, # 1500 JPY
                }
            },
        }

       
    
       

        self.order_api_url = reverse('order_create')
        self.order_estimate_api_url = reverse('order_estimate')

    def test_order_shipping_rate_calculation(self):
        """
        Test case to ensure shipping rates are accurately calculated based on product weights and regions.
        """
        currency = settings.BASE_CURRENCY

        # Create product type and products
        product_type = ProductTypeFactory(
            name=f"{currency} Product Type physical",
            track_stock=False,
            taxable=True,
            physical_product=True,
        )

        # Create products and variants
        product_one = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant_one = ProductVariantFactory(
            product=product_one,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_one_price'], currency),
            cost_per_unit=50.00,
            weight_value= self.test_cases[self.precision]['variant_one_wv'],
        )
        
        product_two = ProductFactory(
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
        )
        variant_two = ProductVariantFactory(
            product=product_two,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_two_price'], currency),
            cost_per_unit=50.00,
            weight_value=self.test_cases[self.precision]['variant_two_wv'],  # 578 grams
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
            'custom_shipping_amount': self.test_cases[self.precision]['custom_shipping_amount'],
            "variants": [
                {
                    "alias": variant_one.alias,
                    "quantity": self.test_cases[self.precision]['variant_one_oqty'],
                },
                {
                    "alias": variant_two.alias,
                    "quantity": self.test_cases[self.precision]['variant_two_oqty'],
                }
            ]
        }

        # Expected values
        total_weight = Decimal(
            (self.test_cases[self.precision]['variant_one_oqty'] * self.test_cases[self.precision]['variant_one_wv'] + self.test_cases[self.precision]['variant_two_oqty'] * self.test_cases[self.precision]['variant_two_wv']) / 1000
        )  # Expected 4.578

       

       

        shipping_cost = Decimal(self.test_cases[self.precision]['custom_shipping_amount']['price'])

        expected_subtotal = Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty'] +
            self.test_cases[self.precision]['variant_two_price'] * self.test_cases[self.precision]['variant_two_oqty']
        )
        expected_total = expected_subtotal + shipping_cost 


        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(expected_subtotal, currency, locale='en_US')
        expected_shipping_cost_fr = build_currency_amount(shipping_cost, currency, locale='en_US')

        

        # Estimate Test
        order_estimate_response = self.auth_client.post(self.order_estimate_api_url, order_payload, format='json')

        self.permissionDenied(order_estimate_response)

       
        # Order Create Test
        order_response = self.auth_client.post(self.order_api_url, order_payload, format='json')
        self.permissionDenied(order_response)