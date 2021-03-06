import decimal
import tempfile
import os

from PIL import Image

from django.urls import reverse
from rest_framework import status

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id: int) -> str:
    """Return URL for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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


class RecipeImageUploadTests:
    """Test image uploads for recipe API"""

    def test_upload_image_successful(self, recipe_for_image_upload, api_client) -> None:
        """Test uploading an image to recipe"""
        url = image_upload_url(recipe_for_image_upload.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            response = api_client.post(url, {"image": ntf}, format="multipart")

        recipe_for_image_upload.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert "image" in response.data
        assert os.path.exists(recipe_for_image_upload.image.path)

    def test_upload_image_failed(self, recipe_for_image_upload, api_client) -> None:
        """Test uploading an invalid image"""
        url = image_upload_url(recipe_for_image_upload.id)
        response = api_client.post(url, {"image": "fakeimage"}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_recipes_by_tags(
        self, simple_user, api_client, helper_functions
    ) -> None:
        """Test returning recipes with specific tags"""
        recipe1 = helper_functions.sample_recipe(user=simple_user, title="Sushi")
        recipe2 = helper_functions.sample_recipe(user=simple_user, title="Cereal")
        tag1 = helper_functions.sample_tag(user=simple_user, name="East kitchen")
        tag2 = helper_functions.sample_tag(user=simple_user, name="Easy level")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = helper_functions.sample_recipe(user=simple_user, title="Manty")

        response = api_client.get(RECIPES_URL, {"tags": f"{tag1.id},{tag2.id}"})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        assert serializer1.data in response.data
        assert serializer2.data in response.data
        assert serializer3.data not in response.data

    def test_filter_recipes_by_ingredients(
        self, simple_user, api_client, helper_functions
    ) -> None:
        """Test returning recipes with specific ingredients"""
        recipe1 = helper_functions.sample_recipe(user=simple_user, title="Pirozhki")
        recipe2 = helper_functions.sample_recipe(
            user=simple_user, title="Fried chicken"
        )
        ingredient1 = helper_functions.sample_ingredient(
            user=simple_user, name="Potato"
        )
        ingredient2 = helper_functions.sample_ingredient(
            user=simple_user, name="Chicken"
        )
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = helper_functions.sample_recipe(user=simple_user, title="Boiled eggs")

        response = api_client.get(
            RECIPES_URL, {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        assert serializer1.data in response.data
        assert serializer2.data in response.data
        assert serializer3.data not in response.data
