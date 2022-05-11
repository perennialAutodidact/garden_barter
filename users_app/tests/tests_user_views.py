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
        self.assertEqual(response.data, {'msg': ["Passwords don't match"]})

    def test_register_fail_email_exists(self):
        request = self.factory.post(
            reverse('users_app:register'),
            self.email_exists_user_data,
            format='json'
        )

        response = views.register(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'msg': ["Email already registered"]})


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


class TestUserDetail(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory()

        self.valid_user, self.valid_refresh_token = self._generate_test_user(
            UserModel=get_user_model(),
            email="valid_user@test.com",
            password="pass3412",
        )

        self.invalid_user, self.expired_refresh_token = self._generate_test_user(
            UserModel=get_user_model(),
            email="invalid_user@test.com",
            password="pass3412",
            token_expiry={'seconds': -10}
        )

        self.inactive_user, self.inactive_refresh_token = self._generate_test_user(
            UserModel=get_user_model(),
            email="inactive_user@test.com",
            password="pass3412",
            is_active=False,
        )

        self.valid_access_token = Token(self.valid_user, 'access')
        self.expired_refresh_token = Token(self.valid_user, 'access', expiry={'minutes':-10})

    def _generate_test_user(self, UserModel:User, email: str, password: str, token_expiry: dict = None, **kwargs) -> 'User':
        '''Generate a User object and RefreshToken for that user.
        UserModel - One of the models from the users_app
        email - string
        password - string
        token_expiry - dict containing the time from creation to expiration for a token. {'hours': 1, 'minutes':1, 'seconds': 1}
        '''

        user, created = UserModel.objects.get_or_create(
            email=email,
            password=password,
        )

        if kwargs:
            for attr, value in kwargs.items():
                setattr(user, attr, value)

        user.save()

        refresh_token = Token(user, 'refresh', expiry=token_expiry)
        user_refresh_token = RefreshToken.objects.get_or_create(
            user=user, token=refresh_token)

        return user, refresh_token

    def test_user_detail_success(self):
        user_id = self.valid_user.id
        request = self.factory.get(reverse('users_app:detail',args=[user_id]), format='json')

        request.COOKIES.update({
            'refreshtoken': self.valid_refresh_token.token
        })

        response = views.extend_token(request)

        user_serializer = UserDetailSerializer(self.valid_user)

        for key, value in user_serializer.data.items():
            self.assertEqual(value, response.data['user'][key])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_fail(self):
        user_id = self.invalid_user.id
        request = self.factory.get(reverse('users_app:detail',args=[user_id]), format='json')
        access_token = Token(self.valid_user, 'access', expiry={'minutes': -10})
        # request.COOKIES.update({
        #     'refreshtoken': self.expired_refresh_token.token
        # })
        headers = {
            'Authorization': f'Token {access_token.token}',
            'X-CSRFToken': generate_csrf_token(request)
        }

        request.headers = headers
        # delay to allow the token to expire
        time.sleep(.1)

        response = views.user_detail(request, 1)

        self.assertEqual(
            response.data, {'msg': ErrorDetail(string='Access token expired', code='authentication_failed')})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_user_detail(self):
        user_id = self.inactive_user.id
        request = self.factory.get(reverse('users_app:detail',args=[user_id]), format='json')
        access_token = Token(self.inactive_user, 'access')

        headers = {
            'Authorization': f'Token {access_token.token}',
            'X-CSRFToken': generate_csrf_token(request)
        }

        request.headers = headers
        request.COOKIES.update({
            'refreshtoken': self.inactive_user.refresh_token.first().token
        })
        

        response = views.user_detail(request, user_id)

        self.assertEqual(response.data, {'detail': ErrorDetail(string='user is inactive', code='authentication_failed')})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_does_not_exist(self):

        access_token = Token(self.valid_user, 'access')

        request = self.factory.get(reverse('users_app:detail',args=[999]), format='json')
        headers = {
            'Authorization': f'Token {access_token.token}',
            'X-CSRFToken': generate_csrf_token(request)
        }

        request.headers = headers

        response = views.user_detail(request, 999)

        self.assertEqual(response.data, {'msg': ['User not found']})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update_success(self):
        access_token = Token(self.valid_user, 'access')

        updated_fields = {
            "first_name": "Bilbo",
            "last_name": "Baggins",
            "username": "HobbitBurglar"
        }

        request = self.factory.put(reverse('users_app:detail',args=[1]), updated_fields, format='json')
        headers = {
            'Authorization': f'Token {access_token.token}',
            'X-CSRFToken': generate_csrf_token(request)
        }

        request.headers = headers
        response = views.user_detail(request, 1)

        user_detail_serializer = UserDetailSerializer(
            self.valid_user, data=updated_fields, partial=True)

        if user_detail_serializer.is_valid():
            user_detail_serializer.save()

        for key, value in user_detail_serializer.initial_data.items():
            self.assertEqual(value, response.data['user'][key])

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
    
    def test_user_update_success(self):
        access_token = Token(self.valid_user, 'access')

        updated_fields = {
            "first_name": "Bilbo",
            "last_name": "Baggins",
            "username": "HobbitBurglar"
        }

        request = self.factory.put(reverse('users_app:detail',args=[1]), updated_fields, format='json')
        headers = {
            'Authorization': f'Token {access_token.token}',
        }

        request.headers = headers
        response = views.user_detail(request, 1)

        user_detail_serializer = UserDetailSerializer(
            self.valid_user, data=updated_fields, partial=True)

        if user_detail_serializer.is_valid():
            user_detail_serializer.save()

        for key, value in user_detail_serializer.initial_data.items():
            self.assertEqual(value, response.data['user'][key])

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
