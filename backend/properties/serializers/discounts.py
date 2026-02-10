from __future__ import annotations

from typing import Any, TYPE_CHECKING, Dict, List

from properties.utils.currency import format_price

if TYPE_CHECKING:
    from properties.models import Currency, Booking, User, Property, LandlordProfile

import hashlib
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.urls import reverse
from django.utils.timezone import now
from rest_framework.exceptions import PermissionDenied

from rest_framework.serializers import (
    Serializer, ModelSerializer, IntegerField, CharField, DateTimeField, BooleanField, ValidationError,
    SerializerMethodField, ListSerializer
)
from properties.models import Discount, DiscountProperty, DiscountUser
from properties.serializers.currency import CurrencyBaseSerializer
from properties.serializers.user import UserBasePublicSerializer, UserBaseSerializer
from properties.serializers.property import PropertyOwnerBaseSerializer
from properties.utils.choices.discount import DiscountValueType, DiscountUserStatus, DiscountType, DiscountStatus
from properties.utils.error_messages.discounts import DISCOUNT_ERRORS
from properties.utils.decorators import atomic_handel
from properties.utils.error_messages.permission import PERMISSION_ERRORS
from properties.utils.serializers.discount import check_m2m_conflict, PKDiscountList, handle_m2m_field

from base_config.settings import BASE_CURRENCY, SITE_URL


class AppliedDiscountSerializer(Serializer):
    id = IntegerField()
    name = CharField()


