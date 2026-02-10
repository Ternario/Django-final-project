from __future__ import annotations

from typing import Dict, Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import HttpRequest
from rest_framework.serializers import (
    ModelSerializer, Serializer, ValidationError, CharField, SerializerMethodField, EmailField
)

from properties.models.user import User

from properties.serializers.language import LanguageSerializer
from properties.serializers.currency import CurrencySerializer

from properties.serializers.user_profile import UserProfileSerializer
from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.currency import get_default_currency

from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.language import get_default_language
from properties.utils.serializers.user import validate_user_data


class UserCreateSerializer(ModelSerializer):
    re_password = CharField(max_length=128, write_only=True, required=True)
    user_profile = UserProfileSerializer(source='profile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'is_landlord', 'landlord_type', 'password',
                  're_password', 'user_profile']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('re_password')

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


class UserLoginSerializer(Serializer):
    email = EmailField(required=True)
    password = CharField(write_only=True, required=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        email: str = attrs.get('email')
        password: str = attrs.get('password')
        request: HttpRequest = self.context['request']

        user: User = authenticate(request, username=email, password=password)

        if not user:
            raise ValidationError({'detail': 'Invalid credentials.'})

        user = User.objects.select_related('language', 'currency').get(pk=user.pk)

        attrs['user'] = user

        return attrs


class UserBasePublicSerializer(ModelSerializer):
    user_name = SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_name']

    def get_user_name(self, obj: User) -> str:
        if obj.username:
            return obj.username

        return f'{obj.first_name} {obj.last_name}'


class UserBaseSerializer(UserBasePublicSerializer):
    role = SerializerMethodField()

    class Meta(UserBasePublicSerializer.Meta):
        model = UserBasePublicSerializer.Meta.model
        fields = UserBasePublicSerializer.Meta.fields + ['id', 'role']

    def get_role(self, obj: User) -> str:
        if obj.is_admin:
            return 'Admin'

        if obj.is_landlord:
            if obj.landlord_type == LandlordType.INDIVIDUAL.value[0]:
                return 'Owner'

            if obj.landlord_type == LandlordType.COMPANY.value[0]:
                return 'Company Owner'

            if obj.landlord_type == LandlordType.COMPANY_MEMBER.value[0]:
                return 'Company member'

        return ''


class UserSerializer(ModelSerializer):
    language_display = LanguageSerializer(source='language', read_only=True)
    currency_display = CurrencySerializer(source='currency', read_only=True)
    landlord_type = CharField(source='get_landlord_type_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_of_birth', 'language', 'language_display',
                  'currency', 'currency_display', 'is_landlord', 'landlord_type']
        read_only_fields = ['is_landlord', 'landlord_type']

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        return validate_user_data(attrs)
