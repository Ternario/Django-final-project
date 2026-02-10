from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Currency(models.Model):
    code = models.CharField(max_length=3, validators=[RegexValidator('^[A-Z]{3}$')], unique=True,
                            verbose_name=_('Code'))
    name = models.CharField(max_length=30, unique=True, verbose_name=_('Name'))
    symbol = models.CharField(max_length=5, blank=True, null=True, verbose_name=_('Symbol'))
    rate_to_base = models.DecimalField(max_digits=12, decimal_places=6)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Currency: {self.name}, code: {self.code}, symbol: {self.symbol}.'

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
