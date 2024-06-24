"""
Test recipe API model.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def create_recipe(user, **params):
    """Create and return recipe."""
    defaults = {
        "user": user,
        "title": "Demo Title",
        "time_minutes": 5,
        "price": Decimal("6.50"),
        "description": "Some demo Description for Recipe.",
        "link": "https://jsonplaceholder.typicode.com/users",
    }
    defaults.update(**params)
    recipe = Recipe.objects.create(**defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Public API Tests for Recipes."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Testing Unauthorized Request."""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Private API test for Recipes."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().people.create_user(
            email="user@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_only_authenticated_user_recipes(self):
        """Test retrieve only authenticated User recipes."""
        other_user = get_user_model().people.create_user(
            email="user2@example.com", password="testpass123"
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
