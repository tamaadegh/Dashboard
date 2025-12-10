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
from nxtbn.shipping.models import ShippingRate
from nxtbn.shipping.tests import ShippingMethodFactory, ShippingRateFactory
from nxtbn.tax.tests import TaxClassFactory, TaxRateFactory
from babel.numbers import get_currency_precision, format_currency


from django.test.utils import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class OrderCreateShippingRateTaxRateTest(BaseTestCase): #single currency: to different single currency test, change settings.BASE_CURRENCY to 'USD' or 'EUR' or 'JPY' or 'KWD' or 'OMR' etc.    
   
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.login(email='test@example.com', password='testpass')

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))

        # Shipping method
        self.shipping_method = ShippingMethodFactory(name='DHL-DTH')

       

        self.test_cases = {
            '2': { # USD, EUR, BDT etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'input_rate': 15,  # 15 USD
                'input_tax_rate': 15,  # 15% VAT/GTST
                'input_incremental_rate': 3,  # 3 USD
                'variant_one_price': 50.29,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.26,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
            },
            '3': { # KWD, OMR, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'input_rate': 15.000,
                'input_tax_rate': 15.000, # 15% VAT/GTST
                'input_incremental_rate': 3.000,
                'variant_one_price': 50.290,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20.260,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
            },
            '0': { # JPY, KRW, etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'input_rate': 15,  # 15 USD
                'input_tax_rate': 15,  # 15% VAT/GTST
                'input_incremental_rate': 3,  # 3 USD
                'variant_one_price': 50,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
            },
        }

         # Tax class
        self.tax_class = TaxClassFactory()
        tax_rate = TaxRateFactory(
            tax_class=self.tax_class,
            is_active=True,
            rate=self.test_cases[self.precision]['input_tax_rate'],
            country=self.country,
            state=self.state,
        )

       
        ShippingRateFactory(
            shipping_method=self.shipping_method,
            country=self.country,
            region=self.state,
            rate=normalize_amount_currencywise(self.test_cases[self.precision]['input_rate'], settings.BASE_CURRENCY),
            weight_min=self.test_cases[self.precision]['input_weight_min'],
            weight_max=self.test_cases[self.precision]['input_weight_max'],  
            currency=settings.BASE_CURRENCY,
            incremental_rate=normalize_amount_currencywise(self.test_cases[self.precision]['input_incremental_rate'], settings.BASE_CURRENCY)
        )

       

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def test_order_shipping_rate_tax_rate_calculation(self):
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
        product_one = ProductFactory( # with tax class
            product_type=product_type,
            status=PublishableStatus.PUBLISHED,
            tax_class=self.tax_class,
        )
        variant_one = ProductVariantFactory(
            product=product_one,
            track_inventory=False,
            currency=currency,
            price=normalize_amount_currencywise(self.test_cases[self.precision]['variant_one_price'], currency),
            cost_per_unit=50.00,
            weight_value= self.test_cases[self.precision]['variant_one_wv'],
        )
        
        product_two = ProductFactory( # without tax class
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
            'shipping_method_id': self.shipping_method.id,
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

       

        address = {
            'country': self.country,
            'state': self.state,
        }
        shipping_rate_instance = get_shipping_rate_instance(
            self.shipping_method.id,
            address,
            total_weight,
        )

        if shipping_rate_instance:
            self.shipping_rate = shipping_rate_instance.rate
            self.test_cases[self.precision]['input_incremental_rate'] = shipping_rate_instance.incremental_rate
       

        shipping_cost = (
            self.shipping_rate
            if total_weight <= self.test_cases[self.precision]['input_weight_max']
            else self.shipping_rate + (total_weight - Decimal(5)) *  self.test_cases[self.precision]['input_incremental_rate']
        )

        tax_cost = Decimal(self.test_cases[self.precision]['input_tax_rate']) / 100 * Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty']
        )

        

        expected_subtotal = Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty'] +
            self.test_cases[self.precision]['variant_two_price'] * self.test_cases[self.precision]['variant_two_oqty']
        )
        expected_total = expected_subtotal + shipping_cost + tax_cost


        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(expected_subtotal, currency, locale='en_US')
        expected_shipping_cost_fr = build_currency_amount(shipping_cost, currency, locale='en_US')
        tax_cost_fr = build_currency_amount(tax_cost, currency, locale='en_US')

        

        # Estimate Test
        order_estimate_response = self.client.post(self.order_estimate_api_url, order_payload, format='json')

        self.assertEqual(order_estimate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_estimate_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_estimate_response.data['total'], expected_total_fr)
        self.assertEqual(order_estimate_response.data['shipping_fee'], expected_shipping_cost_fr)
        self.assertEqual(order_estimate_response.data['estimated_tax'], tax_cost_fr)

        # Order Create Test
        order_response = self.client.post(self.order_api_url, order_payload, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_response.data['total'], expected_total_fr)
        self.assertEqual(order_response.data['shipping_fee'], expected_shipping_cost_fr)
        self.assertEqual(order_response.data['estimated_tax'], tax_cost_fr)
