import pytest

from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def create_user(django_user_model):
    return django_user_model.objects.create_user


@pytest.fixture
def simple_user(create_user, api_client):
    user = create_user(
        email="ruslaneleusinov@gmail.com", password="mypass", name="ruslan"
    )
    api_client.force_authenticate(user=user)
    yield user
