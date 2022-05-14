from barters_app import views
from barters_app.models import (Barter, MaterialBarter, PlantBarter, ProduceBarter,
                                SeedBarter, ToolBarter)
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from django.test import TestCase
from django.urls import reverse
from barters_app.serializers import SeedBarterSerializer
from barters_app.serializers import BarterSerializer
from garden_barter_proj import settings
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from users_app.serializers import UserDetailSerializer
from users_app.utils import Token, generate_test_user
from jwt.exceptions import DecodeError
from barters_app.tests.utils import enrich_request

class TestBarterRetrieve(TestCase):
    fixtures=['fixtures/barters.json', 'fixtures/users.json']

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        # User 1
        self.user_1, self.valid_refresh_token_1 = generate_test_user(
            UserModel=get_user_model(),
            email='test_user_1@gardenbarter.com',
            password='pass3412'
        )

        self.valid_access_token_1 = Token(self.user_1, 'access')
        self.invalid_access_token_1 = Token(self.user_1, 'access', expiry={'days':-1})

        # User 2
        self.user_2, self.valid_refresh_token_2 = generate_test_user(
            UserModel=get_user_model(),
            email='test_user_2@gardenbarter.com',
            password='pass3412'
        )

        self.valid_access_token_2 = Token(self.user_2, 'access')
        self.invalid_access_token_2 = Token(self.user_2, 'access', expiry={'days':-1})

        

    def generate_request(self, barter_type=None, barter_id=None):
        '''return a Factory.get() request with the provided data'''

        kwargs = {}
        if barter_type:
            kwargs['barter_type'] = barter_type
        if barter_id:
            kwargs['barter_id'] = barter_id


        return self.factory.get(
            reverse('barters_app:retrieve', kwargs=kwargs),
            format='json'
        )

    def test_retrieve_list_success(self):
        request = self.generate_request()

        csrf_token = generate_csrf_token(request)
        request = enrich_request(
            request,
            self.valid_refresh_token_1,
            self.valid_access_token_1,
            csrf_token
        )

        response = views.retrieve(request)

        # there are 45 barters in the test db
        self.assertEqual(len(response.data['barters']), 45)
        self.assertEqual(response.status_code, status.HTTP_200_OK)