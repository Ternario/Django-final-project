import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from booking.models.user import User


def validate_user_data(data):
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)
    phone = data.get('phone', None)

    if first_name and not re.match('^[a-zA-Z]+(?:-*[a-zA-Z]+)+(?:-*[a-zA-Z]+)*$', first_name):
        raise serializers.ValidationError(
            {'first_name': 'The First Name must be alphabet characters and can contain up to two dashes.'}
        )
    if last_name and not re.match('^[a-zA-Z]+(?:-*[a-zA-Z]+)+(?:-*[a-zA-Z]+)*$', last_name):
        raise serializers.ValidationError(
            {'last_name': 'The Last Name must be alphabet characters and can contain up to two dashes.'}
        )
    if phone and not re.match(r'^\+[1-9]\s*\(?\d+\)?\s*\d+(?:[-\s]*\d+)*$', phone):
        raise serializers.ValidationError(
            {'phone': 'The Phone Number must start with "+" and contain from 7 to 21 digits'}
        )

    return data


class UserRegisterSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'phone', 'password', 're_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):

        password = attrs.get('password')
        re_password = attrs.get('re_password')

        if password != re_password:
            raise serializers.ValidationError({'password': 'Passwords don\'t match'})

        try:
            validate_password(password)
        except ValidationError as err:
            raise serializers.ValidationError({'password': err.messages})

        return validate_user_data(attrs)

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('re_password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserBaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_of_birth", "phone", "is_landlord",
                  "date_joined"]
        read_only_fields = ['id', 'date_joined']

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

    def validate(self, attrs):
        return validate_user_data(attrs)
