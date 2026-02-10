from django.db import models
from django.utils.text import gettext_lazy as _

from properties.utils.choices.payment import PaymentType as Type


class PaymentType(models.Model):
    code = models.CharField(max_length=20, choices=Type.choices(), unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=50, choices=Type.choices(), unique=True, verbose_name=_('Name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Name: {self.name}, code: {self.code}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Payment type')
        verbose_name_plural = _('Payment types')
