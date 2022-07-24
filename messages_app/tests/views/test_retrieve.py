from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from users_app.serializers import UserDetailSerializer
from barters_app.models import SeedBarter
from rest_framework.test import force_authenticate
from messages_app import views
from rest_framework import status
from messages_app.models import Conversation, Message


class TestRetrieveConversation(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.sender = get_user_model().objects.create_user(
            email='sender@gardenbarter.com',
            password='pass3412'
        )

        self.recipient = get_user_model().objects.create_user(
            email='recipient@gardenbarter.com',
            password='pass3412'
        )

        self.access_token = str(
            RefreshToken.for_user(self.sender).access_token)

        self.seed_barter = SeedBarter.objects.create(
            creator=self.recipient,
            title='test barter title',
            description='test barter description',
            will_trade_for='item that will be traded',
            is_free=False,
            cross_street_1='123 Faux St.',
            cross_street_2='789 Impostor Rd',
            postal_code='99999',
            barter_type='seed',
            latitude='',
            longitude='',
            genus='leonarus',
            species='cardiaca',
            common_name='motherwort',
        )

        self.message_data = {
            "body": "Let's trade!"
        }

        self.conversation = Conversation.objects.create(
            inbox = self.recipient.inbox,
            barter_id=self.seed_barter.id,
            barter_type=self.seed_barter.barter_type,
            sender = self.sender,
            recipient=self.recipient
        )

        self.message = Message.objects.create(
            body=self.message_data['body'],
            sender = self.sender,
            recipient=self.recipient,
            conversation=self.conversation
        )
    
    def generate_request(self, url_reverse, conversation_id=None, message_id=None):
        '''return a Factory.post() request with the provided data'''
        kwargs = {}
        if conversation_id:
            kwargs['conversation_id'] = conversation_id
        if message_id:
            kwargs['message_id'] = message_id

        return self.factory.get(
            reverse(url_reverse, kwargs=kwargs),
            format='json'
        )

    def test_conversation_retrieve_success(self):
        request = self.generate_request(
            'messages_app:conversations',
            conversation_id=self.conversation.id
        )
        force_authenticate(request, user=self.recipient)

        response = views.conversations(request, self.conversation.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        messages = response.data['conversation']['messages']
        self.assertEqual(len(messages), 1)
    
    def test_conversation_retrieve_fail(self):
        invalid_conversation_id = 999
        request = self.generate_request(
            'messages_app:conversations',
            conversation_id=invalid_conversation_id
        )
        force_authenticate(request, user=self.recipient)

        response = views.conversations(request, invalid_conversation_id)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], [f"No conversation found with id {invalid_conversation_id}"])
        self.assertIn('errors',response.data.keys())


    def test_inbox_retrieve_success(self):
        request = self.generate_request(
            'messages_app:inbox'
        )

        force_authenticate(request, user=self.recipient)

        response = views.inbox(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inbox']['user']['id'], self.recipient.id)
    
    def test_inbox_retrieve_fail(self):
        pass