from nxtbn.home.base_tests import BaseTestCase
from rest_framework.reverse import reverse
from rest_framework import status
from nxtbn.product.models import Product, ProductVariant
from nxtbn.core import PublishableStatus
from django.conf import settings
from decimal import Decimal


class TestProductCreateAPITest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.adminLogin()

        self.product_create_url = reverse('product-list')

        # Create ProductType
        self.product_type_data = {
            'name': 'Non-Tracking Product',
            'taxable': True,
            'track_stock': False
        }
        # Create the product type via the API
        self.product_type_url = reverse('producttype-list') 
        response = self.auth_client.post(self.product_type_url, self.product_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product_type_id = response.data['id']

        self.category_data = {
            'name': 'Fasion',
            'parent': None
        }
        self.category_url = reverse('category-list')
        category_response = self.auth_client.post(self.category_url, self.category_data, format='json')
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        self.category_id = category_response.data['id']
        
        if settings.BASE_CURRENCY == 'USD':
            self.variant_1_price =  '20.22'
            self.variant_2_price =  '25.34'
            self.variant_3_price =  '46.21'
        
        if settings.BASE_CURRENCY == 'KWD':
            self.variant_1_price = '6.24'
            self.variant_2_price = '7.81'
            self.variant_3_price = '14.24'

        if settings.BASE_CURRENCY == 'JPY':
            self.variant_1_price = '3182'
            self.variant_2_price = '3982'
            self.variant_3_price = '7263'

    def test_create_product_with_variants(self):
        """Define payload to create a product with 3 variants"""
        payload = {
            "name": "Test Product",
            "description": "A test product for API testing",
            "summary": "A ship for api testing",
            "variants_payload": [
                {
                    "is_default_variant": True,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_1_price,
                    "cost_per_unit": "44",
                    "sku": "USD-3",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_2_price,
                    "cost_per_unit": "23",
                    "sku": "KWD-7",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_3_price,
                    "cost_per_unit": "46",
                    "sku": "JPY-45",
                    "track_inventory": False,
                }
            ],
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "product_type": self.product_type_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
            
        }

        response = self.auth_client.post(self.product_create_url, payload, format='json')
        id = response.json()['id']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product_detail_url = reverse('product-detail', kwargs={'id': id})
        product_detail_response = self.auth_client.get(product_detail_url, format='json')

        self.assertEqual(product_detail_response.json()['name'], payload['name']) # compare product name
        self.assertEqual(product_detail_response.json()['summary'], payload['summary']) # compare product summary
        
        variants = product_detail_response.json()['variants']
        for response_variant, payload_variant in zip(variants, payload["variants_payload"]):
            self.assertEqual(response_variant['is_default_variant'], payload_variant['is_default_variant']) # compare product variant is default or not
            self.assertEqual(float(response_variant['price']), float(payload_variant['price'])) # compare product variant price
            self.assertEqual(Decimal(response_variant['cost_per_unit']), Decimal(payload_variant['cost_per_unit'])) # compare product variant cost_per_unit
            self.assertEqual(response_variant['sku'], payload_variant['sku'])  # compare product variant sku
            self.assertEqual(response_variant['track_inventory'], payload_variant['track_inventory']) # compare product variant track_inventory
        
        self.assertEqual(product_detail_response.json()['category'], self.category_id) # compare product category
        self.assertEqual(product_detail_response.json()['product_type'], self.product_type_id) # compare product product type

        tags = product_detail_response.json()['tags']
        for response_tag, payload_tag in zip(tags, payload['tags_payload']):
            self.assertEqual(response_tag['name'], payload_tag) # compare product tags

    def test_create_product_missing_info(self):
        """ Define payload with missing product name """
        payload = {
            "description": "Product without a name",
            "price": 29.99,
            "variants_payload": [
                {
                    "is_default_variant": True,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_1_price,
                    "cost_per_unit": "44",
                    "sku": "USD-3",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_3_price,
                    "cost_per_unit": "46",
                    "sku": "JPY-45",
                    "track_inventory": False,
                }
            ],
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "product_type": self.product_type_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
        }

        response = self.auth_client.post(self.product_create_url, payload, format='json')

        # Check if the response status is 400 Bad Request (name, summary is missing)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_invalid_price(self):
        """ Define payload with invalid price (negative value) """
        payload = {
            "name": "Test Product",
            "description": "A test product for API testing",
            "summary": "A ship for api testing",
            "variants_payload": [
                {
                    "is_default_variant": True,
                    "currency": settings.BASE_CURRENCY,
                    "price": -334.32, # invalid price
                    "cost_per_unit": "44",
                    "sku": "USD-3",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": -453, # invalid price
                    "cost_per_unit": "23",
                    "sku": "KWD-7",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": -143, # invalid price
                    "cost_per_unit": "46",
                    "sku": "JPY-45",
                    "track_inventory": False,
                }
            ],
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "product_type": self.product_type_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
            
        }


        response = self.auth_client.post(self.product_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_empty_variant(self):
        """ Define payload with empty variant """
        payload = {
            "name": "Test Product",
            "description": "A test product for API testing",
            "summary": "A ship for api testing",
            "variants_payload": [],
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "product_type": self.product_type_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
            
        }

        response = self.auth_client.post(self.product_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_with_duplicate_variant(self):
        """ Define payload with duplicate variants """
        payload = {
            "name": "Product with Duplicate Variant",
            "description": "Product with duplicate variant data",
            "summary": "A ship for api testing",
            "variants_payload": [
                {
                    "is_default_variant": True,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_1_price,
                    "cost_per_unit": "44",
                    "sku": "USD-3",
                    "track_inventory": False,
                },
                {
                    "is_default_variant": False,
                    "currency": settings.BASE_CURRENCY,
                    "price": self.variant_1_price,
                    "cost_per_unit": "44",
                    "sku": "USD-3",
                    "track_inventory": False,
                },
            ],
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "product_type": self.product_type_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
        }

        response = self.auth_client.post(self.product_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)