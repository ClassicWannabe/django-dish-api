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

    def test_retrieve_tags(self, simple_user, api_client) -> None:
        """Test retrieving tags"""
        Tag.objects.create(user=simple_user, name="Vegan")
        Tag.objects.create(user=simple_user, name="Dessert")

        response = api_client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")

        serializer = TagSerializer(tags, many=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_tags_limited_to_user(
        self, simple_user, api_client, django_user_model
    ) -> None:
        """Test that tags returned are for the authenticated user"""
        user2 = django_user_model.objects.create(
            email="otheruser@gmail.com", password="password"
        )
        Tag.objects.create(user=user2, name="Choco")
        tag = Tag.objects.create(user=simple_user, name="Fried")

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
