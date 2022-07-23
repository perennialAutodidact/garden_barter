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



class TestRegister(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.user = get_user_model().objects.create_user(
            email="user1@test.com",
            password="pass3412"
        )

        self.valid_user_data = {
            "email": "user2@test.com",
            "password": "pass3412",
            "password2": "pass3412",
        }

        self.password_mismatch_user_data = {
            "email": "user2@test.com",
            "password": "pass3412",
            "password2": "doesnotmatch",
        }

        self.email_exists_user_data = {
            "email": "user1@test.com",
            "password": "pass3412",
            "password2": "pass3412",
        }

    def test_register_success(self):
        request = self.factory.post(
            reverse('users_app:register'),
            self.valid_user_data,
            format='json'
        )

        response = views.register(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_fail_password_mismatch(self):
        request = self.factory.post(
            reverse('users_app:register'),
            self.password_mismatch_user_data,
            format='json'
        )

        response = views.register(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'errors': ["Passwords don't match"]})

    def test_register_fail_email_exists(self):
        request = self.factory.post(
            reverse('users_app:register'),
            self.email_exists_user_data,
            format='json'
        )

        response = views.register(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'errors': ["Email already registered"]})
