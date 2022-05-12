from barters_app import views
from barters_app.models import (MaterialBarter, PlantBarter, ProduceBarter,
                                SeedBarter, ToolBarter)
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from django.test import TestCase
from django.urls import reverse
from garden_barter_proj import settings
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from users_app.utils import Token, generate_test_user


class TestCreateBarter(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.user, self.valid_refresh_token = generate_test_user(
            UserModel=get_user_model(),
            email='test_user_1@gardenbarter.com',
            password='pass3412'
        )
    
        self.barter_data = {
            'title': 'test barter title',
            'description': 'test barter description',
            'will_trade_for': 'item that will be traded',
            'is_free': False,
            'cross_street_1': '123 Faux St.',
            'cross_street_2': '789 Impostor Rd',
            'postal_code': '99999',
            'latitude': '',
            'longitude': ''
        }

        self.seed_barder_data = self.barter_data.update({
            'genus': 'leonarus',
            'species': 'cardiaca',
            'common_name': 'motherwort',
        })

    def test_create_seed_barter_success(self):
        request = self.factory.post(
            reverse('barters_app:create'),
            ,
            format='json'
        )

        access_token = Token(self.user, 'access')

        csrf_token = generate_csrf_token(request)

        request.COOKIES.update({
            'refreshtoken': self.valid_refresh_token.token,
            'csrftoken': csrf_token
        })

        request.META.update({
            'X-CSRFToken': csrf_token
        })

        headers = {
            'Authorization': f'Token {access_token.token}',
        }

        request.headers = headers

        response = views.create(request)
        print(request.COOKIES, response.data)
