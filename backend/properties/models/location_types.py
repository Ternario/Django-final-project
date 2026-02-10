from django.db import models

from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True, verbose_name=_('Country name'))
    code = models.CharField(max_length=3, unique=True, verbose_name=_('Country code'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self) -> str:
        return f'Country ame: {self.name}, code: {self.code}, id: {self.pk}.'


class Region(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name=_('Region name'))
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='regions',
                                verbose_name=_('Country name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

        unique_together = ('name', 'country')

    def __str__(self) -> str:
        return f'Region name: {self.name}, country: {self.country}, id: {self.pk}.'


class City(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name=_('City name'))
    region = models.ForeignKey('Region', on_delete=models.CASCADE, null=True, blank=True, related_name='cities',
                               verbose_name=_('Region name'))
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='cities',
                                verbose_name=_('Country name'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

        unique_together = ('name', 'region', 'country')

    def __str__(self) -> str:
        region: str = f'Region: {self.region}, '
        return f'City name: {self.name}, {region if self.region else None}Country: {self.country}, id: {self.pk}.'
