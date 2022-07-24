from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from barters_app.models import (Barter, SeedBarter, )
from barters_app.serializers import BarterSerializer

from barters_app.constants import BARTER_CONFIG

BARTER_REQUIRED_FIELDS = [
    field.name 
    for field in Barter._meta.fields
    if not field.null and field.name not in ['id', 'barter_ptr']
]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    response = Response()

    user_data = request.data.get('user_data')
    form_data = request.data.get('form_data')
    barter_type = request.data.get('barter_type')

    error = None
    if not form_data:
        error = f"Missing 'formData' object. Required form fields: {', '.join(BARTER_REQUIRED_FIELDS)}"
    elif not barter_type:
        error = f"Missing property 'barterType'. Choices are {', '.join([key for key in BARTER_CONFIG.keys()])}"
    elif not user_data:
        error = f"Missing 'userData' object."
    else:
        if not form_data.get('is_free') and not form_data.get('will_trade_for'):
            error = "Desired trade missing. An item must be traded for something if 'is_free' is false."
        
    if error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [error]
        }
        return response

    else:
        user = get_user_model().objects.get(id=user_data['id'])

        # get serializer based on the type of barter the user is creating
        barter_serializer = BARTER_CONFIG[barter_type]['serializer']

        barter_serializer = barter_serializer(data=form_data)

        barter_serializer.initial_data['date_expires'] = timezone.now() + timedelta(days=14)
        barter_serializer.initial_data['barter_type'] = barter_type.split('_')[0]
        
        if barter_serializer.is_valid():
            barter_serializer.save(creator=user)
            response.status_code = status.HTTP_201_CREATED
            response.data = {
                'message': 'Barter created successfully!',
                'barter': barter_serializer.data
            }
        else:
            response.data = {
                'errors': barter_serializer.errors
            }
            response.status_code = status.HTTP_400_BAD_REQUEST


    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def retrieve(request, barter_type=None, barter_id=None):
    response = Response()

    barter_config = BARTER_CONFIG.get(barter_type)

    # if a barter_type isn't provided,
    # use the generic BarterSerializer
    if barter_config:
        barter_serializer = barter_config.get('serializer')
    else:
        barter_serializer = BarterSerializer

    # get a queryset of barters based on the barter_type,
    # while checking for various errors
    error = ''
    if not barter_type and not barter_id:
        barters = Barter.objects.all()
    elif barter_type and not barter_id:
        BarterModel = BARTER_CONFIG[barter_type]['model']
        barters = BarterModel.objects.all()
    elif barter_type and barter_id:
        BarterModel = BARTER_CONFIG[barter_type]['model']
        barters = BarterModel.objects.filter(id=barter_id)
        if len(barters) == 0:
            error = f"No barter found of type '{barter_type}' with id {barter_id}."

    if error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [error]
        }
    
    else:
        # apply query filters / pagination...
        # 
        barters=barters.order_by('-date_created')

        barter_serializer = barter_serializer(barters, many=True)

        response.data = {
            'barters': barter_serializer.data
        }

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update(request, barter_type, barter_id):
    response = Response()

    if barter_type not in BARTER_CONFIG:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [f"Invalid 'barter_type': '{barter_type}'"]
        }
    else:
        BarterModel = BARTER_CONFIG[barter_type]['model']
        BarterSerializer = BARTER_CONFIG[barter_type]['serializer']

        barter = BarterModel.objects.filter(id=barter_id).first()


        barter_serializer = BarterSerializer(barter, data=request.data, partial=True)

        if barter_serializer.is_valid():
            updated_barter = barter_serializer.save()

            response.status_code = status.HTTP_202_ACCEPTED
            response.data = {
                'barter': updated_barter,
            }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {
                'errors': barter_serializer.errors
            }

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete(request, barter_type, barter_id):
    pass
