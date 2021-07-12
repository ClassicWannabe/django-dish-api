from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUserManager(UserManager):
    def create_user(
        self, email: str, password: str = None, **extra_fields
    ) -> AbstractUser:
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The email must be specified")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None) -> AbstractUser:
        """Create and save a new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    """Custom user model using email instead of username"""

    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("name"), max_length=255, blank=True)
    username = None
    first_name = None
    last_name = None

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Tag(models.Model):
    """Tag to be used for recipe"""

    name = models.CharField(_("tag name"), max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
