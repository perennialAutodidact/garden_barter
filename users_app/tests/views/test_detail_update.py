import time

import jwt
from garden_barter_proj import settings
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token as generate_csrf_token
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIRequestFactory
from users_app import views
from users_app.models import *
from users_app.serializers import (UserCreateSerializer, UserDetailSerializer,
                                   UserUpdateSerializer)
from users_app.utils import Token, generate_test_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import force_authenticate

class TestUserDetail(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory()

        self.valid_user= get_user_model().objects.create_user(
            email="valid_user@test.com",
            password="pass3412",
        )

        self.invalid_user= get_user_model().objects.create_user(
            email="invalid_user@test.com",
            password="pass3412",
        )

        self.inactive_user= get_user_model().objects.create_user(
            email="inactive_user@test.com",
            password="pass3412",
            is_active=False,
        )

        self.access_token = str(RefreshToken.for_user(self.valid_user).access_token)

    def test_user_detail_success(self):
        request = self.factory.get(reverse('users_app:get_user'), format='json')

        force_authenticate(request, user=self.valid_user)

        response = views.get_user(request)

        user_serializer = UserDetailSerializer(self.valid_user)

        for key, value in user_serializer.data.items():
            self.assertEqual(value, response.data['user'][key])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_fail(self):
        request = self.factory.get(reverse('users_app:get_user'), format='json')

        response = views.get_user(request)

        self.assertEqual(
            response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user_detail(self):
        request = self.factory.get(reverse('users_app:get_user'), format='json')

        force_authenticate(request, user=self.inactive_user)

        response = views.get_user(request)

        self.assertEqual(response.data, {'errors': ['User is not active.']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_user_update_success(self):
        updated_fields = {
            "first_name": "Bilbo",
            "last_name": "Baggins",
            "username": "HobbitBurglar"
        }

        request = self.factory.put(reverse('users_app:update'), updated_fields, format='json')

        force_authenticate(request, user=self.valid_user)

        response = views.update(request)

        user_detail_serializer = UserDetailSerializer(
            self.valid_user, data=updated_fields, partial=True)

        if user_detail_serializer.is_valid():
            user_detail_serializer.save()

        for key, value in user_detail_serializer.initial_data.items():
            self.assertEqual(value, response.data['user'][key])

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    