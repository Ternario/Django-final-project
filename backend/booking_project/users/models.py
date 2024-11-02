from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from booking_project.users.user_manager import CustomUserManager


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(_("username"), max_length=150, unique=True,
                                help_text=_(
                                    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                                ),
                                validators=[username_validator],
                                error_messages={
                                    "unique": _("A user with that username already exists."),
                                },
                                blank=True
                                )
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Birthday")
    phone = models.CharField(max_length=75, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_owner = models.BooleanField(default=False, verbose_name="owner")

    # last_login = models.DateTimeField(null=True, blank=True)
    # email_is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
