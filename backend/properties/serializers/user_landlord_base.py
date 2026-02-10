from __future__ import annotations

from typing import Dict, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

from properties.models import User

from properties.serializers.landlord_profiles import LandlordProfileCreateSerializer, LandlordProfileBaseSerializer
from properties.serializers.user import UserCreateSerializer
from properties.utils.currency import get_default_currency

from properties.utils.decorators import atomic_handel
from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.language import get_default_language
from properties.utils.serializers.user import validate_user_data


class UserLandlordCreateSerializer(UserCreateSerializer):
    landlord_profile = LandlordProfileCreateSerializer(write_only=True, required=True)
    landlord_profile_details = LandlordProfileBaseSerializer(source='landlord_profiles', many=True, read_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = UserCreateSerializer.Meta.model
        fields = UserCreateSerializer.Meta.fields + ['landlord_profile', 'landlord_profile_details']
        extra_kwargs = UserCreateSerializer.Meta.extra_kwargs

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('re_password')
        landlord_profile: Dict[str, Any] = validated_data.pop('landlord_profile')

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
        re_password: str = attrs.get('re_password')

        if password != re_password:
            raise ValidationError({'non_field_errors': USER_ERRORS['password']})

        try:
            validate_password(password)
        except ValidationError:
            raise ValidationError({'non_field_errors': USER_ERRORS['password_error']})

        return validate_user_data(attrs)
