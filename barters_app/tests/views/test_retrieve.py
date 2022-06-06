from barters_app import views
from barters_app.models import (Barter, MaterialBarter, PlantBarter, ProduceBarter,
                                SeedBarter, ToolBarter)
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from django.test import TestCase
from django.urls import reverse
from barters_app.serializers import SeedBarterSerializer
from barters_app.serializers import BarterSerializer
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from users_app.serializers import UserDetailSerializer
from users_app.utils import Token, generate_test_user
from barters_app.tests.utils import enrich_request
from users_app.models import RefreshToken
from barters_app.constants import BARTER_CONFIG


class TestBarterRetrieve(TestCase):
    @classmethod
    def setUpTestData(self):
        users = []
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)
        models = {
            'seed': SeedBarter,
            'plant': PlantBarter,
            'produce': ProduceBarter,
            'material': MaterialBarter,
            'tool': ToolBarter
        }

        for i in range(3):
            user = get_user_model().objects.create_user(
                email=f"user_{i}@gardenbarter.com",
                password='pass3412'
            )

            users.append(user)
            for barter_type in models:
                for i in range(3):
                    Model=models[barter_type]
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
    

            


        self.user_1, self.user_2, self.user_3 = users

        self.valid_refresh_token = RefreshToken.objects.create(
            user=self.user_1,
            token=Token(user, 'refresh').token
        )
        self.valid_access_token = Token(self.user_1, 'access')


        self.invalid_refresh_token = RefreshToken.objects.create(
            user=self.user_2,
            token=Token(
                self.user_2,
                'refresh',
                expiry={'days': -1}
            ).token,
        )
        self.invalid_access_token = Token(
            self.user_2,
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

        # get all barters in the test db
        response = views.retrieve(request)
        self.assertEqual(len(response.data['barters']), 45)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # get all of a particular type of barter
        for barter_type in BARTER_CONFIG:
            response = views.retrieve(request, barter_type=barter_type)
            # the barter_type will be the first part of '*_barter' 
            self.assertEqual(response.data['barters'][0]['barter_type'], barter_type.split('_')[0])
            self.assertEqual(len(response.data['barters']), 9)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        
        # get single item from each model
        for barter_type in BARTER_CONFIG:
            BarterModel = BARTER_CONFIG[barter_type]['model']
            barter_id = BarterModel.objects.first().id
            response = views.retrieve(request, barter_type=barter_type, barter_id=barter_id)

            self.assertEqual(len(response.data['barters']), 1)
            self.assertEqual(response.data['barters'][0]['barter_type'], barter_type.split('_')[0])
            self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_retrieve_list_fail(self):
        request = self.generate_request()

        csrf_token = generate_csrf_token(request)
        request = enrich_request(
            request,
            self.valid_refresh_token,
            self.invalid_access_token,
            csrf_token
        )

        # expired access token
        response = views.retrieve(request)
        self.assertEqual(response.data['msg'], ErrorDetail(string='Access token expired', code='authentication_failed'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # invalid barter_type
        request = enrich_request(
            request,
            self.valid_refresh_token,
            self.valid_access_token,
            csrf_token
        )
        with self.assertRaises(KeyError):
            response = views.retrieve(request, barter_type='floopydoop')

        # invalid barter_id
        invalid_barter_id = 999
        for barter_type in BARTER_CONFIG:
            response = views.retrieve(request, barter_type=barter_type, barter_id=invalid_barter_id)
            self.assertEqual(response.data['error'], f"No barter found of type '{barter_type}' with id {invalid_barter_id}.")

