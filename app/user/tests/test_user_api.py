import pytest

from django.urls import reverse
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

pytestmark = pytest.mark.django_db


class PublicUserAPITests:
    """Test the users API (public)"""

    def test_create_valid_user_successful(self, django_user_model, api_client) -> None:
        """Test creating user with valid payload is successful"""
        payload = {
            "email": "ruslaneleusinov@gmail.com",
            "password": "testpass123",
            "name": "Rus Sur",
        }

        response = api_client.post(CREATE_USER_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        user = django_user_model.objects.get(**response.data)
        assert user.check_password(payload["password"])
        assert "password" not in response.data

    def test_user_exists(self, create_user, api_client) -> None:
        """Test creating user that already exists"""
        payload = {
            "email": "ruslaneleusinov@gmail.com",
            "password": "testpass123",
            "name": "Rus Sur",
        }

        create_user(**payload)

        response = api_client.post(CREATE_USER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_too_short(self, django_user_model, api_client) -> None:
        """Test that the password must be more than 5 characters"""
        payload = {
            "email": "ruslaneleusinov@gmail.com",
            "password": "pass",
            "name": "rus",
        }

        response = api_client.post(CREATE_USER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not django_user_model.objects.filter(email=payload["email"]).exists()

    def test_create_token_for_user(self, create_user, api_client) -> None:
        """Test that token is created for the user"""
        payload = {
            "email": "ruslaneleusinov@gmail.com",
            "password": "passw",
            "name": "rus",
        }

        create_user(**payload)
        response = api_client.post(TOKEN_URL, payload)

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_create_token_invalid_credentials(self, create_user, api_client) -> None:
        """Test that token is not created beacuse of invalid credentials"""
        create_user(email="ruslaneleusinov@gmail.com", password="passw")

        response = api_client.post(
            TOKEN_URL, {"email": "ruslaneleusinov@gmail.com", "password": "passW"}
        )

        assert "token" not in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_token_no_user(self, api_client) -> None:
        """Test that token is not created if user does not exist"""
        payload = {
            "email": "ruslaneleusinov@gmail.com",
            "password": "passw",
            "name": "rus",
        }

        response = api_client.post(TOKEN_URL, payload)

        assert "token" not in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_token_missing_field(self, api_client) -> None:
        """Test that email and password are required"""
        response = api_client.post(TOKEN_URL, {"email": "email", "password": ""})

        assert "token" not in response.data
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_user_unathorized(self, api_client) -> None:
        """Test that authentication is required for users"""
        response = api_client.get(ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class PrivateUserAPITests:
    """Test the API requests that require authentication"""

    def test_retrieve_profile_successful(self, api_client, simple_user):
        """Test retrieving the profile for logged in user"""
        response = api_client.get(ME_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"email": simple_user.email, "name": simple_user.name}

    def test_post_me_not_allowed(self, api_client, simple_user):
        """Test that POST method is not allowed on me url"""
        response = api_client.post(ME_URL, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_profile(self, api_client, simple_user):
        """Test updating the user profile for authenticated user"""
        payload = {"name": "new name", "password": "otherpass"}
        response = api_client.patch(ME_URL, payload)

        simple_user.refresh_from_db()

        assert simple_user.name == payload["name"]
        assert simple_user.check_password(payload["password"])
        assert response.status_code == status.HTTP_200_OK
