from typing import Callable, Iterator

import pytest

from rest_framework.test import APIClient
from core.models import Ingredient, Tag, Recipe


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def sample_tag(user, name="Test tag") -> Tag:
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Test ingredient") -> Ingredient:
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params) -> Recipe:
    """Create and return a sample recipe"""
    defaults = {"time_min": 5, "price": 4.99, "title": "Sample Recipe"}
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


@pytest.fixture
def helper_functions() -> Iterator[Callable]:
    """Helper functions for creating tags, ingredients and recipes"""
    functions = {
        "sample_tag": sample_tag,
        "sample_ingredient": sample_ingredient,
        "sample_recipe": sample_recipe,
    }

    return dotdict(functions)


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
