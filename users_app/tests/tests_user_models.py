from django.contrib.auth import get_user_model

from django.test import TransactionTestCase

from django.db.utils import IntegrityError
from users_app.models import *


class UserModelBaseTestCase(TransactionTestCase):
    def setUp(self) -> None:

        # create test instructor
        self.valid_user, created = User.objects.get_or_create(
            email='valid_user_1_test_user_models@test.com', 
            password='pass3412',
        )
        if created:
            self.valid_user.set_password(self.valid_user.password)

        self.superuser = User.objects.create_superuser(email="superuser@test.com", password="pass3412")

class SuperUserTestCase(UserModelBaseTestCase):
    def test_create_user(self):
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='some_valid_email@test.com', password='')
        
        self.assertFalse(self.valid_user.is_superuser)

    def test_create_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='some_valid_email@test.com', password="pass3412", is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='some_valid_email@test.com', password="pass3412", is_superuser=False)
        
