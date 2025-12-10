
from django.test import  TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from nxtbn.admin_schema import admin_schema
from nxtbn.users import UserRole
from nxtbn.users.tests import UserFactory
from django.test import TestCase
from graphene.test import Client as GRAPHClient
from django.contrib.auth.hashers import make_password
from nxtbn.storefront_schema import storefront_schema
from nxtbn.users import UserRole
from nxtbn.users.tests import UserFactory

from django.contrib.auth.hashers import make_password




class BaseGraphQLTestCase(TestCase):
    graphql_admin_client = GRAPHClient(admin_schema)
    graphql_customer_client = GRAPHClient(storefront_schema)

    def setUp(self):
        self.user = UserFactory(
            email="test@example.com",
            password=make_password('testpass')
        )

    def execute_admin_graphql(self, mutation, variables=None):
        """Helper function to execute a GraphQL mutation with variables."""
        response = self.graphql_admin_client.execute(mutation, variable_values=variables)
        return response


    def assertGraphQLSuccess(self, response, *args, **kwargs):
        """Check if the GraphQL response contains no errors and has data."""
        self.assertNotIn('errors', response)  # Make sure no errors are present
        self.assertIn('data', response)  # Ensure data exists in the response
        # Optionally, you can assert specific data is present
        self.assertIsInstance(response['data'], dict)

    def assertGraphQLFailure(self, response, *args, **kwargs):
        """Check if the GraphQL response contains errors."""
        self.assertIn('errors', response)
        

    def superAdminLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            is_staff=True,
            is_superuser=True,
            role=UserRole.ADMIN
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        response = self.execute_admin_graphql(mutation)
        self.assertGraphQLSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']
        

    def adminLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            is_staff=True,
            role=UserRole.ADMIN
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        response = self.execute_admin_graphql(mutation)
        self.assertGraphQLSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']

    def customerLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.CUSTOMER,
            is_staff=False,
            is_superuser=False
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        # response = self.execute_admin_graphql(mutation)
        # self.assertGraphQLSuccess(response)

        # # Extract access token
        # access_token = response['data']['login']['login']['token']['access']

    def storeManagerLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.STORE_MANAGER,
            is_staff=False
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        response = self.execute_admin_graphql(mutation)
        self.assertGraphQLSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']

    def marketingManagerLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.STORE_MANAGER,
            is_staff=False
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        response = self.execute_admin_graphql(mutation)
        self.assertGraphQLSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']


class BaseTestCase(TestCase): # We have to remove this as we are now transforming rest to graphql
    client = APIClient()
    auth_client = APIClient()
    graphql_admin_client = GRAPHClient(admin_schema)
    graphql_customer_client = GRAPHClient(storefront_schema)
    
    def setUp(self):
        self.user = UserFactory(
            email="test@example.com",
            password=make_password('testpass')
        )       
        
    def badRequest(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 400, *args, **kwargs)

    def permissionDenied(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 403, *args, **kwargs)

    def requestUnauthorized(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 401, *args, **kwargs)
        
    def assertSuccess(self, request, *args, **kwargs):
        self.assertEqual(request.status_code, 200, *args, **kwargs)
        
    def loginSeccess(self, login):
        self.assertTrue(login)

    def assertGraphSuccess(self, response, *args, **kwargs):
        """Check if the GraphQL response contains no errors and has data."""
        self.assertNotIn('errors', response)  # Make sure no errors are present
        self.assertIn('data', response)  # Ensure data exists in the response
        # Optionally, you can assert specific data is present
        self.assertIsInstance(response['data'], dict)

    def execute_graphql(self, mutation, variables=None):
        """Helper function to execute a GraphQL mutation with variables."""
        response = self.graphql_admin_client.execute(mutation, variable_values=variables)
        return response

    def superAdminLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            is_staff=True,
            is_superuser=True,
            role=UserRole.ADMIN
        )
        
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """
        
        response = self.execute_graphql(mutation)
        self.assertGraphSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def adminLogin(self):
       
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            is_staff=True,
            role=UserRole.ADMIN
        )

        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """

        response = self.execute_graphql(mutation)
        self.assertGraphSuccess(response)

       
        # Extract access token
        access_token = response['data']['login']['login']['token']['access']
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


        
        
    
    def customerLogin(self):
      
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.CUSTOMER,
            is_staff=False,
            is_superuser=False
        )
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """

        # response = self.execute_graphql(mutation)
        # self.assertGraphSuccess(response)


        # # Extract access token
        # access_token = response['data']['login']['token']['access']
        # self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def storeManagerLogin(self):
       
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.STORE_MANAGER,
            is_staff=False
        )
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """

        response = self.execute_graphql(mutation)
        self.assertGraphSuccess(response)


        # Extract access token
        access_token = response['data']['login']['login']['token']['access']
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    
    def marketingManagerLogin(self):
        self.user = UserFactory(
            email="cc@example.com",
            password=make_password('testpass'),
            role=UserRole.STORE_MANAGER,
            is_staff=False
        )
        mutation = """
            mutation MyMutation {
                login(email: "cc@example.com", password: "testpass") {
                    login {
                        storeUrl
                        token {
                            access
                            expiresIn
                            refresh
                            refreshExpiresIn
                        }
                        version
                        user {
                            email
                            firstName
                            fullName
                            id
                            lastName
                            role
                            username
                        }
                    }
                }
            }
        """

        response = self.execute_graphql(mutation)
        self.assertGraphSuccess(response)

        # Extract access token
        access_token = response['data']['login']['login']['token']['access']
        self.auth_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')


