from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from users_app.serializers import UserMessageSerializer
from .serializers import InboxSerializer, MessageSerializer, ConversationSerializer
from django.contrib.auth import get_user_model
from barters_app.constants import BARTER_CONFIG
from .models import Conversation


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    response = Response()
    sender_id = request.data.get('sender_id')
    recipient_id = request.data.get('recipient_id')
    barter_id = request.data.get('barter_id')
    barter_type = request.data.get('barter_type')
    form_data = request.data.get('form_data')

    error = None
    if not sender_id:
        error = 'Missing senderId.'
    else:
        sender = get_user_model().objects.filter(id=sender_id).first()

        if not sender:
            error = f"Sender with id {sender_id} not found."

    if not recipient_id:
        error = 'Missing recipientId.'
    else:
        recipient = get_user_model().objects.filter(id=recipient_id).first()

        if not recipient:
            error = f"Recipient with id {recipient_id} not found."

    if not barter_id or not barter_type:
        error = 'Missing barterId.' if not barter_id else 'Missing barterType.'
    else:
        BarterModel = BARTER_CONFIG.get(barter_type)['model']
        barter = BarterModel.objects.filter(id=barter_id).first()

        if not barter:
            error = f"No barter of type '{barter_type}' with id {barter_id}"

    if not form_data:
        error = 'Missing formData object.'

    if error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [error]
        }
    else:
        conversation, created = Conversation.objects.get_or_create(
            inbox=barter.creator.inbox,
            barter_id=barter_id,
            barter_type=barter_type,
            sender=request.user,
            recipient=barter.creator
        )

        message_serializer = MessageSerializer(data={
            'body': form_data.get('body'),
            'conversation': conversation.id
        })

        if message_serializer.is_valid():
            message_serializer.save(sender=sender, recipient=barter.creator)
            barter.conversations.add(conversation)
            response.status_code = status.HTTP_201_CREATED
            response.data = {
                'message': "Message created!"
            }

        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {
                'errors': message_serializer.errors
            }

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations(request, conversation_id):
    response = Response()

    conversation = Conversation.objects.filter(id=conversation_id).first()

    if conversation:
        conversation_serializer = ConversationSerializer(conversation)

        response.data = {'conversation': conversation_serializer.data}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [f"No conversation found with id {conversation_id}"]
        }

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_conversation(request):
    response = Response()

    barter_id = request.GET.get('barterId')
    barter_type = request.GET.get('barterType')
    sender_id = request.GET.get('senderId')
    recipient_id = request.GET.get('recipientId')

    error = None
    if not barter_type:
        error = "Missing barterType."

    else:
        if not barter_id:
            error = "Missing barterId."
        else:
            BarterModel = BARTER_CONFIG.get(barter_type)['model']
            barter = BarterModel.objects.filter(id=barter_id).first()

            if not barter:
                error = f"No barter of type '{barter_type}' with id {barter_id}"


    if not sender_id:
        error = "Missing senderId."
    else:
        sender = get_user_model().objects.filter(id=sender_id)

        if not sender:
            error = f"Sender with id {sender_id} not found."

    if not recipient_id:
        error = "Missing recipientId."
    else:
        recipient = get_user_model().objects.filter(id=recipient_id)

        if not recipient:
            error = f"Recipient with id {recipient_id} not found."

    if error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'errors': [error]
        }
    else:

        conversation = barter.conversations.all().filter(
            sender__id__in=[sender_id],
            recipient__id__in=[recipient_id]
        ).first()

        conversation_data = {}
        if not conversation:
            response.status_code = status.HTTP_404_NOT_FOUND
            message = 'No conversation found.'
        else:
            conversation_data = ConversationSerializer(conversation).data
            response.status_code = status.HTTP_200_OK
            message = 'Conversation found.'

        response.data = {
            'conversation': conversation_data,
            'message': message
        }

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inbox(request):
    response = Response()

    try:
        inbox_serializer = InboxSerializer(request.user.inbox)

        response.data = {
            'inbox': inbox_serializer.data
        }
    except:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.data = {
            'errors': ['Something went wrong when retrieving inbox data.']
        }

    return response
