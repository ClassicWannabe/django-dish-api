from django.urls import reverse
from django.test import Client


def test_users_listed(admin_client: Client) -> None:
    """Test that users are listed on users page"""
    url = reverse("admin:core_customuser_changelist")
    response = admin_client.get(url)

    assert response.status_code == 200


def test_user_change_page(django_user_model, admin_client: Client) -> None:
    """Test that the user edit page works"""
    user = django_user_model.objects.create_user(
        name="Ruslan", email="email@mail.com", password="123"
    )
    url = reverse("admin:core_customuser_change", args=[user.id])
    response = admin_client.get(url)

    assert response.status_code == 200


def test_create_user_page(admin_client: Client) -> None:
    """Test that create user page works"""
    url = reverse("admin:core_customuser_add")
    response = admin_client.get(url)

    assert response.status_code == 200
