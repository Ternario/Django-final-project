from datetime import date
from typing import Dict, List

from django.core.exceptions import ValidationError
from django.template.defaulttags import now
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

from properties.managers.user import CustomUserManager

from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.constants.age import AGE
from properties.utils.currency import get_default_currency
from properties.utils.language import get_default_language
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.regex_patterns import match_user_name


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=35, unique=True, blank=True, null=True, verbose_name=_('Username'))
    email = models.EmailField(max_length=155, unique=True, verbose_name=_('Email'))
    first_name = models.CharField(max_length=155, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=155, verbose_name=_('Last Name'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Birthday'))
    language = models.ForeignKey('Language', on_delete=models.PROTECT, blank=True, verbose_name=_('Language'))
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, blank=True, verbose_name=_('Currency'))
    is_landlord = models.BooleanField(default=False, verbose_name=_('Landlord'))
    landlord_type = models.CharField(max_length=50, blank=True, choices=LandlordType.choices(),
                                     default=LandlordType.NONE.value[0], verbose_name=_('Landlord type'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Access to the admin panel'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Superuser'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Admin'))
    is_moderator = models.BooleanField(default=False, verbose_name=_('Moderator'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    last_login = models.DateTimeField(blank=True, null=True, verbose_name=_('Last login'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f'User: {self.email}'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def clean(self) -> None:
        super().clean()

        errors: Dict[str, str] = {}

        if not self.first_name:
            errors['first_name'] = NOT_NULL_FIELD

        if not self.last_name:
            errors['last_name'] = NOT_NULL_FIELD

        if errors:
            raise ValidationError(errors)

        non_field_errors: List[str] = []

        if not match_user_name(self.first_name):
            non_field_errors.append(USER_ERRORS['first_name'])

        if not match_user_name(self.last_name):
            non_field_errors.append(USER_ERRORS['last_name'])

        if self.date_of_birth:
            today: date = date.today()
            age: int = today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            if age < AGE:
                non_field_errors.append(USER_ERRORS['date_of_birth'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

    def save(self, *args, **kwargs) -> None:
        if not self.language_id:
            self.language = get_default_language()

        if not self.currency_id:
            self.currency = get_default_currency()

        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def restore(self) -> None:
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])

    def privacy_delete(self) -> None:
        self.username = f'deleted_{self.pk}'
        self.email = f'deleted_{self.pk}@example.com'
        self.first_name = ''
        self.last_name = ''
        self.date_of_birth = None
        self.language = None
        self.currency = None
        self.password = ''
        self.is_staff = False
        self.is_superuser = False
        self.is_admin = False
        self.is_moderator = False
        self.is_landlord = False
        self.is_verified = False
        self.is_deleted = True
        self.password = ''
        self.deleted_at = now()
        self.save()
