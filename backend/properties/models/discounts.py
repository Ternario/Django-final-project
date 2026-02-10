from __future__ import annotations

from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from properties.managers.discount import CustomDiscountManager

from properties.utils.choices.discount import DiscountValueType, DiscountType, DiscountStatus, DiscountUserStatus
from properties.utils.currency import get_default_currency
from properties.utils.error_messages.discounts import DISCOUNT_ERRORS
from properties.utils.user_token_generation import make_user_token


class Discount(models.Model):
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='discounts',
                                   verbose_name=_('Discount'))
    created_by_token = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=_('Created by token'))
    is_admin_created = models.BooleanField(default=False, verbose_name=_('Is admin created'))
    landlord_profile = models.ForeignKey('LandlordProfile', on_delete=models.PROTECT, blank=True, null=True,
                                         related_name='discount_landlords', verbose_name=_('Landlord profile'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(2000)],
                                   verbose_name=_('Description'))
    type = models.CharField(max_length=20, choices=DiscountType.choices(), verbose_name=_('Discount type'))
    value_type = models.CharField(max_length=20, choices=DiscountValueType.choices(),
                                  default=DiscountValueType.PERCENTAGE.value[0], verbose_name=_('Discount type'))
    currency = models.ForeignKey('Currency', on_delete=models.PROTECT, blank=True, related_name='discounts',
                                 verbose_name=_('Default currency'))
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=False,
                                validators=[MinValueValidator(Decimal('0.01'))], verbose_name=_('Value'))
    priority = models.PositiveIntegerField(blank=True, validators=[MaxValueValidator(100)], verbose_name=_('Priority'))

    valid_from = models.DateTimeField(blank=True, null=True, verbose_name=_('Valid from'))
    valid_until = models.DateTimeField(blank=True, null=True, verbose_name=_('Valid until'))

    compatible = models.BooleanField(default=True, verbose_name=_('Compatible'))
    incompatible_with = models.ManyToManyField('self', blank=True, symmetrical=False,
                                               related_name='incompatible_discounts',
                                               verbose_name=_('Incompatible with'))

    status = models.CharField(max_length=20, choices=DiscountStatus.choices(), default=DiscountStatus.DRAFT.value[0],
                              verbose_name=_('Status'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomDiscountManager()

    def __str__(self) -> str:
        is_percent: str = (
            '%' if self.value_type == DiscountValueType.PERCENTAGE.value[0]
            else (
                self.currency.symbol if self.currency.symbol else self.currency.code
            )
        )
        return f'Name: {self.name}, type: {self.type}, value: {self.value}{is_percent}.'

    class Meta:
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')

    def clean(self) -> None:
        super().clean()

        non_field_errors: List[str] = []

        if self.type == DiscountType.SEASONAL.value[0]:
            if not self.valid_from or not self.valid_until:
                non_field_errors.append(DISCOUNT_ERRORS['seasonal'])
        else:
            if bool(self.valid_from) ^ bool(self.valid_until):
                non_field_errors.append(DISCOUNT_ERRORS['both_fields'])

        if self.status == DiscountStatus.SCHEDULED.value[0]:
            if not self.valid_from or not self.valid_until:
                non_field_errors.append(DISCOUNT_ERRORS['scheduled'])
        else:
            if bool(self.valid_from) ^ bool(self.valid_until):
                non_field_errors.append(DISCOUNT_ERRORS['both_fields'])

        if self.valid_from and self.valid_from < now():
            non_field_errors.append(DISCOUNT_ERRORS['past_valid_from'])

        if self.valid_until and self.valid_from:
            if self.valid_until <= self.valid_from:
                non_field_errors.append(DISCOUNT_ERRORS['short_duration'])

        if self.value_type == DiscountValueType.FIXED.value[0] and not self.currency_id:
            non_field_errors.append(DISCOUNT_ERRORS['currency'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if not self.currency and self.value_type == DiscountValueType.FIXED.value[0]:
            self.currency = get_default_currency()

        if not self.priority:
            if self.type == DiscountType.CUSTOM.value[0]:
                self.priority = 10
            elif self.type == DiscountType.REFERRAL.value[0]:
                self.priority = 20
            elif self.type == DiscountType.COUPON.value[0]:
                self.priority = 30
            else:
                self.priority = 40
        super().save(*args, **kwargs)

    def set_disabled(self) -> None:
        if self.status == DiscountStatus.DISABLED.value[0]:
            return

        self.status = DiscountStatus.DISABLED.value[0]
        self.save(update_fields=['status', 'updated_at'])

    def set_active(self) -> None:
        if self.status == DiscountStatus.ACTIVE.value[0]:
            return

        self.status = DiscountStatus.ACTIVE.value[0]
        self.save(update_fields=['status', 'updated_at'])

    def privacy_delete(self) -> None:
        if not self.created_by:
            return

        self.created_by_token = make_user_token(self.created_by_id)
        self.created_by = None
        self.status = DiscountStatus.DISABLED.value[0]

        self.save(update_fields=['created_by_token', 'created_by', 'status', 'updated_at'])


class DiscountProperty(models.Model):
    discount = models.ForeignKey('Discount', on_delete=models.PROTECT, related_name='discount_properties',
                                 verbose_name=_('Discount'))
    property = models.ForeignKey('Property', on_delete=models.PROTECT, related_name='property_discounts',
                                 verbose_name=_('Property'))
    landlord_profile = models.ForeignKey('LandlordProfile', on_delete=models.PROTECT,
                                         related_name='discount_property_landlords', verbose_name=_('Landlord profile'))
    added_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='added_discount_properties',
                                 verbose_name=_('Added by'))

    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    removed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Removed at'))
    removed_by = models.ForeignKey('User', null=True, blank=True, related_name='removed_discount_properties',
                                   on_delete=models.SET_NULL, verbose_name=_('Removed by'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    class Meta:
        verbose_name = _('Discount Property')
        verbose_name_plural = _('Discount Properties')
        unique_together = ('discount', 'property', 'landlord_profile')

    def __str__(self) -> str:
        return f'Discount {self.discount_id} -> Property {self.property_id}'

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if self.removed_by and not self.removed_at:
            self.removed_at = now()

        super().save(*args, **kwargs)

    def set_deactivated(self, user: User) -> None:
        if not self.is_active:
            return

        self.is_active = False
        self.removed_at = now()
        self.removed_by = user

        self.save(update_fields=['is_active', 'removed_at', 'removed_by', 'updated_at'])

    def set_active(self) -> None:
        if self.is_active:
            return

        self.is_active = True
        self.removed_at = None
        self.removed_by = None

        self.save(update_fields=['is_active', 'removed_at', 'removed_by', 'updated_at'])


class DiscountUser(models.Model):
    discount = models.ForeignKey('Discount', on_delete=models.PROTECT, related_name='discount_users',
                                 verbose_name=_('Discount'))
    user = models.ForeignKey('User', blank=True, null=True, on_delete=models.SET_NULL, related_name='user_discounts',
                             verbose_name=_('User'))
    assigned_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True,
                                    related_name='assigned_discount_users', verbose_name=_('Assigned by'))
    landlord_profile = models.ForeignKey('LandlordProfile', on_delete=models.PROTECT,
                                         related_name='discount_user_landlords', verbose_name=_('Landlord profile'))

    code = models.CharField(max_length=32, blank=True, null=True, db_index=True, verbose_name=_('Code'))

    token = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True, verbose_name=_('Token'))
    status = models.CharField(max_length=20, choices=DiscountUserStatus.choices(),
                              default=DiscountUserStatus.SCHEDULED.value[0], verbose_name=_('Status'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Expires at'))

    removed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Removed at'))
    removed_by = models.ForeignKey('User', null=True, blank=True, related_name='removed_discount_users',
                                   on_delete=models.SET_NULL, verbose_name=_('Removed by'))
    remove_reason = models.CharField(blank=True, max_length=2000, validators=[MinLengthValidator(40)],
                                     verbose_name=_('Remove reason'))
    used_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Used at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    objects = models.Manager()

    class Meta:
        verbose_name = _('Discount User')
        verbose_name_plural = _('Discount Users')
        unique_together = (('discount', 'user'), ('discount', 'code'))

    def __str__(self) -> str:
        return f'Discount {self.discount_id} for User {self.user_id} ({self.status})'

    def set_used(self) -> None:
        if self.status == DiscountUserStatus.USED.value[0]:
            return

        self.status = DiscountUserStatus.USED.value[0]
        self.used_at = now()

        self.save(update_fields=['status', 'used_at'])

    def set_expired(self) -> None:
        if self.status == DiscountUserStatus.EXPIRED.value[0]:
            return

        self.status = DiscountUserStatus.EXPIRED.value[0]
        self.save(update_fields=['fields'])
