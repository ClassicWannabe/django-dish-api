from unittest.mock import patch
import pytest

from core.models import CustomUser, Tag, Ingredient, Recipe, recipe_image_file_path

pytestmark = pytest.mark.django_db


def test_create_user_with_email_successful(create_user) -> None:
    """Test creating a new user with email is successful"""
    email = "ruslaneleusinov@gmail.com"
    password = "123456789"
    user = create_user(email=email, password=password)

    assert user.email == email
    assert user.check_password(password)


def test_new_user_email_normalized(create_user) -> None:
    """Test the email for a new user is normalized"""
    email = "ruslaneleusinov@GmAiL.COM"
    user = create_user(email=email, password="123")

    assert user.email == email.lower()


def test_new_user_invalid_email(create_user) -> None:
    """Test the invalid email or empty email should raise an error"""

    with pytest.raises(ValueError):
        create_user(email=None, password="123")


def test_create_superuser(django_user_model: CustomUser) -> None:
    """Test creating a new superuser"""
    user = django_user_model.objects.create_superuser(
        email="rus@mail.com", password="123"
    )
    assert user.is_superuser
    assert user.is_staff


def test_tag_str(simple_user) -> None:
    """Test the tag string representation"""
    tag = Tag.objects.create(user=simple_user, name="Vegan")

    assert str(tag) == tag.name


def test_ingredient_str(simple_user) -> None:
    """Test the ingredient string representation"""
    ingredient = Ingredient.objects.create(user=simple_user, name="Tomato")

    assert str(ingredient) == ingredient.name


def test_recipe_str(simple_user) -> None:
    """Test the recipe string representation"""
    recipe = Recipe.objects.create(
        user=simple_user, title="Lasagna", time_min=20, price=49.99
    )

    assert str(recipe) == recipe.title


@patch("uuid.uuid4")
def test_recipe_file_name_uuid(mock_uuid) -> None:
    """Test that image is saved in the correct location"""
    uuid = "test-uuid"
    mock_uuid.return_value = uuid
    file_path = recipe_image_file_path(None, "myimage.jpeg")
    exp_path = f"uploads/recipe/{uuid}.jpeg"

    assert file_path == exp_path
