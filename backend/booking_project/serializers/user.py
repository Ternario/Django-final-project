import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from booking_project.models.user import User


class UserRegisterSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 're_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get("password")
        re_password = data.get("re_password")

        if not re.match('^[a-zA-Z]*$', first_name):
            raise serializers.ValidationError(
                "The first name must contain only alphabet symbols"
            )

        if not re.match('^[a-zA-Z]*$', last_name):
            raise serializers.ValidationError(
                "The last name must contain only alphabet symbols"
            )

        if password != re_password:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        try:
            validate_password(password)
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})

        return data

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
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']
        read_only_fields = ['first_name', 'last_name', 'username']
        extra_kwargs = {'password': {'write_only': True}}


class UserDetailSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = User
        exclude = ['last_login', 'password', 'is_superuser', 'is_staff', 'user_permissions', 'groups', 'is_deleted',
                   'is_verified', 'is_active', 'is_moderator', 'is_admin']
        read_only_fields = ['id', 'date_joined', 'updated_at', 'email']

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
