"""
Tests for Ingredient APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    """Creating Detailed URL with id."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="test@example.com", password="testpass123"):
    """Creating and returning new user."""
    return get_user_model().people.create_user(email=email, password=password)


class PublicIngredientApiTest(TestCase):
    """Public API tests for ingredient API."""

    def setUp(self):
        """Creating client."""
        self.client = APIClient()

    def test_public_unauthenticated_request(self):
        """Testing unauhenticated request."""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Private Authenticated Requests."""

    def setUp(self):
        """Setting Up Client and User."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_ingredients(self):
        """Test getting ingredients."""
        Ingredient.objects.create(name="Banana", user=self.user)
        Ingredient.objects.create(name="Carrot", user=self.user)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_only_auth_user(self):
        """Test getting ingredients creted by logged in user."""
        other_user = create_user(email="another@example.com")
        banana = Ingredient.objects.create(name="Banana", user=self.user)
        carrot = Ingredient.objects.create(name="Carrot", user=other_user)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertNotIn(carrot, Ingredient.objects.filter(user=self.user))
        self.assertEqual(res.data[0]["name"], banana.name)
        self.assertEqual(res.data[0]["id"], banana.id)

    def test_update_ingredient(self):
        """Test updating ingredient."""
        ingredient = Ingredient.objects.create(name="Turmeric", user=self.user)
        payload = {"name": "Coriander"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_ingredient(self):
        """Test deleteing ingredient."""
        ingredient = Ingredient.objects.create(name="Turmeric", user=self.user)
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(name="Turmeric").exists())
