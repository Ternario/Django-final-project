from __future__ import annotations

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, CharField

from properties.models import UserProfile
from properties.serializers.property import PropertyBaseSerializer
from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.regex_patterns import match_phone_number


class UserProfileSerializer(ModelSerializer):
    theme_display = CharField(source='get_theme_display', read_only=True)

    class Meta:
        model = UserProfile
        exclude = ['user_token', 'created_at', 'updated_at']
        read_only_fields = ['user']

    def validate_phone(self, phone: str | None) -> str:
        if phone and not match_phone_number(phone):
            raise ValidationError({'phone': USER_ERRORS['phone']})

        return phone
