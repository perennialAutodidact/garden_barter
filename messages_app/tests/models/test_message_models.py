from django.contrib.auth import get_user_model

from django.test import TransactionTestCase

from django.db.utils import IntegrityError
from users_app.models import *
from messages_app.models import *


class MessagesModelsBaseTestCase(TransactionTestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.sender = User.objects.create_user(
            email='sender@test.com',
            password='pass3412'
        )
        self.recipient = User.objects.create_user(
            email='recipient@test.com',
            password='pass3412'
        )


class MessageTestCase(MessagesModelsBaseTestCase):
    def test_user_inbox_exists(self):
        self.assertIsNotNone(self.sender.inbox)
        self.assertIsNotNone(self.recipient.inbox)

