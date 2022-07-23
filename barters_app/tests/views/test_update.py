from barters_app import views
from barters_app.models import (Barter, MaterialBarter, PlantBarter,
                                ProduceBarter, SeedBarter, ToolBarter)
from barters_app.tests.utils import enrich_request
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from barters_app.serializers import BarterSerializer
from users_app.utils import Token, generate_test_user
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from barters_app.constants import BARTER_CONFIG
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import force_authenticate



class TestBarterUpdate(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory()
        models = {
            'seed': SeedBarter,
            'plant': PlantBarter,
            'produce': ProduceBarter,
            'material': MaterialBarter,
            'tool': ToolBarter
        }

        self.user_1 = get_user_model().objects.create_user(
            email='user1@gardenbarter.com',
            password='pass3412'
        )

        self.access_token = str(RefreshToken.for_user(self.user_1).access_token)

        for i, barter_type in enumerate(models):
            Model=models[barter_type]
            Model.objects.create(
                creator=self.user_1,
                title=f'{barter_type} barter title {i}',
                description= f'{barter_type} barter description {i}',
                will_trade_for= f'item that will be traded {i}',
                is_free= False,
                cross_street_1= '456 Fake St.',
                cross_street_2= '876 Synthetic Ave',
                postal_code= '77777',
                barter_type=barter_type
            )
    
    def generate_request(self, barter_type, barter_id, updated_data):
        '''return a Factory.get() request with the provided data'''

        return self.factory.post(
            reverse('barters_app:retrieve', kwargs={
                'barter_type': barter_type,
                'barter_id': barter_id
            }),
            data=updated_data,
            format='json'
        )

    def test_barter_update_success(self):

        # generate a request for each barter type
        for i, barter_type in enumerate(BARTER_CONFIG):

            # barter model class
            BarterModel = BARTER_CONFIG[barter_type]['model']
            # id of first barter of specific model
            barter_id = BarterModel.objects.first().id
            # shift the barter_type one to the right
            barter_types = list(BARTER_CONFIG.keys())
            updated_barter_type = barter_types[(i+1)%len(barter_types)].split('_')[0]
            updated_barter_data = {
                "title":f'updated {barter_type} barter title {i}',
                "description": f'updated {barter_type} barter description {i}',
                "will_trade_for": f'updated item that will be traded {i}',
                "is_free": False,
                "cross_street_1": 'updated 456 Fake St.',
                "cross_street_2": 'updated 876 Synthetic Ave',
                "postal_code": '11111',
                "barter_type": updated_barter_type
            }

            request = self.generate_request(barter_type, barter_id, updated_barter_data)

            request = enrich_request(
                request,
                self.access_token,
            )
            
            force_authenticate(request, user=self.user_1, token=self.access_token)

            # save the previous date_updated value for comparison after request
            previous_date_updated = BarterModel.objects.get(id=barter_id).date_updated

            #
            response = views.update(request, barter_type=barter_type, barter_id=barter_id)
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

            # check that each field matches the updated values
            updated_barter = response.data['barter']
            for field in updated_barter_data:
                self.assertEqual(
                    getattr(updated_barter, field),
                    updated_barter_data[field]
                )

            # test date_updated attribute
            self.assertGreater(updated_barter.date_updated, previous_date_updated)
            

    def test_barter_update_fail(self):
        barter_id = SeedBarter.objects.first().id
        request = self.generate_request(None, 999, {})

        request = enrich_request(
            request,
            self.access_token,
        )

        force_authenticate(request, user=self.user_1)
        response = views.update(request, None, 999)

        #
        # list of fields that are non-nullable or read-only
        read_only_fields = BarterSerializer.Meta.read_only_fields
        required_fields = [
            f.name 
            for f in SeedBarter._meta.get_fields() 
            if not f.null and f.name not in read_only_fields
        ]

        # create a request for each model type
        for i, barter_type in enumerate(BARTER_CONFIG):
            BarterModel = BARTER_CONFIG[barter_type]['model']
            barter_id = BarterModel.objects.first().id

            # populate update request data for various fields
            for field in required_fields:
                updated_barter_data = {}
                if field == 'is_free' or field == 'will_trade_for':
                    updated_barter_data['is_free'] = False
                    updated_barter_data['will_trade_for'] = ''
                else:
                    updated_barter_data[field] = ''

                request = self.generate_request(barter_type, barter_id, updated_barter_data)

                request = enrich_request(
                    request,
                    self.access_token,
                )

                force_authenticate(request, user=self.user_1)

                response = views.update(request, barter_type, barter_id)

                # self.assertIn('errors', response.data.keys())
                # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
