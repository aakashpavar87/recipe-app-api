"""Testing User Model."""

from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")


class PublicUserTests(test.TestCase):
    """Writing test for user model."""

    def setUp(self):
        self.client = APIClient()

    def create_user(self, **options):
        """Create User For other methods."""
        return get_user_model().people.create_user(**options)

    def test_create_user_success(self):
        """Testing For successfull user creation."""
        payload = {
            "email": "user@example.com",
            "password": "testpass123",
            "name": "Test User",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().people.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_already_exists_error(self):
        """Testing If User already Exists."""
        payload = {
            "email": "user@example.com",
            "password": "testpass123",
            "name": "Test User",
        }
        self.create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_short_password(self):
        """Testing User If User has too short password."""
        payload = {
            "email": "user@example.com",
            "password": "py",
            "name": "Test User",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user_exists = get_user_model().people.filter(email=payload["email"]).exists()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)
