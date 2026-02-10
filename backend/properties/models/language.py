from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=30, unique=True, verbose_name=_('Name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Language: {self.name}, code: {self.code}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
