from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import gettext_lazy as _


class Location(models.Model):
    property_ref = models.OneToOneField('Property', on_delete=models.CASCADE, related_name='location',
                                        verbose_name=_('Location'))
    country = models.ForeignKey('Country', on_delete=models.PROTECT, related_name='locations',
                                verbose_name=_('Country'))
    region = models.ForeignKey('Region', on_delete=models.PROTECT, blank=True, null=True, related_name='locations',
                               verbose_name=_('Region'))
    city = models.ForeignKey('City', on_delete=models.PROTECT, related_name='locations', verbose_name=_('City'))
    post_code = models.CharField(max_length=20, validators=[MinLengthValidator(5)], verbose_name=_('Post code'))
    street = models.CharField(max_length=255, verbose_name=_('Street'))
    house_number = models.CharField(max_length=255, verbose_name=_('House number'))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_('Latitude'))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_('Longitude'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        region: str = f'Region: {self.region},'

        return f'Country: {self.country}, {region if self.region else None} City: {self.city}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

        unique_together = ('city', 'post_code', 'street', 'house_number')
