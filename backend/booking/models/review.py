from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from booking.models import Booking
from booking.models.choices import ReviewStatus


class Review(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='reviews',
                                verbose_name=_('Booking'))
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='reviews', verbose_name=_('Author'))
    placement = models.ForeignKey('Placement', on_delete=models.CASCADE, related_name='reviews',
                                  verbose_name=_('Placement'))
    status = models.CharField(max_length=20, choices=ReviewStatus.choices(), default=ReviewStatus.PUBLISHED.name,
                              verbose_name=_('Status'))
    feedback = models.TextField(max_length=1000, validators=[MinLengthValidator(10)], blank=False,
                                verbose_name=_('Feedback'))
    rating = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)],
                                              verbose_name=_('Rating'))
    owner_response = models.TextField(max_length=1000, validators=[MinLengthValidator(10)], blank=True,
                                      verbose_name=_('Owner response'))
    moderator_notes = models.TextField(max_length=2000, blank=True, verbose_name=_('Moderator notes'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self):
        return f'Review by {self.author} to {self.placement}, ({self.rating}/5).'

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    @property
    def check_out_datetime(self):
        return timezone.make_aware(timezone.datetime.combine(self.booking.check_out_date, self.check_out_time))

    def clean(self):
        super().clean()

        if Review.objects.filter(
                author=self.author,
                booking=self.booking,
        ).exclude(status=ReviewStatus.REMOVED.name).exclude(id=self.pk).exists():
            raise ValidationError(_('You have already left a comment for this reservation.'))

        if self.booking.check_in_date > now().date():
            raise ValidationError(_('You can\'t write review for apartments you have in future'))

        if now() < self.check_out_datetime:
            raise ValidationError(_('You can leave a review only after check-out time.'))

        if not Booking.objects.filter(user=self.author, placement=self.placement).exists():
            raise ValidationError(_('You can\'t write review for apartments you didn\'t booked.'))

        if self.author == self.placement.owner:
            raise ValidationError(_('You can\'t write review for your own apartment.'))

        if self.rating not in {1, 2, 3, 4, 5}:
            raise ValidationError({'rating': _('Rating must be between 1 and 5.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
