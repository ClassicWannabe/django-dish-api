from django.urls import reverse
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params) -> Recipe:
    """Create and return a sample recipe"""
    defaults = {"time_min": 5, "price": 4.99, "title": "Sample Recipe"}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests:
    """Test unauthenticated recipe API access"""

    def test_auth_required(self, api_client) -> None:
        """Test that authentication is required"""
        response = api_client.get(RECIPES_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class PrivateRecipeAPITests:
    """Test authenticated recipe API access"""

    def test_retrieve_recipes(self, api_client, simple_user) -> None:
        """Test retrieving a list of recipes"""
        sample_recipe(simple_user)
        sample_recipe(simple_user)

        response = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_recipes_limited_to_user(
        self, api_client, simple_user, django_user_model
    ) -> None:
        """Test retrieving recipes for user"""
        user2 = django_user_model.objects.create_user("sample@yandex.ru", "PassworD")
        sample_recipe(simple_user)
        sample_recipe(user2)

        response = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=simple_user)
        serializer = RecipeSerializer(recipes, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data == serializer.data
