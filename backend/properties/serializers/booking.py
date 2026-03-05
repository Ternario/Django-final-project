from __future__ import annotations
from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from properties.models import Property, CancellationPolicy, Currency, DiscountUser
    from django.db.models import QuerySet
    from datetime import date

from decimal import Decimal
from datetime import timedelta, date
from django.utils.timezone import now
from rest_framework.serializers import (
    ModelSerializer, CharField, DateTimeField, ValidationError, SerializerMethodField, ListField, IntegerField,
)

from properties.models import Booking, User

from properties.serializers.currency import CurrencyBaseSerializer
from properties.serializers.user import UserBasePublicSerializer
from properties.serializers.discounts import AppliedDiscountSerializer

from properties.services.discount.pre_booking_checker import PreBookingChecker

from properties.utils.choices.booking import BookingStatus, CancellationPolicy as Policy
from properties.utils.error_messages.booking import BOOKING_ERRORS
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.choices.discount import DiscountValueType, DiscountUserStatus
from properties.utils.currency import format_price
from properties.utils.decorators import atomic_handel


class BookingCreateSerializer(ModelSerializer):
    applied_discounts = ListField(
        child=IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        write_only=True
    )

    class Meta:
        model = Booking
        fields = ['id', 'guest', 'property_ref', 'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time',
                  'applied_discounts']
        read_only_fields = ['guest', 'property_ref']

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> Booking:
        guest: User = self.context['guest']
        property_ref: Property = self.context['property_ref']

        validated_data['guest'] = guest
        validated_data['property_ref'] = property_ref
        validated_data['total_price'] = property_ref.total_price

        discounts: List[int] = validated_data.pop('discounts', [])

        Property.objects.select_for_update().get(pk=property_ref.pk)

        if discounts:
            du_to_update: QuerySet[DiscountUser] = DiscountUser.objects.select_for_update().filter(
                user_id=guest.pk, discount__in=discounts, status=DiscountUserStatus.ACTIVE.value[0]
            )

            du_to_update.update(
                status=DiscountUserStatus.USED.value[0], used_at=now()
            )

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        property_ref: Property = self.context['property_ref']
        currency: Currency = self.context['currency']
        check_in_date: date = attrs.get('check_in_date')
        check_out_date: date = attrs.get('check_out_date')
        discounts: List[int] = attrs.get('applied_discounts', [])

        non_field_errors: List[str] = []

        if check_in_date < now().date():
            non_field_errors.append(BOOKING_ERRORS['check_in_past'])

        if check_out_date <= check_in_date:
            non_field_errors.append(BOOKING_ERRORS['short_duration'])

        if Booking.objects.active(
                property_ref_id=property_ref.pk,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
        ).exists():
            non_field_errors.append(BOOKING_ERRORS['overlaps_dates'].format(property=property_ref.property_type))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        if discounts:
            discount_list, discounted_price = PreBookingChecker(property_ref, discounts, currency).execute()
            attrs['discounts'] = [d.pk for d in discount_list]
            attrs['applied_discounts'] = [
                {
                    'id': discount.pk,
                    'name': discount.name,
                    'value': discount.value,
                    'type': discount.type,
                    'value_type': discount.value_type,
                    **({
                           'currency': discount.currency,
                           'currency_name': discount.currency.name,
                           'currency_code': discount.currency.code,
                           'currency_symbol': discount.currency.symbol,
                           'rate_to_base': discount.currency.rate_to_base
                       } if discount.value_type == DiscountValueType.FIXED.value[0] else {})

                }
                for discount in discount_list
            ]
            attrs['discounted_price'] = discounted_price
        else:
            attrs['discounted_price'] = property_ref.total_price

        return attrs


