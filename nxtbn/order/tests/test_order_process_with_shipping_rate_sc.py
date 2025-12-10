
import random
from decimal import Decimal
from unittest.mock import MagicMock
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import build_currency_amount, normalize_amount_currencywise
from nxtbn.home.base_tests import BaseGraphQLTestCase, BaseTestCase
from nxtbn.order.proccesor.views import get_shipping_rate_instance
from nxtbn.product import WeightUnits
from nxtbn.product.models import Product
from rest_framework.test import APIClient
from nxtbn.product.tests import ProductFactory, ProductTypeFactory, ProductVariantFactory
from nxtbn.shipping.models import ShippingRate
from nxtbn.shipping.tests import ShippingMethodFactory, ShippingRateFactory
from nxtbn.tax.tests import TaxClassFactory
from babel.numbers import get_currency_precision, format_currency


from django.test.utils import override_settings

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class OrderCreateShippingRateTaxableGraphQL(BaseGraphQLTestCase): #single currency: to different single currency test, change settings.BASE_CURRENCY to 'USD' or 'EUR' or 'JPY' or 'KWD' or 'OMR' etc.
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
        self.adminLogin()

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
                'input_incremental_rate': 3,  # 3 USD
                'variant_one_price': 50,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
            },
        }

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

        order_mutation = """
            mutation MyMutation {
                orderProcess(
                    input: {
                    variants: [
                        { alias: "%s", quantity: %d },
                        { alias: "%s", quantity: %d }
                    ],
                    note: "",
                    promocode: "",
                    shippingAddress: {
                        country: "%s",
                        email: "test@example.com",
                        firstName: "John",
                        phoneNumber: "1234567890",
                        lastName: "Doe",
                        postalCode: "10001",
                        state: "%s",
                        streetAddress: "123 Main St",
                        city: "New York"
                    },
                    shippingMethodId: %d,
                    createOrder: false
                    }
                ) {
                    message
                    orderAlias
                    orderId
                    response
                    success
                }
            }
        """ % (
            variant_one.alias, self.test_cases[self.precision]['variant_one_oqty'],
            variant_two.alias, self.test_cases[self.precision]['variant_two_oqty'],
            self.country,
            self.state,
            self.shipping_method.id
        )

        mock_user = MagicMock()
        mock_user.id = self.user.id
        mock_user.email = self.user.email
        mock_user.exchange_rate = 1.0
        mock_user.user = self.user
        mock_user.currency = 'USD'

        order_estimate_response = self.graphql_customer_client.execute(order_mutation, context_value=mock_user)
        order_estimate_response = order_estimate_response['data']['orderProcess']['response']

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
        expected_subtotal = Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty'] +
            self.test_cases[self.precision]['variant_two_price'] * self.test_cases[self.precision]['variant_two_oqty']
        )
        expected_total = expected_subtotal + shipping_cost 

        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(expected_subtotal, currency, locale='en_US')
        expected_shipping_cost_fr = build_currency_amount(shipping_cost, currency, locale='en_US')

        self.assertEqual(order_estimate_response['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_estimate_response['total'], expected_total_fr)
        self.assertEqual(order_estimate_response['shipping_fee'], expected_shipping_cost_fr)

        # Order Create Test
        order_mutation_create = """
            mutation MyMutation {
                orderProcess(
                    input: {
                    variants: [
                        { alias: "%s", quantity: %d },
                        { alias: "%s", quantity: %d }
                    ],
                    note: "",
                    promocode: "",
                    shippingAddress: {
                        country: "%s",
                        email: "test@example.com",
                        firstName: "John",
                        phoneNumber: "1234567890",
                        lastName: "Doe",
                        postalCode: "10001",
                        state: "%s",
                        streetAddress: "123 Main St",
                        city: "New York"
                    },
                    shippingMethodId: %d,
                    createOrder: true
                    }
                ) {
                    message
                    orderAlias
                    orderId
                    response
                    success
                }
            }
        """ % (
            variant_one.alias, self.test_cases[self.precision]['variant_one_oqty'],
            variant_two.alias, self.test_cases[self.precision]['variant_two_oqty'],
            self.country,
            self.state,
            self.shipping_method.id
        )

        order_create_response = self.graphql_customer_client.execute(order_mutation_create, context_value=mock_user)
        order_create_response = order_create_response['data']['orderProcess']['response']

        self.assertEqual(order_create_response['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_create_response['total'], expected_total_fr)
        self.assertEqual(order_create_response['shipping_fee'], expected_shipping_cost_fr)
