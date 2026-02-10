from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from properties.utils.choices.gender import Gender
from properties.utils.choices.profile import ProfileTheme
from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.regex_patterns import match_phone_number
from properties.utils.user_token_generation import make_user_token


class UserProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.SET_NULL, null=True, related_name='profile',
                                verbose_name=_('User'))
    user_token = models.CharField(max_length=64, blank=True, db_index=True, verbose_name=_('User token'))
    phone = models.CharField(max_length=21, blank=True, unique=True,
                             validators=[MinLengthValidator(7), MaxLengthValidator(21)], verbose_name=_('Phone number'))
    gender = models.CharField(max_length=1, blank=True, choices=Gender.choices(), verbose_name=_('Gender'))
    citizenship = models.CharField(max_length=30, blank=True, verbose_name=_('Citizenship'))

    theme = models.CharField(max_length=20, blank=True, choices=ProfileTheme.choices(),
                             default=ProfileTheme.LIGHT.value[0], verbose_name=_('Theme'))
    receive_email_notifications = models.BooleanField(default=True, verbose_name=_('Receive email notifications'))
    receive_push_notifications = models.BooleanField(default=True, verbose_name=_('Receive push notifications'))

    favorites = models.ManyToManyField('Property', blank=True, related_name='favorites', verbose_name=_('Favorites'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    objects = models.Manager()

    def __str__(self) -> str:
        if self.user:
            return f'User profile to {self.user}, id: {self.pk}.'
        return f'Anonymous profile {self.user_token}, id: {self.pk}.'

    class Meta:
        verbose_name = _('User profile')
        verbose_name_plural = _('User profiles')

    def clean(self) -> None:
        super().clean()

        if self.phone and not match_phone_number(self.phone):
            raise ValidationError({'phone': USER_ERRORS['phone']})

    def privacy_delete(self) -> None:
        if not self.user:
            return
        self.user_token = make_user_token(self.user_id)
        self.user = None
        self.phone = f'deleted_{self.pk}'
        self.gender = ''
        self.citizenship = ''
        self.favorites.clear()
        self.save()
