from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "date_of_birth",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions"
        ]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "date_of_birth",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions"
        ]
