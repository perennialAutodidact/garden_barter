from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users_app.authentication import SafeJWTAuthentication

from barters_app.serializers import (MaterialBarterSerializer,
                                     PlantBarterSerializer,
                                     ProduceBarterSerializer,
                                     SeedBarterSerializer,
                                     ToolBarterSerializer)


@api_view(['POST'])
@authentication_classes([SafeJWTAuthentication])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def create(request):
    response = Response()

    response.status_code = status.HTTP_200_OK
    response.data = {
        'message': 'test'
    }

    return response
