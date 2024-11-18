from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.db import models

from booking_project.booking_info.models.booking_details import BookingDetails
from booking_project.placement.models.placement import Placement
from booking_project.users.models import User


class Review(models.Model):
    objects = models.Manager()

    booking = models.ForeignKey(BookingDetails, on_delete=models.CASCADE, related_name='Booking',
                                verbose_name="Previos Booking")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Author', verbose_name='Author')
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_review',
                                  verbose_name='placement')
    feedback = models.TextField(max_length=350, validators=[MinLengthValidator(10)],
                                verbose_name="Feedback")
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0)],
                                 verbose_name="Rating")
    created_at = models.DateField(auto_now_add=True, verbose_name="Date created")
    updated_at = models.DateField(auto_now=True, verbose_name="Date updated")

    def __str__(self):
        return f"{self.author}, {self.feedback}"

    class Meta:
        ordering = ['-created_at']
