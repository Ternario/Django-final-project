from __future__ import annotations
from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from properties.models import User, Property, Location, LandlordProfile

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.error_messages.booking import BOOKING_ERRORS
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.user_token_generation import make_user_token
from properties.utils.choices.time import CheckInTime, CheckOutTime
from properties.utils.choices.payment import PaymentStatus
from properties.utils.choices.booking import BookingStatus
from properties.managers.booking import CustomManager


class Booking(models.Model):
    booking_number = models.CharField(max_length=20, unique=True, verbose_name=_('Booking number'))
    property_ref = models.ForeignKey('Property', on_delete=models.PROTECT, related_name='bookings',
                                     verbose_name=_('Property'))

    guest = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, db_index=True, related_name='bookings',
                              verbose_name=_('Guest'))

    guest_token = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=_('Guest token'))
    guests_number = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)],
                                                verbose_name=_('Guests number'))
    additional_requests = models.TextField(blank=True, null=True, verbose_name=_('Additional requests'))

    guest_visible = models.BooleanField(default=True, verbose_name=_('Guest visible'))
    property_owner_visible = models.BooleanField(default=True, verbose_name=_('Property owner visible'))

    check_in_date = models.DateField( verbose_name=_('Check in date'))
    check_out_date = models.DateField(verbose_name=_('Check out date'))
    check_in_time = models.TimeField(choices=CheckInTime.choices(), default=CheckInTime.default(),
                                     blank=True, verbose_name=_('Check in Time'))
    check_out_time = models.TimeField(choices=CheckOutTime.choices(), default=CheckOutTime.default(),
                                      blank=True, verbose_name=_('Check out Time'))

    status = models.CharField(max_length=20, choices=BookingStatus.choices(), default=BookingStatus.PENDING.value[0],
                              verbose_name=_('Status'))

    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, related_name='bookings',
                                 verbose_name=_('Currency'))
    currency_rate_to_base = models.DecimalField(max_digits=10, decimal_places=6,
                                                verbose_name=_('Currency rate to base'))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('10.00'))],
                                     verbose_name=_('Base price'))
    taxes_fees = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                     validators=[MinValueValidator(Decimal('0.00'))], verbose_name=_('Taxes fees'))
    applied_discounts = models.JSONField(blank=True, null=True, verbose_name=_('Applied discounts'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total price'))

    payment_type = models.ForeignKey('PaymentType', on_delete=models.SET_NULL, null=True, related_name='bookings',
                                     verbose_name=_('Payment type'))
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True, related_name='bookings',
                                       verbose_name=_('Payment type'))
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices(),
                                      default=PaymentStatus.PENDING.value[0], verbose_name=_('Payment status'))

    transaction_id = models.CharField(max_length=36, null=True, blank=True, verbose_name=_('Transaction ID'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    cancellation_policy = models.ForeignKey('CancellationPolicy', on_delete=models.SET_NULL, null=True,
                                            related_name='bookings', verbose_name=_('Cancellation policy'))
    cancelled_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='cancelled_bookings', verbose_name=_('Cancelled by'))
    cancelled_by_token = models.CharField(max_length=64, blank=True, db_index=True,
                                          verbose_name=_('Cancelled by token'))
    cancellation_reason = models.TextField(blank=True, validators=[MinLengthValidator(30), MaxLengthValidator(2000)],
                                           verbose_name=_('Cancellation reason'))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Cancelled at'))

    snapshot_data = models.JSONField(blank=True, null=True, verbose_name=_('Snapshot data'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomManager()

    def __str__(self) -> str:
        return (
            f'To property: {self.property_ref}, id: {self.pk}, '
            f'Check in - out date: {self.check_in_date} - {self.check_out_date}.'
        )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')

    def clean(self) -> None:
        super().clean()

        errors: Dict[str, str | List[str]] = {}

        if not self.guest_id:
            errors['guest'] = NOT_NULL_FIELD

        if not self.property_ref_id:
            errors['property_ref'] = NOT_NULL_FIELD

        if not self.check_in_date:
            errors['check_in_date'] = NOT_NULL_FIELD

        if not self.check_out_date:
            errors['check_out_date'] = NOT_NULL_FIELD

        if self.cancelled_by:
            reason: List[str] = []

            if not self.cancellation_reason:
                reason.append(BOOKING_ERRORS['empty'])
            if len(self.cancellation_reason.strip()) < 30:
                reason.append(BOOKING_ERRORS['length'])

            if reason:
                errors['cancellation_reason'] = reason

        if errors:
            raise ValidationError(errors)

        non_field_errors: List[str] = []

        property_data: Property = self.property_ref

        if property_data.owner.type == LandlordType.INDIVIDUAL.value[0]:
            ownership_profile: User = property_data.owner.created_by

            if self.guest == ownership_profile:
                non_field_errors.append(BOOKING_ERRORS['ownership'].format(property=property_data.property_type))

        if self.check_in_date < now().date():
            non_field_errors.append(BOOKING_ERRORS['check_in_past'])

        if self.check_out_date <= self.check_in_date:
            non_field_errors.append(BOOKING_ERRORS['short_duration'])

        if Booking.objects.active(
                property_ref=self.property_ref,
                check_in_date__lt=self.check_out_date,
                check_out_date__gt=self.check_in_date
        ).exclude(id=self.pk).exists():
            non_field_errors.append(BOOKING_ERRORS['overlaps_dates'].format(property=property_data.property_type))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        self.currency_rate_to_base = self.currency.rate_to_base

        if self.status == BookingStatus.CANCELLED.value[0] or self.status == BookingStatus.COMPLETED.value[0]:
            self._snapshot_data()
            self.is_active = False
            if not self.cancelled_at:
                self.cancelled_at = now()
        super().save(*args, **kwargs)

    def _snapshot_data(self) -> None:
        property_data: Property = self.property_ref
        ownership_profile: LandlordProfile = property_data.owner
        guest: User = self.guest
        property_location: Location = property_data.location
        region: str | None = property_location.region

        if region:
            region = f'Region: {region}, '

        property_address: str = (
            f'Country: {property_location.country}, '
            f'{region}'
            f'City: {property_location.city}, '
            f'Street address: {property_location.street} {property_location.house_number}'
        )

        guest_full_name: str = f'{guest.first_name} {guest.last_name}'

        self.snapshot_data = {
            'property_title': property_data.title,
            'property_address': property_address,
            'property_owner_name': ownership_profile.name,
            'property_owner_email': ownership_profile.email,
            'property_owner_type': ownership_profile.type,
            'guest': guest.pk,
            'guest_token': None,
            'guest_full_name': guest_full_name,
            'guest_email': guest.email,
            'guest_phone': guest.phone,
            'currency_id': self.currency.pk,
            'currency_code': self.currency.code,
            'currency_name': self.currency.name,
            'payment_method_id': self.payment_method.pk,
            'payment_method_name': self.payment_method.name,
            'payment_type_id': self.payment_type.pk,
            'payment_type_name': self.payment_type.name,
            'cancellation_policy': self.cancellation_policy.pk if self.cancellation_policy else None,
            'cancelled_by': self.cancelled_by.pk if self.cancelled_by else None,
            'cancelled_by_token': None,
            'cancellation_reason': self.cancellation_reason if self.cancellation_reason else None
        }

    def privacy_delete(self) -> None:
        if not self.guest:
            return

        self.guest_token = make_user_token(self.guest.pk)

        snapshot_data: Dict[str, Any] = self.snapshot_data if self.snapshot_data else {}

        snapshot_data['guest'] = None
        snapshot_data['guest_token'] = self.guest_token
        snapshot_data['guest_full_name'] = None
        snapshot_data['guest_email'] = None
        snapshot_data['guest_phone'] = None
        snapshot_data['updated_at'] = now()

        if self.cancelled_by and self.guest == self.cancelled_by:
            self.cancelled_by_token = make_user_token(self.cancelled_by.pk)
            self.cancelled_by = None

            snapshot_data['cancelled_by'] = None
            snapshot_data['cancelled_by_token'] = self.cancelled_by_token

        self.snapshot_data = snapshot_data
        self.guest = None

        self.save(
            update_fields=['guest_token', 'guest', 'cancelled_by_token', 'cancelled_by', 'snapshot_data', 'updated_at']
        )

    def cancelled_by_privacy_delete(self) -> None:
        if not self.cancelled_by:
            return

        snapshot_data: Dict[str, Any] = self.snapshot_data

        self.cancelled_by_token = make_user_token(self.cancelled_by)

        snapshot_data['cancelled_by_token'] = self.cancelled_by_token
        snapshot_data['cancelled_by'] = None

        self.snapshot_data = snapshot_data
        self.cancelled_by = None

        self.save(update_fields=['cancelled_by_token', 'cancelled_by', 'snapshot_data', 'updated_at'])

    def property_owner_privacy_delete(self) -> None:
        snapshot_data: Dict[str, Any] = self.snapshot_data

        snapshot_data['property_owner_name'] = None
        snapshot_data['property_owner_email'] = None

        self.snapshot_data = snapshot_data

        self.save(update_fields=['snapshot_data', 'updated_at'])