class BookingBaseSerializer(ModelSerializer):
    property_name = CharField(source='property_ref.title', read_only=True)
    booking_date = SerializerMethodField(read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    payment_status = CharField(source='get_payment_status_display', read_only=True)
    city = CharField(source='property_ref.location.city', read_only=True)
    currency = CurrencyBaseSerializer(read_only=True)
    discounted_price = SerializerMethodField()
    cancelled_at = DateTimeField(format='%d-%m-%Y %H:%M', read_only=True)
    created_at = DateTimeField(format='%d-%m-%Y %H:%M', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'property_ref', 'property_name', 'booking_date', 'status', 'discounted_price',
                  'currency', 'payment_status', 'city', 'cancelled_at', 'created_at']

    def get_discounted_price(self, obj: Booking) -> Decimal:
        return format_price(obj.discounted_price, obj.currency_rate_to_base)

    def get_booking_date(self, obj: Booking) -> str:
        check_in: date = obj.check_in_date
        check_out: date = obj.check_out_date

        if check_in.year == check_out.year and check_in.month == check_out.month:
            month: str = check_in.strftime('%b')
            return f'{check_in.day} - {check_out.day} {month} {check_in.year}'

        if check_in.year == check_out.year:
            return f'{check_in.day}.{check_in.month} - {check_out.day}.{check_out.month} {check_out.year}'

        check_in_formatted: str = check_in.strftime('%d.%m.%Y')
        check_out_formatted: str = check_out.strftime('%d.%m.%Y')

        return f'{check_in_formatted} - {check_out_formatted}'


class BookingGuestSerializer(ModelSerializer):
    property_name = CharField(source='property_ref.title', read_only=True)
    check_in_time = CharField(source='get_check_in_time_display', read_only=True)
    check_out_time = CharField(source='get_check_out_time_display', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    currency = CurrencyBaseSerializer(read_only=True)
    payment_type = CharField(source='payment_type.name')
    payment_method = CharField(source='payment_method.name')
    payment_status = CharField(source='get_payment_status_display', read_only=True)
    cancelled_at = DateTimeField(format='%d-%m-%Y %H:%M', read_only=True)
    created_at = DateTimeField(format='%d-%m-%Y %H:%M', read_only=True)
    discounted_price = SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'property_ref', 'property_name', 'guests_number', 'additional_requests',
                  'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time', 'status', 'currency',
                  'discounted_price', 'payment_type', 'payment_method', 'payment_status', 'is_active',
                  'cancellation_reason', 'cancelled_at', 'created_at']

    def get_discounted_price(self, obj: Booking) -> Decimal:
        return format_price(obj.discounted_price, obj.currency_rate_to_base)


class BookingOwnerSerializer(BookingGuestSerializer):
    guest = UserBasePublicSerializer(read_only=True)
    discounts = AppliedDiscountSerializer(source='applied_discounts', many=True, read_only=True)
    total_price = SerializerMethodField()

    class Meta(BookingGuestSerializer.Meta):
        model = BookingGuestSerializer.Meta.model
        fields = BookingGuestSerializer.Meta.fields + ['guest', 'total_price', 'discounts']

    def get_total_price(self, obj: Booking) -> Decimal:
        return format_price(obj.total_price, obj.currency_rate_to_base)


class BookingCancellationSerializer(ModelSerializer):
    check_in_time = CharField(source='get_check_in_time_display', read_only=True)
    check_out_time = CharField(source='get_check_out_time_display', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    cancelled_at = DateTimeField(format='%d-%m-%Y %H:%M', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time', 'status', 'cancelled_at',
                  'cancellation_reason']

    def update(self, instance: Booking, validated_data: Dict[str, Any]) -> Booking:
        cancelled_by: User = validated_data.get('cancelled_by')
        cancellation_reason: str = validated_data.get('cancellation_reason')

        instance.status = BookingStatus.CANCELLED.value[0]
        instance.is_active = False
        instance.cancelled_by = cancelled_by
        instance.cancellation_reason = cancellation_reason
        instance.cancelled_at = now()
        instance.save(update_fields=['status', 'is_active', 'cancelled_by', 'cancellation_reason', 'cancelled_at'])

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance: Booking = self.instance

        if instance.status == BookingStatus.CANCELLED.value[0]:
            raise ValidationError({'status': BOOKING_ERRORS['status']})

        cancellation_policy: CancellationPolicy = instance.cancellation_policy
        cancelled_by: User | None = attrs.get('cancelled_by', None)
        reason: str | None = attrs.get('cancellation_reason', None)

        errors: Dict[str, str] = {}

        if not cancelled_by:
            errors['cancelled_by'] = NOT_NULL_FIELD

        if not reason or len(reason.strip()) < 40:
            errors['cancellation_reason'] = BOOKING_ERRORS['cancellation_reason']

        if errors:
            raise ValidationError(errors)

        non_field_errors: List[str] = []

        cancel_date: date = instance.check_in_date - timedelta(days=2)

        if cancellation_policy.name != Policy.FLEXIBLE.value[0] and cancelled_by == instance.guest:
            non_field_errors.append(BOOKING_ERRORS['cancellation_permission'])

        if now().date() >= cancel_date and cancelled_by == instance.guest:
            non_field_errors.append(BOOKING_ERRORS['user_cancellation'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs
