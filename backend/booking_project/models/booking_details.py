from django.db import models

from booking_project.models import Placement
from booking_project.models import User


class BookingDetails(models.Model):
    objects = models.Manager()

    placement = models.ForeignKey(Placement, on_delete=models.PROTECT, related_name="Placement")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="User")
    start_date = models.DateField(null=False, blank=False, verbose_name="Start date")
    end_date = models.DateField(null=False, blank=False, verbose_name="End date")
    is_confirmed = models.BooleanField(default=False, verbose_name="Is confirmed")
    is_cancelled = models.BooleanField(default=False, verbose_name="Is cancelled")
    is_active = models.BooleanField(default=True, verbose_name="Is active")
    created_at = models.DateField(auto_now_add=True, verbose_name="Date created")
    updated_at = models.DateField(auto_now=True, verbose_name="Date updated")

    def __str__(self):
        return f"{self.placement}. {self.start_date} - {self.end_date}"

    class Meta:
        ordering = ['-created_at']
