from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator, RegexValidator
from django.utils.text import gettext_lazy as _

from .categories import Categories


class Apartments(models.Model):
    objects = models.Manager()

    is_active = models.BooleanField(default=True, verbose_name="Is active")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Owner", verbose_name="Owner")

    category = models.ForeignKey(Categories, on_delete=models.PROTECT, related_name="Apartments",
                                 verbose_name="Category", db_index=True)
    title = models.CharField(max_length=130, verbose_name="Apartments title")
    description = models.TextField(max_length=250, validators=[MinLengthValidator(40)],
                                   verbose_name="Apartments description")
    city = models.CharField(max_length=100, verbose_name="City name")
    post_code = models.CharField(max_length=6, validators=[RegexValidator('^[0-9]{0,6}$', _('Invalid postal code'))])
    street = models.CharField(max_length=120, verbose_name="Street name")
    house_number = models.CharField(max_length=30, verbose_name="House number")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    number_of_rooms = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)],
                                                  verbose_name="Number of rooms")
    apartment_area = models.DecimalField(max_digits=5, decimal_places=2,
                                         validators=[MaxValueValidator(400), MinValueValidator(10)],
                                         verbose_name="Area of apartment")
    number_of_beds = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)],
                                                 verbose_name="Number of beds")
    single_bed = models.IntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)],
                                     verbose_name="Number of single bed")
    double_bed = models.IntegerField(default=0, validators=[MaxValueValidator(6), MinValueValidator(0)],
                                     verbose_name="Number of double bed")

    pets = models.BooleanField(default=False, verbose_name="Pets friendly")
    free_wifi = models.BooleanField(default=False, verbose_name="Free wifi")
    smoking = models.BooleanField(default=False, verbose_name="Smoking allowed")
    parking = models.BooleanField(default=False, verbose_name="Parking space")
    room_service = models.BooleanField(default=False, verbose_name="Room service")
    front_desk_allowed_24 = models.BooleanField(default=False, verbose_name="24-hour front desk")
    free_cancellation = models.BooleanField(default=False, verbose_name="Free cancellation")
    balcony = models.BooleanField(default=False, verbose_name="Balcony")
    air_conditioning = models.BooleanField(default=False, verbose_name="Air conditioning")
    washing_machine = models.BooleanField(default=False, verbose_name="Washing machine")
    kitchenette = models.BooleanField(default=False, verbose_name="Kitchenette")
    tv = models.BooleanField(default=False, verbose_name="Tv")
    coffee_tee_maker = models.BooleanField(default=False, verbose_name="Coffee/Tea maker")

    created_at = models.DateField(auto_now_add=True, verbose_name="Date created")
    updated_at = models.DateField(auto_now=True, erbose_name="Date updated")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(single_bed__isnull=False) | Q(double_bed__isnull=False),
                name="Both fields can't be zero"
            )
        ]
