from django.db import models
from django.utils.translation import gettext_lazy as _


class AmenityCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Name: {self.name}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Amenity Category')
        verbose_name_plural = _('Amenity Categories')


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    category = models.ForeignKey('AmenityCategory', on_delete=models.PROTECT, related_name='amenities',
                                 verbose_name=_('Category'))
    description = models.TextField(blank=True, verbose_name=_('Description'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Name: {self.name} by amenity category: {self.category}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')
