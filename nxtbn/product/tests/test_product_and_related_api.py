import random
import sys
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from nxtbn.core import PublishableStatus
from nxtbn.home.base_tests import BaseTestCase
from django.utils import timezone
from nxtbn.product.models import Product, ProductType
from rest_framework.test import APIClient


class ProductAndRelatedCreateAPITest(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        
        self.adminLogin()
        
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
            "name": "Test Category",
            "parent": None
        }
        self.category_url = reverse('category-list')
        category_response = self.auth_client.post(self.category_url, self.category_data, format='json')
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        self.category_id = category_response.data['id']
        

        if settings.BASE_CURRENCY == 'USD':
            price = '20.25'
        
        if settings.BASE_CURRENCY == 'KWD':
            price = '30.258'

        if settings.BASE_CURRENCY == 'JPY':
            price = '2025'

        # Create Product
        self.product_data = {
            "variants_payload": [
                {
                    "is_default_variant": True,
                    "currency": settings.BASE_CURRENCY,
                    "price": price,
                    "cost_per_unit": "44",
                    "sku": "BBC-3",
                    # "color_code": "#FFFFFF",
                    "track_inventory": False,
                }
            ],
            "product_type": self.product_type_id,
            "description": "[{\"type\":\"paragraph\",\"children\":[{\"text\":\"Lorem Ipsum\"}]}]",
            # "tax_class": 1,
            "name": "Titanic",
            "summary": "A ship that sank",
            "images": [],
            "meta_title": "Titanic",
            "meta_description": "A ship sank to the bottom of the ocean",
            "slug": "titanic",
            "status": PublishableStatus.PUBLISHED,
            "category": self.category_id,
            "tags_payload": [
                "Southampton",
                "New York"
            ]
        }

        self.product_url = reverse('product-list')
        response = self.auth_client.post(self.product_url, self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(str(response.data['variants'][0]['price']), price)
        
        self.product_id = response.data['id']

    def test_product_creation(self):
        """Test product creation process."""
        # Ensure the product type, category, and product were created
        self.assertIsNotNone(self.product_type_id)
        self.assertIsNotNone(self.category_id)
        self.assertIsNotNone(self.product_id)