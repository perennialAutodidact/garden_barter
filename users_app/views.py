from weakref import ref
from django.shortcuts import render

import jwt

from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.decorators import (
    api_view, permission_classes,
    authentication_classes
)

from .authentication import SafeJWTAuthentication
from .models import User, RefreshToken
from .serializers import UserCreateSerializer, UserDetailSerializer, UserUpdateSerializer
from .utils import Token


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    '''Validate request POST data and create new User objects in database
    Set refresh cookie and return access token on successful registration'''
    # create response object
    response = Response()

    user = get_user_model().objects.filter(email=request.data.get('email')).first()
    if user:
        response.data = {'errors': ["Email already registered"]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    # serialize request JSON data
    new_user_serializer = UserCreateSerializer(data=request.data)

    if request.data.get('password') != request.data.get('password_2'):
        # if password and password2 don't match return status 400
        response.data = {'errors': ["Passwords don't match"]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    if new_user_serializer.is_valid():
        # If the data is valid, create the item in the database
        new_user = new_user_serializer.save()

        # generate access and refresh tokens for the new user
        # access_token = Token(new_user, 'access')
        # refresh_token = Token(new_user, 'refresh')

        # attach the access token to the response data
        # and set the response status code to 201

        # if new_user.username:
        #     new_username = new_user.username
        # else:
        #     new_user.username = new_user.email
        #     new_username = new_user.email

        response.data = {
            'message': [f'Registration complete!'],
        }
        response.status_code = status.HTTP_201_CREATED

        # create refreshtoken cookie
        # response.set_cookie(
        #     key='refreshtoken',
        #     value=refresh_token,
        #     httponly=True,  # to help prevent XSS
        #     samesite='strict',  # to help prevent XSS
        #     domain='localhost',  # change in production
        #     secure=True  # for https connections only
        # )

        # return successful response
        return response

    # if the serialized data is NOT valid
    # send a response with error messages and status code 400
    response.data = {
        'errors': new_user_serializer.errors
    }

    response.status_code = status.HTTP_400_BAD_REQUEST
    # return failed response
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    try:
        user = request.user
        user_serializer = UserDetailSerializer(user)

        if not user.is_active:    
            return Response(
                status=400,
                data={
                    'errors': ['User is not active.']
                }
            )

        return Response(
            status=200,
            data={
                'user': user_serializer.data
            }
        )

    except:
        return Response(
            status=500,
            data={'errors': ['Something went wrong fetching user data']}
        )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request):
    user=request.user
    user_serializer = UserUpdateSerializer(instance=user, data=request.data)

    if user_serializer.is_valid():
        user_serializer.save()
        return Response(
            status=status.HTTP_202_ACCEPTED,
            data={
                'user':user_serializer.data
            }
        )
    
    else: 
        return Response(
            status=400,
            data={
                'errors': user_serializer.errors
            }
        )