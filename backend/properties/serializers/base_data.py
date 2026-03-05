from __future__ import annotations
from typing import Dict, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from properties.models import Property, Discount, Currency, User
from properties.serializers.landlord_profiles import LandlordProfileCreateSerializer

from properties.utils.choices.discount import DiscountValueType
from properties.utils.currency import format_price, get_default_currency
from properties.utils.decorators import atomic_handel
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.language import get_default_language
from properties.utils.serializers.user import validate_user_data


class UserLandlordCreateSerializer(ModelSerializer):
    re_password = CharField(max_length=128, write_only=True, required=True)
    landlord_profile = LandlordProfileCreateSerializer(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'language', 'currency', 'landlord_profile',
                  'password', 're_password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('re_password')
        landlord_profile: Dict[str, Any] = validated_data.pop('landlord_profile')
        validated_data['is_landlord'] = True

        if 'language' not in validated_data:
            validated_data['language'] = get_default_language()

        if 'currency' not in validated_data:
            validated_data['currency'] = get_default_currency()

        user: User = User.objects.create_user(
            email=validated_data.pop('email'),
            first_name=validated_data.pop('first_name'),
            last_name=validated_data.pop('last_name'),
            password=validated_data.pop('password'),
            **validated_data
        )

        landlord_profile_serializer: LandlordProfileCreateSerializer = LandlordProfileCreateSerializer(
            data=landlord_profile, context={'user': user}
        )
        landlord_profile_serializer.is_valid(raise_exception=True)
        landlord_profile_serializer.save()

        return User.objects.filter(id=user.pk).select_related(
            'language', 'currency'
        ).first()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        password: str = attrs.get('password')
        landlord_type: str = attrs.get('landlord_type')
        re_password: str = attrs.get('re_password')

        if password != re_password:
            raise ValidationError({'non_field_errors': USER_ERRORS['password']})

        try:
            validate_password(password)
        except ValidationError:
            raise ValidationError({'non_field_errors': USER_ERRORS['password_error']})

        if not landlord_type:
            raise ValidationError({'landlord_type': NOT_NULL_FIELD})

        return validate_user_data(attrs)


class PropertyOwnerBaseSerializer(ModelSerializer):
    property_type = CharField(source='get_property_type_display', read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'title', 'slug', 'property_type']


class DiscountBaseSerializer(ModelSerializer):
    value = SerializerMethodField(read_only=True)

    class Meta:
        model = Discount
        fields = ['id', 'name', 'value']

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
