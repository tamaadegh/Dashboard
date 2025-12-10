from django.test import TestCase
from nxtbn.core import PublishableStatus
from nxtbn.home.base_tests import BaseGraphQLTestCase
from nxtbn.product.models import Product, Category, Collection, ProductTag
from nxtbn.product.tests import (
    ProductFactory,
    CategoryFactory,
    CollectionFactory,
    ProductTagFactory,
    ProductVariantFactory,
)
from nxtbn.admin_schema import admin_schema
from graphene.test import Client as GRAPHClient
from unittest.mock import Mock


class ProductQueryTestCase(BaseGraphQLTestCase):
    def setUp(self):
        super().setUp()

        # Create sample data for testing
        self.category = CategoryFactory(name="Test Category")
        self.collection = CollectionFactory(name="Test Collection")
        self.tag = ProductTagFactory(name="Test Tag")
        self.product = ProductFactory(
            name="Test Product",
            category=self.category,
            # collections=[self.collection],
            # tags=[self.tag],
            status=PublishableStatus.PUBLISHED,
        )

        self.variant = ProductVariantFactory(product=self.product, price=10.0)
        self.product.default_variant = self.variant
        self.product.save()

    def test_resolve_product_valid_id(self):
        query = """
        query getProduct($slug: String!) {
            product(slug: $slug) {
                id
                slug
                name
                category {
                    name
                }
            }
        }
        """

        mocked_context = Mock()
        mocked_context.exchange_rate = None

        variables = {"slug": self.product.slug}
        response = self.graphql_customer_client.execute(query, variables=variables, context_value=mocked_context)


        self.assertGraphQLSuccess(response)
        data = response["data"]["product"]

        self.assertEqual(data["name"], "Test Product")
        self.assertEqual(data["category"]["name"], "Test Category")

    def test_resolve_product_invalid_id(self):
        query = """
        query getProduct($id: ID!) {
            product(id: $id) {
                id
            }
        }
        """

        variables = {"id": "invalid-id"}
        response = self.graphql_customer_client.execute(query, variables=variables)

        self.assertGraphQLFailure(response)
        self.assertIsNone(response["data"])  # Product should be None

    def test_resolve_all_products(self):
        query = """
        query getAllProducts {
            products(first: 50) {
            edges {
                node {
                id
                name
                category {
                    name
                }
                }
            }
            }
        }
        """
        mocked_context = Mock()
        mocked_context.exchange_rate = None

        response = self.graphql_customer_client.execute(query, context_value=mocked_context)

        self.assertGraphQLSuccess(response)
        products = response["data"]["products"]["edges"]

        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["node"]["name"], "Test Product")
        self.assertEqual(products[0]["node"]["category"]["name"], "Test Category")

    def test_resolve_all_categories(self):
        query = """
        query getAllCategories {
            categories(first: 50) {
            edges {
                node {
                id
                name
                }
            }
            }
        }
        """


        response = self.graphql_customer_client.execute(query)

        self.assertGraphQLSuccess(response, expected_status=200)
        categories = response["data"]["categories"]["edges"]

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]["node"]["name"], "Test Category")

    def test_resolve_all_collections(self):
        query = """
        query getAllCollections {
            collections(first: 50) {
            edges {
                node {
                id
                name
                }
            }
            }
        }
        """

        response = self.graphql_customer_client.execute(query)

        self.assertGraphQLSuccess(response, expected_status=200)
        collections = response["data"]["collections"]["edges"]

        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0]["node"]["name"], "Test Collection")

    def test_resolve_all_tags(self):
        query = """
        query getAllTags {
            tags(first: 50) {
            edges {
                node {
                id
                name
                }
            }
            }
        }
        """

        response = self.graphql_customer_client.execute(query)

        self.assertGraphQLSuccess(response, expected_status=200)
        tags = response["data"]["tags"]["edges"]

        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]["node"]["name"], "Test Tag")