class DiscountCreateSerializer(ModelSerializer):
    status_display = CharField(source='get_status_display', read_only=True)
    type_display = CharField(source='get_type_display', read_only=True)
    value_type_display = CharField(source='get_value_type_display', read_only=True)
    valid_from_display = DateTimeField(source='valid_from', format='%d-%m-%Y %H:%M', read_only=True)
    valid_until_display = DateTimeField(source='valid_until', format='%d-%m-%Y %H:%M', read_only=True)

    class Meta:
        model = Discount
        exclude = ['created_by_token', 'is_admin_created', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'landlord_profile']

    def create(self, validated_data: Dict[str, Any]) -> Discount:
        validated_data['created_by'] = self.context['user']
        validated_data['landlord_profile'] = self.context['landlord_profile']
        value_type: str = validated_data.get('value_type')
        currency: Currency | None = validated_data.get('currency', None)

        value: Decimal = validated_data.pop('value')

        if value_type == DiscountValueType.FIXED.value[0]:
            if currency.code != BASE_CURRENCY:
                validated_data['value'] = (value * currency.rate_to_base).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        discount_type: str | None = attrs.get('type', None)
        valid_from: datetime | None = attrs.get('valid_from', None)
        valid_until: datetime | None = attrs.get('valid_until', None)
        value_type: str = attrs.get('value_type')
        currency: Currency | None = attrs.get('currency', None)

        non_field_errors: List[str] = []

        if discount_type in [DiscountType.SEASONAL.value[0], DiscountType.WELCOME.value[0]]:
            raise PermissionDenied(PERMISSION_ERRORS)

        if discount_type == DiscountStatus.SCHEDULED.value[0]:
            if not valid_from or not valid_until:
                non_field_errors.append(DISCOUNT_ERRORS['scheduled'])
        else:
            if bool(valid_from) ^ bool(valid_until):
                non_field_errors.append(DISCOUNT_ERRORS['both_fields'])

        if valid_from and valid_from < now():
            non_field_errors.append(DISCOUNT_ERRORS['past_valid_from'])

        if valid_until and valid_from:
            if valid_until <= valid_from:
                non_field_errors.append(DISCOUNT_ERRORS['short_duration'])

        if value_type == DiscountValueType.FIXED.value[0] and not currency:
            non_field_errors.append(DISCOUNT_ERRORS['currency'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class DiscountBaseSerializer(ModelSerializer):
    type = CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Discount
        fields = ['id', 'name', 'type', 'valid_from', 'valid_until']


class DiscountPublicSerializer(DiscountBaseSerializer):
    value = SerializerMethodField(read_only=True)

    class Meta(DiscountBaseSerializer.Meta):
        model = DiscountBaseSerializer.Meta.model
        fields = DiscountBaseSerializer.Meta.fields + ['description', 'status', 'value_type', 'value',
                                                       'currency']

    def get_value(self, obj: Discount) -> Dict:
        currency: Currency = self.context['currency']

        if obj.value_type == DiscountValueType.FIXED.value[0]:
            if currency:
                return {
                    'type': DiscountValueType.FIXED.value[0],
                    'value': format_price(obj.value, currency.rate_to_base),
                    'code': currency.code,
                    'symbol': currency.symbol
                }
            return {
                'type': DiscountValueType.FIXED.value[0],
                'value': obj.value,
                'code': obj.currency.code,
                'symbol': obj.currency.symbol
            }

        return {
            'type': DiscountValueType.PERCENTAGE.value[0],
            'value': obj.value,
            'symbol': '%'
        }


class DiscountSerializer(ModelSerializer):
    status_display = CharField(source='get_status_display', read_only=True)
    type_display = CharField(source='get_type_display', read_only=True)
    value_type_display = CharField(source='get_value_type_display', read_only=True)
    currency = CurrencyBaseSerializer(read_only=True)
    incompatible_with = DiscountBaseSerializer(many=True, read_only=True)
    value = SerializerMethodField(read_only=True)

    add_incompatible = PKDiscountList()
    remove_incompatible = PKDiscountList()

    class Meta:
        model = Discount
        exclude = ['created_by_token', 'is_admin_created', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'name', 'type', 'value_type', 'currency', 'value', 'currency']

    @atomic_handel
    def update(self, instance: Discount, validated_data: Dict[str, Any]) -> Discount:
        add_incompatible = validated_data.pop('add_incompatible', [])
        remove_incompatible = validated_data.pop('remove_incompatible', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        handle_m2m_field(instance, 'incompatible_with', add_incompatible, remove_incompatible)

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        discount: Discount = self.instance

        valid_from_present = 'valid_from' in attrs
        valid_until_present = 'valid_until' in attrs
        priority_present = 'priority' in attrs
        compatible_present = 'compatible' in attrs

        valid_from: datetime | None = attrs.get('valid_from', discount.valid_from)
        valid_until: datetime | None = attrs.get('valid_until', discount.valid_until)
        add_incompatible = attrs.get('add_incompatible', [])
        remove_incompatible = attrs.get('remove_incompatible', [])

        non_field_errors: List[str] = []

        if discount.status in [DiscountStatus.DRAFT.value[0], DiscountStatus.SCHEDULED.value[0]]:
            if bool(valid_from) ^ bool(valid_until):
                non_field_errors.append(DISCOUNT_ERRORS['both_fields'])

            if valid_from and valid_from < now():
                non_field_errors.append(DISCOUNT_ERRORS['past_valid_from'])

            if valid_until and valid_from:
                if valid_until <= valid_from:
                    non_field_errors.append(DISCOUNT_ERRORS['short_duration'])

            result: str | None = check_m2m_conflict(add_incompatible, remove_incompatible, 'incompatible_with')
            if result:
                non_field_errors.append(result)

            if non_field_errors:
                raise ValidationError({'non_field_errors': non_field_errors})

            return attrs
        else:
            if (
                    any([valid_from_present, valid_until_present, priority_present, compatible_present,
                         add_incompatible, remove_incompatible])
            ):
                raise ValidationError({'non_field_errors': DISCOUNT_ERRORS['late_data_update']})

        return attrs

    def get_value(self, obj: Discount) -> Decimal:
        return format_price(obj.value, obj.currency.rate_to_base)


class DiscountPropertyListCreateSerializer(ListSerializer):
    @atomic_handel
    def create(self, validated_data: List[Dict[str, Any]]) -> List[DiscountProperty]:
        discount: Discount = self.context['discount']
        landlord_profile: LandlordProfile = self.context['landlord_profile']
        user: User = self.context['user']

        return DiscountProperty.objects.bulk_create(
            [DiscountProperty(
                **item,
                discount=discount,
                landlord_profile=landlord_profile,
                added_by=user
            ) for item in validated_data],
            ignore_conflicts=True
        )


class DiscountPropertyCreateSerializer(ModelSerializer):
    class Meta:
        model = DiscountProperty
        fields = ['id', 'discount', 'property', 'landlord_profile', 'added_by', 'is_active']
        read_only_fields = ['discount', 'landlord_profile', 'added_by']

        list_serializer_class = DiscountPropertyListCreateSerializer

    def create(self, validated_data: Dict[str, Any]) -> DiscountProperty:
        validated_data['discount'] = self.context['discount']
        validated_data['landlord_profile'] = self.context['landlord_profile']
        validated_data['added_by'] = self.context['user']
        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        property_ref: Property = attrs.get('property')
        landlord_profile: LandlordProfile = attrs.get('landlord_profile')

        if landlord_profile.pk != property_ref.owner_id:
            raise PermissionDenied(PERMISSION_ERRORS)

        return attrs


class DiscountPropertyBaseSerializer(ModelSerializer):
    discount = DiscountPublicSerializer(read_only=True)
    property = PropertyOwnerBaseSerializer(read_only=True)

    class Meta:
        model = DiscountProperty
        fields = ['id', 'discount', 'property', 'is_active']


class DiscountPropertySerializer(ModelSerializer):
    discount = DiscountPublicSerializer(read_only=True)
    property = PropertyOwnerBaseSerializer(read_only=True)
    added_by = UserBasePublicSerializer(read_only=True)

    class Meta:
        model = DiscountProperty
        fields = '__all__'
        read_only_fields = ['id', 'discount', 'property', 'landlord_profile', 'added_by', 'removed_at', 'created_at',
                            'updated_at']

    def update(self, instance: DiscountProperty, validated_data: Dict[str, Any]) -> DiscountProperty:
        is_active: bool = validated_data.get('is_active', False)
        removed_by: User = self.context['user']

        if not is_active and removed_by:
            instance.set_deactivated(removed_by)
        else:
            instance.set_active()

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance: DiscountProperty = self.instance

        is_active: bool = attrs.get('is_active', False)

        if instance.is_active and is_active:
            raise ValidationError({'non_field_error': DISCOUNT_ERRORS['already_active']})
        if not instance.is_active and not is_active and instance.removed_by:
            raise ValidationError({'non_field_error': DISCOUNT_ERRORS['already_inactive']})

        return attrs


class DiscountUserCreateSerializer(ModelSerializer):
    create_token = BooleanField(write_only=True, default=False)
    invite_url = SerializerMethodField(read_only=True)
    booking = CharField(write_only=True)

    class Meta:
        model = DiscountUser
        fields = ['id', 'discount', 'landlord_profile', 'assigned_by', 'code', 'invite_url', 'booking', 'create_token']
        read_only_fields = ['landlord_profile', 'assigned_by']

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> DiscountUser:
        validated_data['assigned_by'] = self.context['user']
        validated_data['landlord_profile'] = self.context['landlord_profile']
        booking: Booking | None = self.context['booking']

        create_token: bool = validated_data.pop('create_token', False)

        discount_user: DiscountUser = super().create(validated_data)

        if booking:
            discount_user.user = booking.guest
            discount_user.status = DiscountUserStatus.ACTIVE.value[0]
            discount_user.save(update_fields=['user', 'status'])
            return discount_user

        if create_token:
            unique_string = f'{discount_user.pk}-{discount_user.created_at}'
            token: str = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
            discount_user.token = token
            discount_user.save(update_fields=['token'])

        return discount_user

    def get_invite_url(self, obj: DiscountUser) -> str:
        token: str = obj.token

        if token:
            path: str = reverse('referral-discount-redirect', kwargs={'token': obj.token})
            return f'{SITE_URL}{path}'
        return ''


class DiscountUserBaseSerializer(ModelSerializer):
    discount_name = DiscountBaseSerializer(source='discount.name', read_only=True)
    status = CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DiscountUser
        fields = ['id', 'discount_name', 'status', 'used_at', 'expires_at']


class DiscountUserSerializer(ModelSerializer):
    discount = DiscountPublicSerializer(read_only=True)
    status = CharField(source='get_status_display', read_only=True)

    class Meta:
        model = DiscountUser
        exclude = ['assigned_by', 'code', 'token', 'removed_at', 'removed_by', 'remove_reason', 'created_at']


class DiscountUserPropertyOwnerSerializer(ModelSerializer):
    discount = DiscountPublicSerializer(read_only=True)
    user = UserBasePublicSerializer(read_only=True)
    assigned_by = UserBaseSerializer(read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    invite_url = SerializerMethodField(read_only=True)

    class Meta:
        model = DiscountUser
        exclude = ['token', 'used_at']

    def update(self, instance: DiscountUser, validated_data: Dict[str, Any]) -> DiscountUser:
        removed_by: User = self.context['user']
        remove_reason: str | None = validated_data.get('remove_reason')

        instance.removed_by = removed_by
        instance.remove_reason = remove_reason
        instance.status = DiscountUserStatus.REMOVED.value[0]
        instance.removed_at = now()
        instance.save(update_fields=['status', 'removed_at', 'removed_by', 'remove_reason'])

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        instance: DiscountUser = self.instance

        if instance.status == DiscountUserStatus.REMOVED.value[0]:
            raise ValidationError({'status': DISCOUNT_ERRORS['status']})

        remove_reason: str | None = attrs.get('remove_reason', None)

        if not remove_reason or len(remove_reason.strip()) < 40:
            ValidationError({'remove_reason': DISCOUNT_ERRORS['remove_reason']})

        return attrs

    def get_invite_url(self, obj: DiscountUser) -> str:
        token: str = obj.token

        if token:
            path: str = reverse('referral-discount-redirect', kwargs={'token': obj.token})
            return f'{SITE_URL}{path}'
        return ''
