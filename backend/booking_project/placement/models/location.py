from django.core.validators import RegexValidator
from django.utils.text import gettext_lazy as _
from django.db import models


class Location(models.Model):
    objects = models.Manager()

    country = models.CharField(max_length=155, verbose_name="Country name")
    city = models.CharField(max_length=100, verbose_name="City name")
    post_code = models.CharField(max_length=6, validators=[RegexValidator('^[0-9]{0,6}$', _('Invalid postal code'))])
    street = models.CharField(max_length=155, verbose_name="Street name")
    house_number = models.CharField(max_length=30, verbose_name="House number")
    # latitude
    # longitude