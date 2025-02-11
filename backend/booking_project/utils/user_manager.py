from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_moderator", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                _("Superuser must have is_staff=True.")
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                _("Superuser must have is_superuser=True.")
            )
        if extra_fields.get("is_admin") is not True:
            raise ValueError(
                _("Superuser must have is_admin=True.")
            )
        if extra_fields.get("is_moderator") is not True:
            raise ValueError(
                _("Superuser must have is_moderator=True.")
            )

        return self.create_user(
            email,
            password,
            first_name,
            last_name,
            **extra_fields
        )

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set."))
        if not password:
            raise ValueError(_("The Password must be set."))
        if not first_name:
            raise ValueError(_("The First Name must be set."))
        if not last_name:
            raise ValueError(_("The Last Name must be set."))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def get_by_natural_key(self, email):
        return self.get(**{self.model.USERNAME_FIELD: email})
