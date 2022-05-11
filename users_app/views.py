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
# from .utils import generate_access_token, generate_refresh_token
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
        response.data = {'msg': ["Email already registered"]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    # serialize request JSON data
    new_user_serializer = UserCreateSerializer(data=request.data)

    if request.data.get('password') != request.data.get('password_2'):
        # if password and password2 don't match return status 400
        response.data = {'msg': ["Passwords don't match"]}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    if new_user_serializer.is_valid():
        # If the data is valid, create the item in the database
        new_user = new_user_serializer.save()

        # generate access and refresh tokens for the new user
        access_token = Token(new_user, 'access')
        refresh_token = Token(new_user, 'refresh')

        # attach the access token to the response data
        # and set the response status code to 201

        if new_user.username:
            new_username = new_user.username
        else:
            new_user.username = new_user.email
            new_username = new_user.email

        response.data = {
            'accessToken': access_token.token,
            'msg': [f'Welcome, {new_username}!'],
            'user': UserDetailSerializer(new_user).data
        }
        response.status_code = status.HTTP_201_CREATED

        # create refreshtoken cookie
        response.set_cookie(
            key='refreshtoken',
            value=refresh_token,
            httponly=True,  # to help prevent XSS
            samesite='strict',  # to help prevent XSS
            domain='localhost',  # change in production
            secure=True  # for https connections only
        )

        # return successful response
        return response

    # if the serialized data is NOT valid
    # send a response with error messages and status code 400
    response.data = {
        'msg': new_user_serializer.errors
    }

    response.status_code = status.HTTP_400_BAD_REQUEST
    # return failed response
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    '''
    POST: Validate User credentials and generate refresh and access tokens
    '''
    # create response object
    response = Response()

    email = request.data.get('email')
    password = request.data.get('password')

    if email is None or password is None:
        response.data = {'msg': ['Username and password required.']}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    user = User.objects.filter(email=email).first()

    if user is None or not user.check_password(password):
        response.data = {
            'msg': ['Incorrect email or password']
        }
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    # generate access and refresh tokens for the current user
    access_token = Token(user, 'access')
    refresh_token = Token(user, 'refresh')

    try:
        # if the user has a refresh token in the db,
        # get the old token
        old_refresh_tokens = RefreshToken.objects.filter(user=user.id)

        for token in old_refresh_tokens:
            # delete the old token
            token.delete()

        # generate new token
        RefreshToken.objects.create(user=user, token=refresh_token)

    except RefreshToken.DoesNotExist:

        # assign a new refresh token to the current user
        RefreshToken.objects.create(user=user, token=refresh_token)

    # create refreshtoken cookie
    response.set_cookie(
        key='refreshtoken',  # cookie name
        value=refresh_token,  # cookie value
        httponly=True,  # to help prevent XSS
        domain='localhost',  # change in production
        samesite='strict',  # to help prevent XSS
        secure=True  # for https connections only
    )

    # return the access token in the reponse
    response.data = {
        'accessToken': access_token.token,
        'msg': ['Login successful!'],
        'user': UserDetailSerializer(user).data
    }
    response.status_code = status.HTTP_200_OK
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([SafeJWTAuthentication])
@ensure_csrf_cookie
def auth(request):
    '''Return the user data for the user id contained in a valid access token'''
    # create response object
    response = Response()

    # Get the access token from headers
    access_token = request.headers.get('Authorization')

    # if the access token doesn't exist, return 401
    if access_token is None:
        response.data = {'msg': ['No access token']}
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    # remove 'token' prefix
    access_token = access_token.split(' ')[1]

    # decode access token payload
    payload = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=['HS256']
    )

    # get the user with the same id as the token's user_id
    user = User.objects.filter(id=payload.get('user_id')).first()

    if user is None:
        response.data = {'msg': ['User not found']}
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    if not user.is_active:
        response.data = {'msg': ['User not active']}
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    # serialize the User object and attach to response data
    serialized_user = UserDetailSerializer(instance=user)
    response.data = {'user': serialized_user.data}
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def extend_token(request):
    '''Return new access token if request's refresh token cookie is valid'''
    # create response object
    response = Response()

    # get the refresh token cookie
    refresh_token = request.COOKIES.get('refreshtoken')

    # if the refresh token doesn't exist
    # return 401 - Unauthorized
    if refresh_token is None:
        response.data = {
            'msg': ['Missing refresh token']
        }

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    # if the refresh_token doesn't exist in the database,
    # return 401 - Unauthorized
    user_refresh_token = RefreshToken.objects.filter(
        token=refresh_token).first()

    if user_refresh_token is None:
        response.data = {
            'msg': ['Refresh token does not belong to an active user.']
        }

        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    # if a token is found,
    # try to decode it
    
    payload = Token.get_payload(refresh_token, 'refresh')

    if not payload:
        # if the token is expired, delete it from the database
        # return 401 Unauthorized

        # find the expired token in the database
        expired_tokens = RefreshToken.objects.filter(
            token=refresh_token).first()

        for token in expired_tokens:
            # delete the old token
            token.delete()

        response.data = {
            'msg': ['Expired refresh token, please log in again.']
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED

        # remove exipred refresh token cookie
        response.delete_cookie('refreshtoken')
        return response

    # if the token is valid,
    # get the user asscoiated with token
    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        response.data = {
            'msg': ['User not found']
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    if not user.is_active:
        response.data = {
            'msg': ['User is inactive']
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return response

    # generate new refresh token for the user
    new_refresh_token = Token(user, 'refresh').token

    # Delete old refresh token
    # if the user has a refresh token in the db,
    # get the old token
    old_refresh_token = RefreshToken.objects.filter(user=user.id).first()
    if old_refresh_token:
        # delete the old token
        old_refresh_token.delete()

    # assign a new refresh token to the current user
    RefreshToken.objects.create(user=user, token=new_refresh_token)

    # change refreshtoken cookie
    response.set_cookie(
        key='refreshtoken',  # cookie name
        value=new_refresh_token,  # cookie value
        httponly=True,  # to help prevent XSS attacks
        samesite='strict',  # to help prevent XSS attacks
        domain='localhost',  # change in production
        # secure=True # for https connections only
    )

    # generate new access token for the user
    new_access_token = Token(user, 'access').token

    user_serializer = UserDetailSerializer(user)

    response.data = {'accessToken': new_access_token, 'user': user_serializer.data}
    return response


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([SafeJWTAuthentication])
@ensure_csrf_cookie
def user_detail(request, pk):
    '''
    GET: Get the user data associated with the pk
    PUT: Update the user data associated with the pk
    '''
    # Create response object
    response = Response()

    # find the user associated with
    # the pk passed in the url
    user = User.objects.filter(pk=pk).first()


    if user is None:
        response.data = {
            'msg': ['User not found']
        }
        response.status_code = status.HTTP_401_UNAUTHORIZED

        return response


    # Get the access token from request headers
    access_token = request.headers.get('Authorization').split(' ')[1]

    # decode token payload
    payload = jwt.decode(
        access_token,
        settings.ACCESS_TOKEN_SECRET,
        algorithms=['HS256']
    )
    
    # GET = view user details
    if request.method == 'GET':
        serialized_user = UserDetailSerializer(instance=user)

        response.data = {'user': serialized_user.data}
        response.status_code = status.HTTP_200_OK

        return response

    # PUT = update user info
    if request.method == 'PUT':

        # partial = True will allow for User fields to be missing
        serialized_user = UserUpdateSerializer(instance=user, data=request.data, partial=True)

        if serialized_user.is_valid():
            # combine updated with the current user instance and serialize
            updated_user = serialized_user.save()
            
            user_detail_serializer = UserDetailSerializer(instance=updated_user)

            response.data = {
                'msg': ['Account info updated successffully'],
                'user': user_detail_serializer.data
            }
            response.status_code = status.HTTP_202_ACCEPTED
            return response

        response.data = {'msg': serialized_user.errors}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def logout(request):
    '''Delete refresh token from the database
    and delete the refreshtoken cookie'''
    # Create response object
    response = Response()

    # id of logged in user from request data
    logged_in_user = request.data.get('user')

    # find the logged in user's refresh token
    refresh_token = RefreshToken.objects.filter(
        user=logged_in_user['id']).first()

    if refresh_token is None:
        response.data = {'msg': ['Not logged in']}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    # if the token is found, delete it
    refresh_token.delete()

    # delete the refresh cookie
    response.delete_cookie('refreshtoken')

    response.data = {
        'msg': ['Logout successful. See you next time!']
    }

    return response
