import pytest

from core.models import CustomUser

pytestmark = pytest.mark.django_db


def test_create_user_with_email_successful(django_user_model: CustomUser) -> None:
    """Test creating a new user with email is successful"""
    email = "ruslaneleusinov@gmail.com"
    password = "123456789"
    user = django_user_model.objects.create_user(email=email, password=password)

    assert user.email == email
    assert user.check_password(password)


def test_new_user_email_normalized(django_user_model: CustomUser) -> None:
    """Test the email for a new user is normalized"""
    email = "ruslaneleusinov@GmAiL.COM"
    user = django_user_model.objects.create_user(email=email, password="123")

    assert user.email == email.lower()


def test_new_user_invalid_email(django_user_model: CustomUser) -> None:
    """Test the invalid email or empty email should raise an error"""

    with pytest.raises(ValueError):
        django_user_model.objects.create_user(email=None, password="123")


def test_create_superuser(django_user_model: CustomUser) -> None:
    """Test creating a new superuser"""
    user = django_user_model.objects.create_superuser(
        email="rus@mail.com", password="123"
    )
    assert user.is_superuser
    assert user.is_staff
