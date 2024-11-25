import os
import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..media_services import delete_old_file
from ..models.user import User


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not re.match('^[a-zA-Z]*$', first_name):
            raise serializers.ValidationError(
                "The first name must contain only alphabet symbols"
            )

        if not re.match('^[a-zA-Z]*$', last_name):
            raise serializers.ValidationError(
                "The last name must contain only alphabet symbols"
            )

        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        try:
            validate_password(password)
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserBaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'user_img']
        read_only_fields = ['first_name', 'last_name', 'username', 'user_img']
        extra_kwargs = {'password': {'write_only': True}}


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['last_login', 'password', 'is_superuser', 'is_staff', 'user_permissions', 'groups', 'is_deleted',
                   'is_verified', 'is_active']
        read_only_fields = ['id', 'date_joined', 'updated_at', 'email', 'user_img']

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance

        # password = validated_data.pop('password')
        # if password is not None:
        #     instance.set_password(password)


class UserImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_img']

    def update(self, instance, validated_data):
        if len(str(instance.user_img)) > 0 and not validated_data['user_img']:
            delete_old_file(instance.user_img.path)

        if len(str(instance.user_img)) > 0 and validated_data['user_img']:
            delete_old_file(instance.user_img.path)

        setattr(instance, str(list(validated_data.keys())[0]), validated_data['user_img'])

        instance.save()

        return instance

    def validate(self, data):
        if data['user_img']:
            type_list = ['jpg', 'png']
            img, img_type = str(data['user_img']).split('.')

            if img_type not in type_list:
                raise serializers.ValidationError({"image": "Invalid file type"})

        return data
