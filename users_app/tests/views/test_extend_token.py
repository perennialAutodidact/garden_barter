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
from users_app.utils import Token

class TestExtendToken(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.user = get_user_model().objects.create_user(
            email="user2@test.com",
            password="pass3412"
        )

        refresh_token = Token(self.user, 'refresh')
        RefreshToken.objects.create(user=self.user, token=refresh_token)

    def test_extend_token_success(self):
        request = self.factory.get('/token/', format='json')
        csrf_token = generate_csrf_token(request)

        refresh_token = self.user.refresh_token.first()

        request.COOKIES.update({
            'refreshtoken': refresh_token.token,
            'csrftoken': csrf_token
        })

        response = views.extend_token(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_extend_token_fail(self):
        request = self.factory.get('/token/', format='json')
        csrf_token = generate_csrf_token(request)

        refresh_token = self.user.refresh_token.first()

        request.COOKIES = {}

        response = views.extend_token(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'msg': ['Missing refresh token']})

    def test_extend_token_nonexistent_user(self):
        request = self.factory.get('/token/', format='json')
        csrf_token = generate_csrf_token(request)

        user = get_user_model().objects.create_user(
            email='invalid@test.com', password='pass3412')

        refresh_token = Token(user, 'refresh')

        user.delete()

        request.COOKIES.update({
            'refreshtoken': refresh_token.token,
            'csrftoken': csrf_token
        })

        response = views.extend_token(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data, {'msg': ['Refresh token does not belong to an active user.']})

