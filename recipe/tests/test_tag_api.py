"""Test for tag API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from yaml import serialize

import user
from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """create and return detail url with id."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return new user."""
    return get_user_model().people.create_user(email=email, password=password)


class PublicTagsApiTest(TestCase):
    """Test unauthenticated requests."""

    def setUp(self):
        """Creating new API client for testing."""
        self.client = APIClient()

    def test_unauthenticate_request(self):
        """Testing unauthenticated  request."""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test Authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_tags(self):
        """Testing getting tags."""
        Tag.objects.create(user=self.user, name="Fast Food")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by("-name")
        serialize = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialize.data)

    def test_get_specific_tags(self):
        """Testing getting specific user tags."""
        tag = Tag.objects.create(user=self.user, name="Fast Food")
        user2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user2, name="Dessert")

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Only one user is authenticated.
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test Updating Tags."""
        tag = Tag.objects.create(user=self.user, name="Fast Food")
        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test delete tags."""
        tag = Tag.objects.create(user=self.user, name="Fast Food")
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
