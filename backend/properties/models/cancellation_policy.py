from decimal import Decimal

from django.core.validators import MinLengthValidator, MaxLengthValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from properties.utils.choices.booking import CancellationPolicy as Policy


class CancellationPolicy(models.Model):
    name = models.CharField(max_length=155, blank=False, unique=True, verbose_name=_('Policy name'))
    type = models.CharField(max_length=20, choices=Policy.choices(), blank=False, verbose_name=_('Policy type'))
    description = models.TextField(blank=False, validators=[MinLengthValidator(10), MaxLengthValidator(500)],
                                   verbose_name=_('Description'))
    free_cancellation_days = models.PositiveIntegerField(blank=False, default=1, validators=[MaxValueValidator(31)],
                                                         verbose_name=_('Free cancellation days'))
    refund_percentage_after_deadline = models.DecimalField(blank=False, max_digits=5, decimal_places=2,
                                                           default=Decimal('0.00'),
                                                           validators=[MaxValueValidator(Decimal('100.00'))],
                                                           verbose_name=_('Refund percentage after deadline'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Policy name: {self.name}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Cancellation Policy')
        verbose_name_plural = _('Cancellation Policies')
