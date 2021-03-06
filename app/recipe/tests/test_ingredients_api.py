from django.urls import reverse
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientAPITests:
    """Test the publicly available ingredients API"""

    def test_login_required(self, api_client) -> None:
        """Test that login required for endpoint access"""
        response = api_client.get(INGREDIENTS_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class PrivateIngredientAPITests:
    """Test the private ingredients API"""

    def test_retrieve_ingredients_list(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test retrieving a list of ingredients"""
        helper_functions.sample_ingredient(user=simple_user, name="Strawberry")
        helper_functions.sample_ingredient(user=simple_user, name="Banana")

        response = api_client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_ingredients_limited_to_user(
        self, api_client, simple_user, django_user_model, helper_functions
    ) -> None:
        """Test that user gets his own ingredients"""
        user2 = django_user_model.objects.create_user(
            "example@gmail.com", "testpassword"
        )
        helper_functions.sample_ingredient(user=user2, name="Oil")

        ingredient = helper_functions.sample_ingredient(user=simple_user, name="Water")

        response = api_client.get(INGREDIENTS_URL)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == ingredient.name

    def test_create_ingredient_successful(self, api_client, simple_user) -> None:
        """Test creating a new ingredient"""
        payload = {"name": "Pumpkin"}

        api_client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=simple_user, name=payload["name"]
        ).exists()

        assert exists

    def test_create_ingredient_invalid(self, api_client, simple_user) -> None:
        """Test creating an invalid ingredient fails"""
        payload = {"name": ""}
        response = api_client.post(INGREDIENTS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_ingredients_assigned_to_recipes(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = helper_functions.sample_ingredient(
            user=simple_user, name="Cabbage"
        )
        ingredient2 = helper_functions.sample_ingredient(user=simple_user, name="Honey")
        recipe = helper_functions.sample_recipe(user=simple_user, title="Cold tea")
        recipe.ingredients.add(ingredient2)

        response = api_client.get(INGREDIENTS_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        assert serializer2.data in response.data
        assert serializer1.data not in response.data

    def test_retrieve_ingredients_assigned_unique(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = helper_functions.sample_ingredient(user=simple_user, name="Pepper")
        helper_functions.sample_ingredient(user=simple_user, name="Cheese")
        recipe1 = helper_functions.sample_recipe(user=simple_user, title="Seasoning")
        recipe2 = helper_functions.sample_recipe(user=simple_user, title="Mohito")
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        response = api_client.get(INGREDIENTS_URL, {"assigned_only": 1})

        assert len(response.data) == 1
