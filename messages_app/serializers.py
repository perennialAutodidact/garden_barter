from rest_framework import serializers
from .models import Inbox, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class InboxSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Inbox
        fields = ['user', 'messages']
