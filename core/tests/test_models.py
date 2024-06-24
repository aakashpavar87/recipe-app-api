from django.contrib.auth import get_user_model  # type: ignore
from django.test import TestCase  # type: ignore


class ModelTest(TestCase):
    """Testing custom Models"""

    def test_create_user_with_email_success(self):
        """Creating demo user for testing custom models"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().people.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Testing normalisation of email of user."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().people.create_user(email=email)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):

        with self.assertRaises(ValueError):
            get_user_model().people.create_user("", "testpass123")

    def test_create_super_user(self):
        user = get_user_model().people.create_superuser(
            email="test1@example.com", password="testpass123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
