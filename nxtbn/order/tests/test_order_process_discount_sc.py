import random
from decimal import Decimal
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.core.utils import build_currency_amount, normalize_amount_currencywise
from nxtbn.discount import PromoCodeType
from nxtbn.discount.tests import PromoCodeFactory
from nxtbn.home.base_tests import BaseGraphQLTestCase, BaseTestCase
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
from unittest.mock import MagicMock


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestOrderProcessWithDiscount(BaseGraphQLTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.login(email='test@example.com', password='testpass')

        self.country = 'US'
        self.state = 'NY'
        self.precision = str(get_currency_precision(settings.BASE_CURRENCY))
        
        # Configurable test cases for different currency precisions
        self.test_cases = {
            '2': { # USD, EUR, BDT etc.
                'input_weight_min': 0,
                'input_weight_max': 5,  # 5kg
                'order_discount_code_percentage': 'DISCOUNT10P',
                'order_discount_code_fixed': 'DISCOUNT100FIXED',
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
                'order_discount_code_percentage': 'DISCOUNT10P',
                'order_discount_code_fixed': 'DISCOUNT100FIXED',
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
                'order_discount_code_percentage': 'DISCOUNT10P',
                'order_discount_code_fixed': 'DISCOUNT100FIXED',
                'variant_one_price': 50,
                'variant_one_wv': 100,  # 100 grams
                'variant_one_oqty': 40,
                'variant_two_price': 20,
                'variant_two_wv': 578,
                'variant_two_oqty': 1,
            },
        }

        self.order_api_url = reverse('admin_order_create')
        self.order_estimate_api_url = reverse('admin_order_estimate')

    def _run_discount_test(self, discount_type):
        """
        Run discount calculation test for a given discount type
        
        :param discount_type: Either 'percentage' or 'fixed'
        """
        # Determine the test case and create appropriate discount
        if discount_type == PromoCodeType.PERCENTAGE:  # percentage
            discount_code = self.test_cases[self.precision]['order_discount_code_percentage']
            discount = PromoCodeFactory(
                code=discount_code,
                code_type=PromoCodeType.PERCENTAGE,
                value=10,
                is_active=True,
                min_purchase_amount=0,
                min_purchase_period=None,
                redemption_limit=None,
                new_customers_only=False,
            )
        else:  # fixed
            discount_code = self.test_cases[self.precision]['order_discount_code_fixed']
            discount = PromoCodeFactory(
                code=discount_code,
                code_type=PromoCodeType.FIXED_AMOUNT,
                value=100,
                is_active=True,
                min_purchase_amount=0,
                min_purchase_period=None,
                redemption_limit=None,
                new_customers_only=False,
            )

        currency = settings.BASE_CURRENCY

        # Create product type and products
        product_type = ProductTypeFactory(
            name=f"{currency} Product Type physical",
            track_stock=False,
            taxable=False,
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
            weight_value=self.test_cases[self.precision]['variant_one_wv'],
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
            weight_value=self.test_cases[self.precision]['variant_two_wv'],
        )

        # Payload for order
        order_mutation = """
            mutation MyMutation {
            orderProcess(
                input: {
                variants: [
                    {alias: "%s", quantity: %d},
                    {alias: "%s", quantity: %d}
                ],
                createOrder: false,
                note: "",
                promocode: "%s",
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
                variant_one.alias,
                self.test_cases[self.precision]['variant_one_oqty'],
                variant_two.alias,
                self.test_cases[self.precision]['variant_two_oqty'],
                discount_code,
                self.country,
                self.state
            )

        # Calculate subtotal
        subtotal = Decimal(
            self.test_cases[self.precision]['variant_one_price'] * self.test_cases[self.precision]['variant_one_oqty'] +
            self.test_cases[self.precision]['variant_two_price'] * self.test_cases[self.precision]['variant_two_oqty']
        )

        # Calculate discount based on type
        if discount_type == PromoCodeType.PERCENTAGE:
            total_discount = subtotal * Decimal(discount.value) / 100
        else:  # fixed
            total_discount = Decimal(discount.value)

        # Ensure discount doesn't exceed subtotal
        total_discount = min(total_discount, subtotal)
        
        # Calculate expected total
        expected_total = subtotal - total_discount

        # Format amounts
        expected_total_fr = build_currency_amount(expected_total, currency, locale='en_US')
        expected_subtotal_fr = build_currency_amount(subtotal, currency, locale='en_US')
        expected_total_discount_fr = build_currency_amount(total_discount, currency, locale='en_US')

        mock_user = MagicMock()
        mock_user.id = self.user.id
        mock_user.email = self.user.email
        mock_user.exchange_rate = 1.0
        mock_user.user = self.user
        mock_user.currency = 'USD'

        # Estimate Test
        order_estimate_response =  self.graphql_customer_client.execute(order_mutation, context_value=mock_user)


        order_estimate_response = order_estimate_response['data']['orderProcess']['response']

        self.assertEqual(order_estimate_response['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_estimate_response['total'], expected_total_fr)
        self.assertEqual(order_estimate_response['discount'], expected_total_discount_fr)


        # Payload for order
        order_mutation_create = """
            mutation MyMutation {
            orderProcess(
                input: {
                variants: [
                    {alias: "%s", quantity: %d},
                    {alias: "%s", quantity: %d}
                ],
                createOrder: true,
                note: "",
                promocode: "%s",
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
                variant_one.alias,
                self.test_cases[self.precision]['variant_one_oqty'],
                variant_two.alias,
                self.test_cases[self.precision]['variant_two_oqty'],
                discount_code,
                self.country,
                self.state
            )

        # # Order Create Test
  
        order_response =  self.graphql_customer_client.execute(order_mutation_create, context_value=mock_user)

        order_response = order_response['data']['orderProcess']['response']


        # self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response['subtotal'], expected_subtotal_fr)
        self.assertEqual(order_response['total'], expected_total_fr)
        self.assertEqual(order_response['discount'], expected_total_discount_fr)

    def test_order_discount_calculation_percentage(self):
        """
        Test order discount calculation for percentage-based discount
        """
        self._run_discount_test(PromoCodeType.PERCENTAGE)

    def test_order_discount_calculation_fixed(self):
        """
        Test order discount calculation for fixed amount discount
        """
        self._run_discount_test(PromoCodeType.FIXED_AMOUNT)