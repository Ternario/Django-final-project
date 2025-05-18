from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

from booking.managers.user import CustomUserManager


class User(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=35, unique=True, null=True, blank=True, verbose_name='Username')
    email = models.EmailField(blank=False, null=False, unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=155, null=False, blank=False, verbose_name='First Name')
    last_name = models.CharField(max_length=155, null=False, blank=False, verbose_name='Last Name')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Birthday')
    phone = models.CharField(validators=[MinLengthValidator(7), MaxLengthValidator(mx_num := 21)],
                             max_length=mx_num, unique=True, verbose_name='Phone number')

    is_admin = models.BooleanField(default=False, verbose_name='Is admin')
    is_moderator = models.BooleanField(default=False, verbose_name='Moderator')
    is_landlord = models.BooleanField(default=False, verbose_name='Is landlord')
    is_verified = models.BooleanField(default=False, verbose_name='Is verified')
    is_deleted = models.BooleanField(default=False, verbose_name='Is deleted')

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='registered')
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'phone',
    ]

    objects = CustomUserManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.email

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()
