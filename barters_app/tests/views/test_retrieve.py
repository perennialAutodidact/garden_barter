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
from users_app.models import RefreshToken

BARTER_TYPES = [ 
    'seed_barter',
    'plant_barter',
    'produce_barter',
    'material_barter',
    'tool_barter'
]


class TestBarterRetrieve(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = []
        # Every test needs access to the request factory.
        cls.factory = APIRequestFactory(enforce_csrf_checks=True)
        models = {
            'plant': PlantBarter,
            'produce': ProduceBarter,
            'material': MaterialBarter,
            'tool':ToolBarter
        }

        for i in range(3):
            user = get_user_model().objects.create_user(
                email=f"user_{i}@gardenbarter.com",
                password='pass3412'
            )

            users.append(user)


            for barter_type in models:
                Model=models[barter_type]
                for i in range(3):
                    Model.objects.create(
                        creator=user,
                        title=f'{barter_type} barter title {i}',
                        description= f'{barter_type} barter description {i}',
                        will_trade_for= f'item that will be traded {i}',
                        is_free= False,
                        cross_street_1= '456 Fake St.',
                        cross_street_2= '876 Synthetic Ave',
                        postal_code= '77777',
                        barter_type=barter_type
                    )

        cls.user_1, cls.user_2, cls.user_3 = users

        cls.valid_refresh_token = RefreshToken.objects.create(
            user=cls.user_1,
            token=Token(user, 'refresh').token
        )
        cls.valid_access_token = Token(cls.user_1, 'access')


        cls.invalid_refresh_token = RefreshToken.objects.create(
            user=cls.user_2,
            token=Token(
                user,
                'refresh',
                expiry={'days': -1}
            ).token,
        )
        cls.invalid_access_token = Token(
            cls.user_2,
            'access',
            expiry={'days': -1}
        ).token

        
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
            self.valid_refresh_token,
            self.valid_access_token,
            csrf_token
        )

        response = views.retrieve(request)

        # there are 45 barters in the test db
        self.assertEqual(len(response.data['barters']), 45)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = views.retrieve(request, barter_type='seed_barter')

        self.assertEqual(len(response.data['barters']), 9)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for barter_type in BARTER_TYPES:
            response = views.retrieve(request, barter_type=barter_type)
            self.assertEqual(response.data['barters'][0]['barter_type'], barter_type.split('_')[0])
            self.assertEqual(len(response.data['barters']), 9)
            self.assertEqual(response.status_code, status.HTTP_200_OK)