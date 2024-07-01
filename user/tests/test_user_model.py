"""Testing User Model."""

from django import test
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**options):
    """Create User For other methods."""
    return get_user_model().people.create_user(**options)


class PublicUserTests(test.TestCase):
    """Writing test for user model."""

    def setUp(self):
        self.client = APIClient()

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
        create_user(**payload)
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

    def test_create_token(self):
        """Testing Create Token Successfull."""
        user_details = {
            "email": "user@example.com",
            "password": "testpass123",
            "name": "Test User",
        }
        create_user(**user_details)
        payload = {"email": user_details["email"], "password": user_details["password"]}
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Testing  bad credentials for token."""
        create_user(email="user@example.com", password="testpass123")
        payload = {"email": "", "password": "testpass123"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_empty_password(self):
        """Testing empty credentials for token."""
        create_user(email="user@example.com", password="testpass123")
        payload = {"email": "user@example.com", "password": "badpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_error_me_request(self):
        """Testing Unauthorized Request Error"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTests(test.TestCase):
    """Testing Authorized test case."""

    def setUp(self):
        self.user = create_user(
            email="user@example.com",
            password="testpass123",
            name="Test Name",
            is_verified=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        """Test Retrieving User Profile."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email})

    def test_post_me_not_allowed(self):
        """Testing POST method not Allowed."""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user(self):
        """Testing update user functionality."""
        payload = {"name": "Updated Name", "password": "newpass123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
