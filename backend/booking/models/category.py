from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'categories'
