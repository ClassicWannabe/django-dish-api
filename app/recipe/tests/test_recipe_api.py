import decimal

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

    def test_create_basic_recipe(self, api_client, simple_user) -> None:
        """Test creating recipe"""
        payload = {"title": "Rice porridge", "time_min": 20, "price": 1.99}

        response = api_client.post(RECIPES_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=response.data["id"])
        for key in payload:
            recipe_attr = getattr(recipe, key)
            if isinstance(recipe_attr, decimal.Decimal):
                recipe_attr = float(recipe_attr)
            assert payload[key] == recipe_attr

    def test_create_with_tags(self, api_client, simple_user, helper_functions) -> None:
        """Test creating a recipe with tags"""
        tag1 = helper_functions.sample_tag(user=simple_user, name="Milk free")
        tag2 = helper_functions.sample_tag(user=simple_user, name="Sugar free")
        payload = {
            "title": "Steak",
            "tags": [tag1.id, tag2.id],
            "time_min": 60,
            "price": 20,
        }

        response = api_client.post(RECIPES_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=response.data["id"])
        tags = recipe.tags.all()

        assert tags.count() == 2
        assert tag1 in tags and tag2 in tags

    def test_create_recipe_with_ingredients(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test creating a recipe with ingredients"""
        ingredient1 = helper_functions.sample_ingredient(
            user=simple_user, name="Orange"
        )
        ingredient2 = helper_functions.sample_ingredient(user=simple_user, name="Apple")
        payload = {
            "title": "Fruit Salad",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_min": 5,
            "price": 0.99,
        }
        response = api_client.post(RECIPES_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED

        recipe = Recipe.objects.get(id=response.data["id"])
        ingredients = recipe.ingredients.all()

        assert ingredients.count() == 2
        assert ingredient1 in ingredients and ingredient2 in ingredients

    def test_partial_update_recipe(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test updating a recipe with patch"""
        recipe = helper_functions.sample_recipe(user=simple_user)
        recipe.tags.add(helper_functions.sample_tag(user=simple_user))
        new_tag = helper_functions.sample_tag(user=simple_user, name="Dry")
        payload = {"title": "Fruit Paradise", "tags": [new_tag.id]}
        url = recipe_detail_url(recipe.id)

        response = api_client.patch(url, payload)

        recipe.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert recipe.title == payload["title"]

        tags = recipe.tags.all()

        assert len(tags) == 1
        assert new_tag in tags

    def test_full_update_recipe(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test updating a recipe with put"""
        recipe = helper_functions.sample_recipe(user=simple_user)
        recipe.tags.add(helper_functions.sample_tag(user=simple_user))
        payload = {"title": "Black Ice Cream", "time_min": 10, "price": 10}
        url = recipe_detail_url(recipe.id)

        response = api_client.put(url, payload)

        recipe.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert recipe.title == payload["title"]
        assert recipe.time_min == payload["time_min"]
        assert recipe.price == payload["price"]

        tags = recipe.tags.all()

        assert len(tags) == 0
