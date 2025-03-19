from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.text import gettext_lazy as _
from django.db import models

from booking_project.models import Placement
from booking_project.utils.placement_manager import FilterPlacementRelatedManager


class PlacementLocation(models.Model):
    objects = FilterPlacementRelatedManager()

    placement = models.OneToOneField(Placement, on_delete=models.CASCADE, related_name='placement_location',
                                     verbose_name='placement')
    country = models.CharField(max_length=155, blank=False, null=False, verbose_name='Country name')
    city = models.CharField(max_length=155, blank=False, null=False, verbose_name='City name')
    post_code = models.CharField(max_length=6, blank=False, null=False,
                                 validators=[MinLengthValidator(5),
                                             RegexValidator('^[0-9]{5}$', _('Invalid postal code.'))])
    street = models.CharField(max_length=155, blank=False, null=False, verbose_name="Street name")
    house_number = models.CharField(max_length=30, blank=False, null=False, verbose_name='')

    created_at = models.DateField(auto_now_add=True, verbose_name='')
    updated_at = models.DateField(auto_now=True, verbose_name='Date updated')

    def __str__(self):
        return f"{self.placement}, {self.country}, {self.city}"
