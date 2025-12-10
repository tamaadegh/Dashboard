# test case for single currency mode
from decimal import Decimal
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


from django.test.utils import override_settings


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ProductListAPITest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.adminLogin()

        self.products = []
        for _ in range(20):
            product_type = ProductTypeFactory()
            product = ProductFactory(product_type=product_type)
            default_variant = ProductVariantFactory(product=product, price=Decimal('157.69'))
            product.default_variant = default_variant
            product.save()
            self.products.append(product)

        
    def test_product_list_with_default_variant_only(self):
        url = reverse('product-list')
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)
        
        for product in response.data['results']:
            self.assertNotIn('variants', product) # only default variant should be present, not all variants


    def get_product_list_api_with_variant_only(self):
        url = reverse('product-withvariant')
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for product in response.data:
            self.assertIn('variants', product)
            self.assertNotIn('default_variant', product) # only variants should be present, not default variant


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ProductDetailAPITest(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.adminLogin()
        self.product = ProductFactory()
        self.product_type = ProductTypeFactory()
        self.product.product_type = self.product_type
        self.product.save()

    def test_product_detail(self):
        url = reverse('product-detail', args=[self.product.slug])
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.product.id)
        self.assertEqual(response.data['texts']['name'], self.product.name)
        self.assertEqual(response.data['texts']['summary'], self.product.summary)
        self.assertEqual(response.data['category'], self.product.category.id)
        self.assertIn('variants', response.data)


    def test_product_detail_with_related(self):
        black_shirt = ProductFactory(
            name='black t-shirt',
            name_when_in_relation='black'
        )
        
        ProductVariantFactory(product=black_shirt, name='black t-shirt - small',)
        ProductVariantFactory(product=black_shirt, name='black t-shirt - medium',)
        ProductVariantFactory(product=black_shirt, name='black t-shirt - large',)
        black_shirt.default_variant = ProductVariantFactory(product=black_shirt, name='black t-shirt - x-large',)

        white_shirt = ProductFactory(
            name='white t-shirt',
        )

        ProductVariantFactory(product=white_shirt, name='white t-shirt - small',)
        ProductVariantFactory(product=white_shirt, name='white t-shirt - medium',)
        ProductVariantFactory(product=white_shirt, name='white t-shirt - large',)
        white_shirt.default_variant = ProductVariantFactory(product=white_shirt, name='white t-shirt - x-large',)

        white_shirt.related_to.add(black_shirt)
        black_shirt.related_to.add(white_shirt)


        url = reverse('product-with-related', args=[black_shirt.slug])
        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        self.assertEqual(response.data['id'], black_shirt.id)
        self.assertEqual(response.data['texts']['name'], black_shirt.name)
        self.assertEqual(response.data['texts']['summary'], black_shirt.summary)
        self.assertIn('variants', response.data)
        self.assertIn('related_links', response.data)
        self.assertEqual(len(response.data['related_links']), 1)
        
        self.assertEqual(response.data['related_links'][0]['id'], white_shirt.id)
        self.assertEqual(response.data['related_links'][0]['slug'], white_shirt.slug)
        self.assertEqual(response.data['related_links'][0]['name_when_in_relation'], white_shirt.name_when_in_relation)