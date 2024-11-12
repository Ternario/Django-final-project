from django.db import models

from booking_project.placement.models.placement import Placement
from booking_project.users.models.user import User


class BookingDates(models.Model):
    objects = models.Manager()

    placement_id = models.ForeignKey(Placement, on_delete=models.PROTECT)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT)
    start_date = models.DateField(null=False, blank=False, verbose_name="Start date")
    end_date = models.DateField(null=False, blank=False, verbose_name="End date")