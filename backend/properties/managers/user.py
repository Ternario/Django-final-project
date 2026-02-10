from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict

from properties.utils.decorators import atomic_handel

if TYPE_CHECKING:
    from properties.models import User

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from properties.models.user_profile import UserProfile


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model that provides utility methods
    for creating users and superusers with validation,
    and filtering users based on soft deletion status.

    Supports:
        - Creating superusers with required flags (is_staff, is_superuser, is_admin, is_moderator).
        - Creating regular users with validation for required fields.
        - Retrieving users by natural key (email).
        - Filtering users that are not soft-deleted.

    Methods:
        create_superuser(email, password, first_name, last_name, **extra_fields) -> User
            Creates a superuser with automatic validation of required flags.
        create_user(email, password, first_name, last_name, **extra_fields) -> User
            Creates a regular user with required fields validation.
        get_by_natural_key(email) -> User
            Retrieves a user instance by their natural key (email).
        not_deleted() -> QuerySet[User]
            Returns a queryset of users that are not soft-deleted.
    """

    def create_superuser(self, email: str, password: str, first_name: str, last_name: str, **extra_fields: Any) -> User:
        """
        Create a superuser with required flags.

        Automatically sets:
            - is_staff=True
            - is_superuser=True
            - is_admin=True
            - is_moderator=True

        Validates that all required flags are True.

        Args:
            email (str): Email of the superuser.
            password (str): Password for the superuser.
            first_name (str): First name of the superuser.
            last_name (str): Last name of the superuser.
            **extra_fields: Additional fields to pass to the user model.

        Returns:
            User: The created superuser instance.

        Raises:
            ValidationError: If any required flag is missing or False.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_moderator', True)

        errors: Dict[str, str] = {}

        if not extra_fields.get('is_staff'):
            errors['is_staff'] = _('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            errors['is_superuser'] = _('Superuser must have is_superuser=True.')
        if not extra_fields.get('is_admin'):
            errors['is_admin'] = _('Superuser must have is_admin=True.')
        if not extra_fields.get('is_moderator'):
            errors['is_moderator'] = _('Superuser must have is_moderator=True.')

        if errors:
            raise ValidationError(errors)

        return self.create_user(
            email,
            password,
            first_name,
            last_name,
            **extra_fields
        )

    @atomic_handel
    def create_user(self, email: str, password: str, first_name: str, last_name: str, **extra_fields: Any) -> User:
        """
        Create a regular user with validation of required fields.

        Validates that `email`, `password`, `first_name`, and `last_name` are provided.

        Args:
            email (str): Email of the user.
            password (str): Password for the user.
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            **extra_fields: Additional fields to pass to the user model.

        Returns:
            User: The created user instance.

        Raises:
            ValidationError: If any required field is missing.
        """
        errors: Dict[str, str] = {}

        if not email:
            errors['email'] = _('The Email must be set.')
        if not password:
            errors['password'] = _('The Password must be set.')
        if not first_name:
            errors['first_name'] = _('The First Name must be set.')
        if not last_name:
            errors['last_name'] = _('The Last Name must be set.')

        if errors:
            raise ValidationError(errors)

        normalized_email: str = self.normalize_email(email)
        user: User = self.model(
            email=normalized_email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user)

        return user

    def get_by_natural_key(self, email: str) -> User:
        """
        Retrieve a user instance by its natural key (email).

        Args:
            email (str): Email of the user.

        Returns:
            User: The user instance matching the provided email.
        """
        return self.get(**{self.model.USERNAME_FIELD: email})

    def not_deleted(self) -> QuerySet[User]:
        """
        Retrieve all users that are not soft-deleted.

        Returns:
            QuerySet[User]: QuerySet containing users where `is_deleted=False`.
        """
        return self.filter(is_deleted=False)
