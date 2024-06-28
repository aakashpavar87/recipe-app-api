"""
Test recipe API model.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from recipe.serializers import RecipeDetailSerializer, RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def create_detail_url(recipe_id):
    """Create detail url."""
    return reverse("recipe:recipe-detail", args=[recipe_id])


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

    def test_get_recipe_detail(self):
        """Testing Recipe Detail API."""
        recipe = create_recipe(user=self.user)
        res = self.client.get(create_detail_url(recipe_id=recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating Recipe from API."""
        payload = {
            "title": "Demo Title",
            "time_minutes": 5,
            "price": Decimal("6.50"),
            "description": "Some demo Description for Recipe.",
            "link": "https://jsonplaceholder.typicode.com/users",
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for key, val in payload.items():
            self.assertEqual(getattr(recipe, key), val)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Testing partial update."""
        original_link = "https://google.com"
        recipe = create_recipe(
            user=self.user, title="My Recipe Title", description="My Demo Description"
        )
        payload = {
            "title": "Updated Title",
            "description": "My Updated Description.",
            "link": original_link,
        }

        res = self.client.patch(create_detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.link, original_link)

        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Testing full update."""
        original_link = "https://google.com"
        recipe = create_recipe(
            user=self.user, title="My Recipe Title", description="My Demo Description"
        )
        payload = {
            "title": "Updated Title",
            "description": "My Updated Description.",
            "link": original_link,
            "time_minutes": 15,
            "price": Decimal("16.50"),
        }

        res = self.client.put(create_detail_url(recipe.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(recipe, key), val)
        self.assertEqual(recipe.user, self.user)

    def test_change_of_user_in_patch(self):
        """Testing change of user in update results in error."""
        new_user = get_user_model().people.create_user(
            email="user5@example.com", password="testpass123"
        )
        recipe = create_recipe(
            user=self.user, title="My Recipe Title", description="My Demo Description"
        )
        payload = {"user": new_user.id}

        res = self.client.patch(create_detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_recipe(self):
        """Testing Delete Recipe."""
        recipe = create_recipe(
            user=self.user, title="My Recipe Title", description="My Demo Description"
        )
        res = self.client.delete(create_detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_another_user(self):
        """Testing another user deletion error."""
        new_user = get_user_model().people.create_user(
            email="user5@example.com", password="testpass123"
        )
        recipe = create_recipe(
            user=new_user, title="My Recipe Title", description="My Demo Description"
        )
        res = self.client.delete(create_detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Testing creating recipes with tags."""
        payload = {
            "title": "Punjabi Dal Makhni",
            "price": Decimal("35.50"),
            "time_minutes": 35,
            "tags": [{"name": "Punjabi"}, {"name": "Lunch"}],
        }
        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creatring recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")
        payload = {
            "title": "Dosa",
            "price": Decimal("35.50"),
            "time_minutes": 35,
            "tags": [{"name": "Indian"}, {"name": "BreakFast"}],
        }
        res = self.client.post(RECIPE_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload["tags"]:
            exists = recipe.tags.filter(name=tag["name"], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tags_on_update(self):
        """Test updating recipes with new tags."""
        recipe = create_recipe(user=self.user)
        payload = {"tags": [{"name": "Dinner"}]}
        url = create_detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(Tag.objects.filter(name="Dinner").exists())

    def test_update_recipe_assigning_existed_tags(self):
        """Test assigning existed tags to recipes while update."""
        breakfast_tag = Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(breakfast_tag)

        lunch_tag = Tag.objects.create(user=self.user, name="Lunch")
        payload = {"tags": [{"name": "Lunch"}]}
        url = create_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        recipe.refresh_from_db()  # Refresh instance from the database
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(lunch_tag, recipe.tags.all())
        self.assertNotIn(breakfast_tag, recipe.tags.all())

    def test_clear_tags_recipe(self):
        """Test clearing tags of recipe."""
        breakfast_tag = Tag.objects.create(user=self.user, name="breakfast")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(breakfast_tag)

        payload = {"tags": []}
        url = create_detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()  # Refresh instance from the database
        self.assertEqual(recipe.tags.count(), 0)
