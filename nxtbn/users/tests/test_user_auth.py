import random

from rest_framework.reverse import reverse

from nxtbn.home.base_tests import BaseTestCase

from django.utils import timezone
from django.contrib.auth.hashers import make_password

from nxtbn.users.tests import UserFactory

class AuthUserLoginAPITest(BaseTestCase):
    
    def setUp(self):
        self.user = UserFactory(
            email="test@example.com",
            password=make_password('testpass')
        )   
        
    def test_authentication(self):
             
        # =================================
        # Test login
        # =================================
        
        # login
        login = self.client.login(email='test@example.com', password='testpass')
        self.loginSeccess(login)
        
        # logout        
        self.client.logout()