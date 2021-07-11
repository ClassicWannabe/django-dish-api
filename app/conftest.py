import pytest

from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def create_user(django_user_model):
    return django_user_model.objects.create_user
