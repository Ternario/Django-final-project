from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentMethod(models.Model):
    code = models.CharField(max_length=20, blank=False, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=30, blank=False, unique=True, verbose_name=_('Name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Payment name: {self.name}, code: {self.code}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Payment method')
        verbose_name_plural = _('Payment methods')
