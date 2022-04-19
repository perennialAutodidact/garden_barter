from django.contrib.auth import get_user_model

from django.test import TransactionTestCase

from django.db.utils import IntegrityError
from users_app.models import *


class UserModelBaseTestCase(TransactionTestCase):
    def setUp(self) -> None:

        # create test instructor
        self.valid_instructor, created = Instructor.objects.get_or_create(
            email='valid_instructor_1_test_user_models@test.com', 
            password='pass3412',
            is_staff=True
        )
        if created:
            self.valid_instructor.set_password(self.valid_instructor.password)

        # Create test student
        self.enrollment_status, _ = EnrollmentStatus.objects.get_or_create(code='EG')
        self.funding_type, _ = FundingType.objects.get_or_create(title='vettec')
        
        self.valid_student,created = Student.objects.get_or_create(
            email='valid_student_1_test_user_models@test.com',
            password='pass3412',
            enrollment_status=self.enrollment_status,
            funding_type=self.funding_type,
        )
        if created:
            self.valid_instructor.set_password(self.valid_instructor.password)

        self.superuser = User.objects.create_superuser(email="superuser@test.com", password="pass3412")

class SuperUserTestCase(UserModelBaseTestCase):
    def test_create_user(self):
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='some_valid_email@test.com', password='')
        
        self.assertFalse(self.valid_instructor.is_superuser)

    def test_create_superuser(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='some_valid_email@test.com', password="pass3412", is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='some_valid_email@test.com', password="pass3412", is_superuser=False)
        

class InstructorModelTestCase(UserModelBaseTestCase):
    def test_create_instructor(self):
        self.assertEqual(self.valid_instructor.email, "valid_instructor_1_test_user_models@test.com")
        self.assertEqual(True, self.valid_instructor in Instructor.objects.all())
        self.assertTrue(self.valid_instructor.is_staff)
        
        # email already exists
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=self.valid_instructor.email,
                password='pass3412'
            )


        
class StudentModelTestCase(UserModelBaseTestCase):
    def test_create_student(self):
        self.assertEqual(self.valid_student.email, "valid_student_1_test_user_models@test.com")
        self.assertEqual(True, self.valid_student in Student.objects.all())
        self.assertFalse(self.valid_student.is_staff)

        

        

