from django.core.validators import RegexValidator
from django.utils.text import gettext_lazy as _
from django.db import models

from booking_project.placement.models.placement import Placement


class Location(models.Model):
    objects = models.Manager()

    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_location',
                                  verbose_name='placement')
    country = models.CharField(max_length=155, blank=True, verbose_name="Country name")
    city = models.CharField(max_length=100, blank=True, verbose_name="City name")
    post_code = models.CharField(max_length=6, blank=True,
                                 validators=[RegexValidator('^[0-9]{0,6}$', _('Invalid postal code'))])
    street = models.CharField(max_length=155, blank=True, verbose_name="Street name")
    house_number = models.CharField(max_length=30, blank=True, verbose_name="House number")
    created_at = models.DateField(auto_now_add=True, verbose_name="Date created")
    updated_at = models.DateField(auto_now=True, verbose_name="Date created")
    # latitude
    # longitude
