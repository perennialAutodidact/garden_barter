from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users_app.authentication import SafeJWTAuthentication


@api_view(['POST'])
@authentication_classes([SafeJWTAuthentication])
# @permission_classes([IsAuthenticated])
def create(request):
    print(request.data)