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

class TestLogin(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        get_user_model().objects.create_user(
            email="user2@test.com",
            password="pass3412"
        )

        self.valid_user_data = {
            "email": "user2@test.com",
            "password": "pass3412",
        }

        self.invalid_user_data = {
            "email": "user2@test.com",
            "password1": "doesnotmatch",
        }

    def test_login_success(self):

        request = self.factory.post(
            reverse('users_app:login'),
            self.valid_user_data,
            format='json'
        )

        response = views.login(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_fail(self):

        request = self.factory.post(
            reverse('users_app:login'),
            self.invalid_user_data,
            format='json'
        )

        response = views.login(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
