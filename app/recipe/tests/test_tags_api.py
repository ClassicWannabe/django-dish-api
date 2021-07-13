from django.urls import reverse
from rest_framework import status

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class PublicTagsAPITests:
    """Test the publicly available tags API"""

    def test_login_required(self, api_client) -> None:
        """Test that login is required for retrieving tags"""
        response = api_client.get(TAGS_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class PrivateTagsAPITests:
    """Test the authorized user tags API"""

    def test_retrieve_tags(self, simple_user, api_client, helper_functions) -> None:
        """Test retrieving tags"""
        helper_functions.sample_tag(user=simple_user, name="Vegan")
        helper_functions.sample_tag(user=simple_user, name="Dessert")

        response = api_client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")

        serializer = TagSerializer(tags, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_tags_limited_to_user(
        self, simple_user, api_client, django_user_model, helper_functions
    ) -> None:
        """Test that tags returned are for the authenticated user"""
        user2 = django_user_model.objects.create(
            email="otheruser@gmail.com", password="password"
        )
        helper_functions.sample_tag(user=user2, name="Choco")
        tag = helper_functions.sample_tag(user=simple_user, name="Fried")

        response = api_client.get(TAGS_URL)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == tag.name

    def test_create_tag_successful(self, simple_user, api_client) -> None:
        """Test creating a new tag"""
        payload = {"name": "Test Tag"}

        response = api_client.post(TAGS_URL, payload)
        tags = Tag.objects.filter(user=simple_user)

        assert response.status_code == status.HTTP_201_CREATED
        assert tags.exists()
        assert tags[0].name == payload["name"]

    def test_create_tag_invalid(self, simple_user, api_client):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ""}

        response = api_client.post(TAGS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_tags_assigned_to_recipes(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test filtering tags by those assigned to recipes"""
        tag1 = helper_functions.sample_tag(user=simple_user, name="Cold")
        tag2 = helper_functions.sample_tag(user=simple_user, name="Hot")
        recipe = helper_functions.sample_recipe(user=simple_user, title="Super dish")
        recipe.tags.add(tag1)

        response = api_client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        assert serializer1.data in response.data
        assert serializer2.data not in response.data

    def test_retrieve_tags_assigned_unique(
        self, api_client, simple_user, helper_functions
    ) -> None:
        """Test filtering tags by assigned returns unique items"""
        tag = helper_functions.sample_tag(user=simple_user, name="Fresh")
        helper_functions.sample_tag(user=simple_user, name="Lunch")
        recipe1 = helper_functions.sample_recipe(user=simple_user, title="Besbarmak")
        recipe2 = helper_functions.sample_recipe(user=simple_user, title="Kozhe")
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        response = api_client.get(TAGS_URL, {"assigned_only": 1})

        assert len(response.data) == 1
