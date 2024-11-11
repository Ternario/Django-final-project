from django.db import models

from booking_project.placement.models.placement import Placement


class BookingDates(models.Model):
    objects = models.Manager()

    placement_id = models.ForeignKey(Placement, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(nutl=False, blank=False, verbose_name="Start date")
    end_date = models.DateField(nutl=False, blank=False, verbose_name="End date")
