from __future__ import annotations

import decimal
from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from properties.models import Property, Discount, CancellationPolicy
    from datetime import date
    from decimal import Decimal

from datetime import timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from django.utils.timezone import now
from rest_framework.serializers import (
    ModelSerializer, CharField, DateTimeField, ValidationError, SerializerMethodField, ListField, IntegerField
)

from properties.models import Booking, User

from properties.serializers.currency import CurrencyBaseSerializer
from properties.serializers.user import UserBasePublicSerializer
from properties.serializers.discounts import AppliedDiscountSerializer
from properties.utils.choices.booking import BookingStatus, CancellationPolicy as Policy
from properties.utils.error_messages.booking import BOOKING_ERRORS
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.choices.discount import DiscountValueType
from properties.utils.currency import format_price


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
                  'base_price', 'taxes_fees', 'total_price', 'applied_discounts']
        read_only_fields = ['guest', 'property_ref']

    def create(self, validated_data: Dict[str, Any]) -> Booking:
        guest: User = self.context['guest']
        property_ref: Property = self.context['property_ref']

        validated_data['guest'] = guest
        validated_data['property_ref'] = property_ref

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        property_ref: Property = self.context['property_ref']
        check_in_date: date = attrs.get('check_in_date')
        check_out_date: date = attrs.get('check_out_date')
        base_price: Decimal = attrs.get('base_price')
        taxes_fees: Decimal = attrs.get('taxes_fees')
        total_price: Decimal = attrs.get('total_price')
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

        sub_total_price: Decimal = (base_price + taxes_fees).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        total_price: Decimal = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if discounts:
            discount_list: List[Discount] = Discount.objects.active(pk__in=discounts)
            discounts_value: Decimal = Decimal('0.00')

            for discount in discount_list:
                if discount.value_type == DiscountValueType.PERCENTAGE.value[0]:
                    discounts_value += sub_total_price * Decimal(discount.value) / Decimal('100')
                else:
                    discounts_value += Decimal(discount.value)

            new_price: Decimal = (sub_total_price - discounts_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if total_price != new_price:
                non_field_errors.append(BOOKING_ERRORS['wrong_total_price'])

            if non_field_errors:
                raise ValidationError({'non_field_errors': non_field_errors})

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

        else:
            if total_price != sub_total_price:
                non_field_errors.append(BOOKING_ERRORS['wrong_total_price'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class BookingBaseSerializer(ModelSerializer):
    property_name = CharField(source='property_ref.title', read_only=True)
    check_in_time_display = CharField(source='get_check_in_time_display', read_only=True)
    check_out_time_display = CharField(source='get_check_out_time_display', read_only=True)
    status_display = CharField(source='get_status_display', read_only=True)
    payment_status_display = CharField(source='get_payment_status_display', read_only=True)
    currency = CurrencyBaseSerializer(read_only=True)
    cancelled_at_display = DateTimeField(source='cancelled_at', format='%d-%m-%Y %H:%M', read_only=True)
    created_at_display = DateTimeField(source='created_at', format='%d-%m-%Y %H:%M', read_only=True)
    total_price_display = SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'property_ref', 'property_name', 'check_in_date', 'check_in_time',
                  'check_out_date', 'check_out_time', 'status', 'status_display', 'total_price_display',
                  'currency', 'payment_status', 'payment_status_display', 'cancelled_at', 'created_at_display',
                  'created_at']

    def get_total_price_display(self, obj: Booking) -> decimal:
        return format_price(obj.total_price, obj.currency_rate_to_base)


class BookingGuestSerializer(ModelSerializer):
    property_name = CharField(source='property_ref.title', read_only=True)
    check_in_time_display = CharField(source='get_check_in_time_display', read_only=True)
    check_out_time_display = CharField(source='get_check_out_time_display', read_only=True)
    status_display = CharField(source='get_status_display', read_only=True)
    currency = CurrencyBaseSerializer(read_only=True)
    payment_type_display = CharField(source='payment_type.name')
    payment_method_display = CharField(source='payment_method.name')
    payment_status_display = CharField(source='get_payment_status_display', read_only=True)
    cancelled_at_display = DateTimeField(source='cancelled_at', format='%d-%m-%Y %H:%M', read_only=True)
    created_at_display = DateTimeField(source='created_at', format='%d-%m-%Y %H:%M', read_only=True)
    total_price = SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'booking_number', 'property_ref', 'property_name', 'guests_number', 'additional_requests',
                  'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time', 'status', 'status_display',
                  'currency', 'total_price_display', 'payment_type_display', 'payment_method_display',
                  'payment_status_display', 'is_active', 'cancellation_reason', 'cancelled_at', 'created_at_display',
                  'created_at']

    def get_total_price(self, obj: Booking) -> decimal:
        return format_price(obj.total_price, obj.currency_rate_to_base)


class BookingOwnerSerializer(BookingGuestSerializer):
    guest = UserBasePublicSerializer(read_only=True)
    discounts = AppliedDiscountSerializer(source='applied_discounts', many=True, read_only=True)
    base_price = SerializerMethodField()
    taxes_fees = SerializerMethodField()

    class Meta(BookingGuestSerializer.Meta):
        model = BookingGuestSerializer.Meta.model
        fields = BookingGuestSerializer.Meta.fields + ['guest', 'base_price', 'taxes_fees', 'discounts']

    def get_base_price(self, obj: Booking) -> decimal:
        return format_price(obj.base_price, obj.currency_rate_to_base)

    def get_taxes_fees(self, obj: Booking) -> decimal:
        return format_price(obj.taxes_fees, obj.currency_rate_to_base)


class BookingCancellationSerializer(ModelSerializer):
    check_in_time_display = CharField(source='get_check_in_time_display', read_only=True)
    check_out_time_display = CharField(source='get_check_out_time_display', read_only=True)
    status_display = CharField(source='get_status_display', read_only=True)
    cancelled_at_display = DateTimeField(source='cancelled_at', format='%d-%m-%Y %H:%M', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'check_in_date', 'check_in_time', 'check_out_date', 'check_out_time', 'status',
                  'status_display', 'cancelled_at', 'cancellation_reason', 'cancelled_at_display']

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
