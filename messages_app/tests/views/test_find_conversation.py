from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from users_app.serializers import UserDetailSerializer
from messages_app.serializers import ConversationSerializer
from barters_app.models import SeedBarter
from rest_framework.test import force_authenticate
from messages_app import views
from rest_framework import status
from messages_app.models import Conversation, Message


class TestFindConversation(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = APIRequestFactory(enforce_csrf_checks=True)

        self.sender_1 = get_user_model().objects.create_user(
            email='sender1@gardenbarter.com',
            password='pass3412'
        )

        self.sender_2 = get_user_model().objects.create_user(
            email='sender2@gardenbarter.com',
            password='pass3412'
        )

        self.recipient_1 = get_user_model().objects.create_user(
            email='recipient1@gardenbarter.com',
            password='pass3412'
        )

        self.recipient_2 = get_user_model().objects.create_user(
            email='recipient2@gardenbarter.com',
            password='pass3412'
        )

        self.seed_barter_1 = SeedBarter.objects.create(
            creator=self.recipient_1,
            title='test seed barter',
            description='test seed barter description',
            will_trade_for='item that will be traded',
            is_free=False,
            postal_code='99999',
            barter_type='seed',
        )
        self.seed_barter_2 = SeedBarter.objects.create(
            creator=self.recipient_1,
            title='test plant barter',
            description='test plant barter description',
            will_trade_for='item that will be traded',
            is_free=False,
            postal_code='99999',
            barter_type='plant',
        )

        self.message_data = {
            "body": "Let's trade!"
        }

        self.conversation_1 = Conversation.objects.create(
            inbox = self.recipient_1.inbox,
            barter_id=self.seed_barter_1.id,
            barter_type=self.seed_barter_1.barter_type,
            sender = self.sender_1,
            recipient=self.recipient_1
        )
        self.conversation_2 = Conversation.objects.create(
            inbox = self.recipient_1.inbox,
            barter_id=self.seed_barter_1.id,
            barter_type=self.seed_barter_1.barter_type,
            sender = self.sender_2,
            recipient=self.recipient_1
        )
        self.seed_barter_1.conversations.add(self.conversation_1, self.conversation_2)

    def generate_request(self, url_reverse, data):
        '''return a Factory.post() request with the provided data'''

        return self.factory.get(
            reverse(url_reverse),
            data,
            format='json'
        )

    def test_conversation_find_success_conversation_exists(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                'recipientId': self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        test_conversation = ConversationSerializer(self.conversation_1).data
        self.assertEqual(response.data['conversation'], test_conversation)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_conversation_find_fail_conversation_does_not_exist(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_2.id,
                'recipientId': self.recipient_2.id
            }
        )

        force_authenticate(request, user=self.sender_2)

        response = views.find_conversation(request)
        

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['conversation'], {})
        

    def test_conversation_find_fail_missing_barter_id(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                # 'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                'recipientId':self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], ['Missing barterId.'])


    def test_conversation_find_fail_missing_barter_type(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                # 'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                'recipientId':self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], ['Missing barterType.'])

    def test_conversation_find_fail_missing_sender_id(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                # 'senderId': self.sender_1.id,
                'recipientId':self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], ['Missing senderId.'])


    def test_conversation_find_fail_missing_recipient_id(self):
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                # 'recipientId':self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], ['Missing recipientId.'])


    def test_conversation_find_fail_sender_does_not_exist(self):
        invalid_user_id = 999
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': invalid_user_id,
                'recipientId':self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], [f"Sender with id {invalid_user_id} not found."])


    def test_conversation_find_fail_recipient_does_not_exist(self):
        invalid_user_id = 999
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': self.seed_barter_1.id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                'recipientId':invalid_user_id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], [f"Recipient with id {invalid_user_id} not found."])
    
    def test_conversation_find_fail_barter_does_not_exist(self):
        invalid_barter_id = 999
        request = self.generate_request(
            'messages_app:find_conversation',
            {
                'barterId': invalid_barter_id,
                'barterType': self.seed_barter_1.barter_type,
                'senderId': self.sender_1.id,
                'recipientId': self.recipient_1.id
            }
        )

        force_authenticate(request, user=self.sender_1)

        response = views.find_conversation(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.data['errors'], [f"No barter of type '{self.seed_barter_1.barter_type}' with id {invalid_barter_id}"])


   