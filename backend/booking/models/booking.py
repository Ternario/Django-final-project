from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from booking.models.choices import BookingStatus, CheckInTime, CheckOutTime
from booking.managers.booking import (
    BookingManager, FilterActiveBookingManager, FilterNotActiveBookingManager
)


class Booking(models.Model):
    placement = models.ForeignKey('Placement', on_delete=models.PROTECT, related_name='bookings',
                                  verbose_name=_('Placement'))
    user = models.ForeignKey('User', on_delete=models.PROTECT, related_name='bookings', verbose_name=_('User'))
    check_in_date = models.DateField(null=False, blank=False, verbose_name=_('Check in date'))
    check_out_date = models.DateField(null=False, blank=False, verbose_name=_('Check out date'))
    check_in_time = models.TimeField(choices=[(v.value, v.name) for v in CheckInTime], default=CheckInTime.default(),
                                     blank=True, verbose_name=_('Check in Time'))
    check_out_time = models.TimeField(choices=[(v.value, v.name) for v in CheckOutTime], default=CheckOutTime.default(),
                                      blank=True, verbose_name=_('Check out Time'))
    status = models.CharField(max_length=20, choices=BookingStatus.choices(), default=BookingStatus.PENDING.name,
                              verbose_name=_('Booking Status'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))

    cancelled_by = models.ForeignKey('User', null=True, blank=True, on_delete=models.PROTECT,
                                     related_name='cancelled_bookings', verbose_name=_('Cancelled by'))
    cancellation_reason = models.TextField(null=True, blank=True, verbose_name=_('Cancellation reason'))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Cancellation date'))
    created_at = models.DateField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateField(auto_now=True, verbose_name=_('Updated at'))

    all_objects = BookingManager()
    objects = FilterActiveBookingManager()
    inactive_objects = FilterNotActiveBookingManager()

    def __str__(self):
        return f"{self.placement}. {self.check_in_date} - {self.check_out_date}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')

    def clean(self):
        super().clean()

        if not self.check_in_date:
            raise ValidationError({'check_in_date': _('This field cannot be null.')})

        if not self.check_out_date:
            raise ValidationError({'check_out_date': _('This field cannot be null.')})

        if self.check_in_date < now().date():
            raise ValidationError(_('Start date can\'t be in the past.'))

        if self.check_out_date <= self.check_in_date:
            raise ValidationError(_('The end date must be at least one day later than the start date.'))

        if self.user == self.placement.owner:
            raise ValidationError(_('You can\'t booking your own apartment.'))

        if self.cancelled_by:
            if not self.cancellation_reason:
                raise ValidationError(
                    {'cancellation_reason': _('This field is required when booking is being cancelled.')})
            if len(self.cancellation_reason.strip()) < 40:
                raise ValidationError(
                    {'cancellation_reason': _('Cancellation reason must be at least 40 characters long.')})

        if Booking.objects.filter(
                placement=self.placement,
                check_in_date__lt=self.check_out_date,
                check_out_date__gt=self.check_in_date
        ).exclude(id=self.id).exists():
            raise ValidationError(_('This apartment is already reserved for the selected dates.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.status == BookingStatus.CANCELLED.name or self.status == BookingStatus.COMPLETED.name:
            self.is_active = False
            if not self.cancelled_at:
                self.cancelled_at = now()
        super().save(*args, **kwargs)
