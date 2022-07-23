from rest_framework import serializers
from .models import Inbox, Message, Conversation


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Conversation
        fields = '__all__'

class InboxSerializer(serializers.ModelSerializer):
    conversations = ConversationSerializer(many=True)

    class Meta:
        model = Inbox
        fields = '__all__'
