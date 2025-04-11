from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from booking_project.models import Placement
from booking_project.models import User
from booking_project.models.choices import BookingStatus, CheckInTime, CheckOutTime
from booking_project.utils.booking_manager import (
    BookingManager, FilterActiveBookingManager, FilterNotActiveBookingManager
)


class Booking(models.Model):
    placement = models.ForeignKey(Placement, on_delete=models.PROTECT, related_name='Placement')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='User')
    check_in_date = models.DateField(null=False, blank=False, verbose_name='Start date')
    check_out_date = models.DateField(null=False, blank=False, verbose_name='End date')
    check_in_time = models.TimeField(choices=[(v.value, v.name) for v in CheckInTime], default=CheckInTime.default(),
                                     blank=True,
                                     verbose_name='Check-in Time')
    check_out_time = models.TimeField(choices=[(v.value, v.name) for v in CheckOutTime], default=CheckOutTime.default(),
                                      blank=True,
                                      verbose_name='Check-out Time')
    status = models.CharField(max_length=20, choices=BookingStatus.choices(), default=BookingStatus.PENDING.value,
                              verbose_name='Booking Status')
    is_active = models.BooleanField(default=True, verbose_name='Is active')

    cancelled_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.PROTECT,
        related_name='cancelled_bookings', verbose_name="Cancelled by"
    )
    cancellation_reason = models.TextField(null=True, blank=True, verbose_name="Cancellation reason")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Cancellation date")
    created_at = models.DateField(auto_now_add=True, verbose_name='Date created')
    updated_at = models.DateField(auto_now=True, verbose_name='Date updated')

    all_objects = BookingManager()
    objects = FilterActiveBookingManager()
    inactive_objects = FilterNotActiveBookingManager()

    def __str__(self):
        return f"{self.placement}. {self.check_in_date} - {self.check_out_date}"

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if not self.user_id:
            raise ValidationError({'user': 'This field cannot be null.'})

        if not self.placement_id:
            raise ValidationError({'placement': 'This field cannot be null.'})

        if not self.check_in_date:
            raise ValidationError({'check_in_date': 'This field cannot be null.'})

        if not self.check_out_date:
            raise ValidationError({'check_out_date': 'This field cannot be null.'})

        if self.check_in_date < now().date():
            raise ValidationError('Start date can\'t be in the past.')

        if self.check_out_date <= self.check_in_date:
            raise ValidationError('The end date must be at least one day later than the start date.')

        if self.user == self.placement.owner:
            raise ValidationError('You can\'t booking your own apartment.')

        if self.cancelled_by:
            if not self.cancellation_reason:
                raise ValidationError(
                    {'cancellation_reason': 'This field is required when booking is being cancelled.'})
            if len(self.cancellation_reason.strip()) < 40:
                raise ValidationError(
                    {'cancellation_reason': 'Cancellation reason must be at least 40 characters long.'})

        bookings = Booking.objects.filter(
            placement=self.placement,
        ).filter(
            Q(check_in_date__lt=self.check_out_date) &
            Q(check_out_date__gt=self.check_in_date)
        ).exclude(id=self.id)

        if bookings.exists():
            raise ValidationError('This apartment is already reserved for the selected dates.')

    def save(self, *args, **kwargs):
        self.clean()
        if self.status == BookingStatus.CANCELLED.value and not self.cancelled_at:
            self.cancelled_at = now()
        super().save(*args, **kwargs)
