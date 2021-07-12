from django.urls import reverse
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id: int) -> str:
    """Return recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])


class PublicRecipeAPITests:
    """Test unauthenticated recipe API access"""

    def test_auth_required(self, api_client) -> None:
        """Test that authentication is required"""
        response = api_client.get(RECIPES_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class PrivateRecipeAPITests:
    """Test authenticated recipe API access"""

    def test_retrieve_recipes(self, api_client, simple_user, helper_functions) -> None:
        """Test retrieving a list of recipes"""
        helper_functions.sample_recipe(simple_user)
        helper_functions.sample_recipe(simple_user)

        response = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_recipes_limited_to_user(
        self, api_client, simple_user, django_user_model, helper_functions
    ) -> None:
        """Test retrieving recipes for user"""
        user2 = django_user_model.objects.create_user("sample@yandex.ru", "PassworD")
        helper_functions.sample_recipe(simple_user)
        helper_functions.sample_recipe(user2)

        response = api_client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=simple_user)
        serializer = RecipeSerializer(recipes, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data == serializer.data

    def test_view_recipe_detail(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test viewing a recipe detail"""
        recipe = helper_functions.sample_recipe(user=simple_user)
        recipe.tags.add(helper_functions.sample_tag(user=simple_user))
        recipe.ingredients.add(helper_functions.sample_ingredient(user=simple_user))

        url = recipe_detail_url(recipe.id)
        response = api_client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data
