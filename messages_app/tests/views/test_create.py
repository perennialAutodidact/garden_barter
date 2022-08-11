from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from users_app.serializers import UserDetailSerializer, UserMessageSerializer
from barters_app.models import SeedBarter
from rest_framework.test import force_authenticate
from messages_app import views
from rest_framework import status


class TestBarterCreate(TestCase):
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

        self.message_body = "Let's trade!"

    def generate_request(self, data):
        '''return a Factory.post() request with the provided data'''
        return self.factory.post(
            reverse('messages_app:create'),
            data,
            format='json'
        )

    def test_message_create_success(self):
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                'recipientId': self.recipient.id,
                'barterId': self.seed_barter.uuid,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.recipient.inbox.conversations.count(), 1)
        
        conversation = self.recipient.inbox.conversations.first()
        self.assertEqual(conversation.messages.count(), 1)

        self.assertEqual(self.seed_barter.conversations.count(), 1)

    def test_message_create_fail_missing_sender_id(self):
        # missing senderId
        request = self.generate_request(
            {
                # 'senderId': self.sender.id,
                'recipientId': self.recipient.id,
                'barterId': self.seed_barter.id,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], ['Missing senderId.'])
    
    def test_message_create_fail_missing_recipient_id(self):
        # missing recipientId
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                # 'recipientId': self.recipient.id,
                'barterId': self.seed_barter.uuid,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], ['Missing recipientId.'])
    
    def test_message_create_fail_missing_sender_id(self):
        # missing barterId
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                'recipientId': self.recipient.id,
                # 'barterId': self.seed_barter.id,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], ['Missing barterId.'])

    def test_message_create_fail_missing_barter_type(self):
        # missing barterType
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                'recipientId': self.recipient.id,
                'barterId': self.seed_barter.uuid,
                # 'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], ['Missing barterType.'])
   

    def test_message_create_fail_sender_does_not_exist(self):
        # sender doesn't exist
        invalid_user_id = 999
        request = self.generate_request(
            {
                'senderId': invalid_user_id,
                'recipientId': self.recipient.id,
                'barterId': self.seed_barter.uuid,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], [
                        f"Sender with id {invalid_user_id} not found."])

    def test_message_create_fail_sender_does_not_exist(self):
        # recipient doesn't exist
        invalid_user_id = 999
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                'recipientId': invalid_user_id,
                'barterId': self.seed_barter.uuid,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], [
                        f"Recipient with id {invalid_user_id} not found."])

    def test_message_create_fail_barter_does_not_exist(self):
        # barter doesn't exist
        invalid_barter_id = 999
        request = self.generate_request(
            {
                'senderId': self.sender.id,
                'recipientId': self.recipient.id,
                'barterId': invalid_barter_id,
                'barterType': self.seed_barter.barter_type,
                'messageBody': self.message_body
            }
        )
        force_authenticate(request, user=self.sender)

        response = views.create(request)

        self.assertIn('errors', response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'], [
                         f"No barter of type '{self.seed_barter.barter_type}' with id {invalid_barter_id}"])
