from __future__ import annotations

from typing import Dict, Any, List, TYPE_CHECKING

from properties.utils.regex_patterns import match_phone_number

if TYPE_CHECKING:
    from properties.models import User

import hashlib

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from base_config.settings import HASH_SALT
from properties.managers.landlord_profile import CustomLandlordProfileManager, CustomCompanyMembershipManager

from properties.utils.choices.landlord_profile import CompanyRole, LandlordType
from properties.utils.constants.default_depersonalization_values import DELETED_LANDLORD_PLACEHOLDER
from properties.utils.currency import get_default_currency
from properties.utils.error_messages.landlord_profile import LANDLORD_PROFILE_ERRORS
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.user_token_generation import make_user_token


class LandlordProfile(models.Model):
    hash_id = models.CharField(max_length=64, unique=True, blank=True, verbose_name=_('Hash id'))
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='landlord_profiles',
                                   verbose_name=_('Created by'))
    created_by_token = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=_('Created by token'))
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    phone = models.CharField(max_length=21, unique=True, verbose_name=_('Phone'))
    email = models.EmailField(max_length=155, unique=True, verbose_name=_('Email'))
    type = models.CharField(max_length=20, choices=LandlordType.choices(), verbose_name=_('Type'))
    tax_id = models.CharField(max_length=50, verbose_name=_('Tax id'))
    registration_address = models.CharField(max_length=255, verbose_name=_('Registration address'))
    description = models.TextField(blank=True, validators=[MinLengthValidator(40), MaxLengthValidator(2000)],
                                   verbose_name=_('Description'))

    languages_spoken = models.ManyToManyField('Language', related_name='landlord_profiles',
                                              verbose_name=_('Languages spoken'))
    accepted_currencies = models.ManyToManyField('Currency', blank=True, related_name='accepted_by_landlords',
                                                 verbose_name=_('Accepted currencies'))
    default_currency = models.ForeignKey('Currency', on_delete=models.PROTECT, default=get_default_currency,
                                         blank=True, related_name='default_for_landlords',
                                         verbose_name=_('Default currency'))
    available_payment_methods = models.ManyToManyField('PaymentMethod', related_name='landlord_profiles',
                                                       verbose_name=_('Available payments methods'))

    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))

    is_trusted = models.BooleanField(default=False, verbose_name=_('Trusted'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomLandlordProfileManager()

    def __str__(self) -> str:
        if self.created_by:
            return f'{self.type}: {self.email}, by: {self.created_by}.'
        return f'{self.type}: Anonymous: {self.created_by_token}.'

    class Meta:
        verbose_name = _('Landlord Profile')
        verbose_name_plural = _('Landlord Profiles')

    def clean(self) -> None:
        super().clean()

        if self.is_deleted:
            return

        errors: Dict[str, str] = {}

        if not self.created_by_id:
            errors['created_by'] = NOT_NULL_FIELD

        if not self.phone:
            errors['phone'] = NOT_NULL_FIELD

        if errors:
            raise ValidationError(errors)

        non_field_errors: List[str] = []

        if not match_phone_number(str(self.phone)):
            non_field_errors.append(LANDLORD_PROFILE_ERRORS['phone'])

        if (
                self.type == LandlordType.INDIVIDUAL.value[0]
                and
                self.name != f'{self.created_by.first_name} {self.created_by.last_name}'
        ):
            non_field_errors.append(LANDLORD_PROFILE_ERRORS['name'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if not self.hash_id:
            salt: str = HASH_SALT
            raw_string: str = f'{now()}-{salt}'
            self.hash_id = hashlib.sha256(raw_string.encode()).hexdigest()[:12]

        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def privacy_delete(self) -> None:
        if not self.created_by:
            return

        self.created_by_token = make_user_token(self.created_by.pk)
        self.created_by = None

        if self.type == LandlordType.INDIVIDUAL.value[0]:
            self.name = DELETED_LANDLORD_PLACEHOLDER
            self.email = f'deleted_{self.pk}@example.com'
            self.phone = f'deleted_{self.pk}'
            self.address = ''
            self.description = ''
            self.languages_spoken.clear()
            self.accepted_currencies.clear()
            self.default_currency = None
            self.available_payment_methods.clear()

        self.is_deleted = True
        self.deleted_at = now()

        self.save()


class CompanyMembership(models.Model):
    company = models.ForeignKey('LandlordProfile', on_delete=models.PROTECT, related_name='company_memberships',
                                verbose_name=_('Company'))
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='user_memberships',
                             verbose_name=_('User'))
    user_token = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=_('User token'))
    user_full_name = models.CharField(max_length=155, verbose_name=_('User full name'))

    role = models.CharField(max_length=15, choices=CompanyRole.choices(), default=CompanyRole.ACCOUNTANT.value[0],
                            verbose_name=_('Role'))
    languages_spoken = models.ManyToManyField('Language', related_name='company_membership',
                                              verbose_name=_('Languages spoken'))
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Joined at'))

    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    left_at = models.DateTimeField(verbose_name=_('Joined at'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomCompanyMembershipManager()

    def __str__(self) -> str:
        if self.user:
            return f'User: {self.user}, company: {self.company}.'
        return f'Anonymous {self.user_token}, company: {self.company}.'

    class Meta:
        verbose_name = _('Company Membership')
        verbose_name_plural = _('Company Memberships')
        unique_together = ('company', 'user')

    def clean(self) -> None:
        super().clean()

        if not self.company_id:
            raise ValidationError({'company': NOT_NULL_FIELD})

        if self.company.type == LandlordType.INDIVIDUAL.value[0]:
            raise ValidationError({'non_field_errors': LANDLORD_PROFILE_ERRORS['landlord']})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if not self.user_full_name:
            user: User = self.user

            self.user_full_name = f'{user.first_name} {user.last_name}'

        if self.is_deleted and self.is_active:
            self.is_active = False

        super().save(*args, **kwargs)

    def soft_delete(self) -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = now()
        self.left_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'left_at', 'updated_at'])

    def privacy_delete(self) -> None:
        if not self.user:
            return
        self.user_token = make_user_token(self.user.pk)
        self.user = None
        self.languages_spoken.clear()
        self.is_deleted = True
        self.deleted_at = now()
        if not self.left_at:
            self.left_at = now()
        self.save(update_fields=['user_token', 'user', 'is_deleted', 'deleted_at', 'left_at', 'updated_at'])
