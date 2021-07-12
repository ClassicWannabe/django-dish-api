import pytest

from core.models import CustomUser, Tag

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


def test_tag_str(simple_user):
    """Test the tag string represention"""
    tag = Tag.objects.create(user=simple_user, name="Vegan")

    assert str(tag) == tag.name
