from django.contrib.auth import get_user_model

from django.test import TransactionTestCase

from django.db.utils import IntegrityError
from users_app.models import *
from barters_app.models import *


class BarterModelBaseTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.user_1 = User.objects.create_user(
            email='user1@test.com',
            password='pass3412'
        )



class BarterTestCase(BarterModelBaseTestCase):
    def test_create_barter(self):
        with self.assertRaises(IntegrityError):
            Barter.objects.create(
                will_trade_for='tomatoes',
                title='test_title',
                postal_code='55555'
            )
        with self.assertRaises(ValueError):
            Barter.objects.create(
                creator=self.user_1,
                title='',
                will_trade_for='tomatoes',
                postal_code='55555'
            )
        with self.assertRaises(ValueError):
            Barter.objects.create(
                creator=self.user_1,
                title='test title',
                will_trade_for='',
                postal_code='55555'
            )
        with self.assertRaises(ValueError):
            Barter.objects.create(
                creator=self.user_1,
                title='test title',
                will_trade_for='tomatoes',
                postal_code=''
            )
        
