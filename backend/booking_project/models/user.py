from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from booking_project.utils.user_manager import CustomUserManager


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(_("username"), max_length=150, unique=True,
                                help_text=_(
                                    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                                ),
                                validators=[UnicodeUsernameValidator()],
                                error_messages={
                                    "unique": _("A user with that username already exists."),
                                },
                                null=True,
                                blank=True
                                )
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True, error_messages={
        "unique": _("A user with that username already exists."), })
    first_name = models.CharField(_("first name"), max_length=150, null=False, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, null=False, blank=False)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Birthday")
    phone = models.CharField(max_length=75, null=True, blank=True)

    is_admin = models.BooleanField(default=False, verbose_name="Admin")
    is_moderator = models.BooleanField(default=False, verbose_name="Moderator")
    is_landlord = models.BooleanField(default=False, verbose_name="Is landlord")
    is_verified = models.BooleanField(default=False, verbose_name="Is verified")
    is_deleted = models.BooleanField(default=False, verbose_name="Is deleted")

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="registered")
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
    ]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
