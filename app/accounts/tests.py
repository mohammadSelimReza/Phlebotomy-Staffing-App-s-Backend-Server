from django.test import TestCase
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model

CustomerUser = get_user_model()
class CustomerUserTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "gender": "Male",
            "birth_date": "1990-01-01",
            "role": CustomerUser.USER,
            "password": "testpassword"
        }

    def test_create_user(self):
        user = CustomerUser.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, "John Doe")
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertEqual(user.role, CustomerUser.USER)
        self.assertTrue(user.check_password("testpassword"))
        self.assertTrue(user.is_active)

    def test_create_user_without_email(self):
        self.user_data['email'] = ""
        with self.assertRaises(ValueError):
            CustomerUser.objects.create_user(**self.user_data)

    def test_create_superuser(self):
        superuser_data = self.user_data.copy()
        superuser_data['role'] = CustomerUser.ADMIN
        user = CustomerUser.objects.create_superuser(**superuser_data)
        self.assertEqual(user.role, CustomerUser.ADMIN)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_user_username_generated_from_email(self):
        user_data = self.user_data.copy()
        user_email = user_data["email"]
        emailUserName,_ = user_email.split("@")
        user_data['username'] = emailUserName  # Don't pass username
        user = CustomerUser.objects.create_user(**user_data)
        self.assertEqual(user.username, "john.doe")

    def test_role_choices(self):
        valid_roles = [CustomerUser.ADMIN, CustomerUser.USER, CustomerUser.PHLEBOTOMIST, CustomerUser.BUSINESS_OWNER]
        for role in valid_roles:
            user_data = self.user_data.copy()
            user_data['role'] = role
            user = CustomerUser.objects.create_user(**user_data)
            self.assertEqual(user.role, role)

    def test_invalid_role(self):
        invalid_data = self.user_data.copy()
        invalid_data['role'] = 'invalid_role'
        with self.assertRaises(ValidationError):
            CustomerUser.objects.create_user(**invalid_data)
