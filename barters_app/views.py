from datetime import timedelta

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from barters_app.serializers import BarterSerializer
from users_app.authentication import SafeJWTAuthentication

from barters_app.models import (Barter, MaterialBarter, PlantBarter,
                                ProduceBarter, SeedBarter, ToolBarter)
from barters_app.serializers import (BarterSerializer,
                                     MaterialBarterSerializer,
                                     PlantBarterSerializer,
                                     ProduceBarterSerializer,
                                     SeedBarterSerializer,
                                     ToolBarterSerializer)

required_fields = [
    field.name 
    for field in SeedBarter._meta.fields
    if not field.null and field.name not in ['id', 'barter_ptr']
]

BARTER_SERIALIZERS =  {
    'seed_barter': SeedBarterSerializer,
    'plant_barter': PlantBarterSerializer,
    'produce_barter': ProduceBarterSerializer,
    'material_barter': MaterialBarterSerializer,
    'tool_barter': ToolBarterSerializer
}

BARTER_MODELS = {
    'seed_barter': SeedBarter,
    'plant_barter': PlantBarter,
    'produce_barter': ProduceBarter,
    'material_barter': MaterialBarter,
    'tool_barter': ToolBarter
}


@api_view(['POST'])
@authentication_classes([SafeJWTAuthentication])
@permission_classes([IsAuthenticated])
def create(request):
    response = Response()

    form_data = request.data.get('form_data')
    barter_type = request.data.get('barter_type')
    user_data = request.data.get('user_data')

    error = None
    if not form_data:
        error = f"Missing 'formData' object. Required form fields: {', '.join(required_fields)}"
    elif not barter_type:
        error = f"Missing property 'barterType'. Choices are {', '.join([key for key in BARTER_SERIALIZERS.keys()])}"
    elif not user_data:
        error = f"Missing 'userData' object."
    else:
        if not form_data.get('is_free') and not form_data.get('will_trade_for'):
            error = "Desired trade missing. An item must be traded for something if 'is_free' is false."
        
    if error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'error': error
        }
        return response

    else:
        user = get_user_model().objects.get(id=user_data['id'])

        # get serializer based on the type of barter the user is creating
        barter_serializer = BARTER_SERIALIZERS.get(barter_type)

        barter_serializer = barter_serializer(data=form_data)

        barter_serializer.initial_data['date_expires'] = timezone.now() + timedelta(days=7)
        barter_serializer.initial_data['barter_type'] = barter_type.split('_')[0]

        if barter_serializer.is_valid():
            barter_serializer.save(creator=user)
            response.status_code = status.HTTP_200_OK
            response.data = {
                'message': 'test',
                'barter': barter_serializer.data
            }
        else:
            response.data = {
                'error': barter_serializer.errors
            }
            response.status_code = status.HTTP_400_BAD_REQUEST


    return response


@api_view(['GET'])
@authentication_classes([SafeJWTAuthentication])
@permission_classes([IsAuthenticated])
def retrieve(request, barter_type=None, barter_id=None):
    response = Response()

    if not barter_type and not barter_id:
        barters = Barter.objects.all()
    elif barter_type and not barter_id:
        BarterModel = BARTER_MODELS[barter_type]
        barters = BarterModel.objects.all()
    elif barter_type and barter_id:
        BarterModel = BARTER_MODELS[barter_type]
        barter = get_object_or_404(BarterModel, id=barter_id)

    barter_serializer = BarterSerializer(barters, many=True)


    response.data = {
        'barters': barter_serializer.data
    }

    return response
