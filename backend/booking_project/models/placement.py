from django.db import models
from django.db.models import Q
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator

from booking_project.models.user import User
from booking_project.models.category import Category


class Placement(models.Model):
    objects = models.Manager()

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Owner", verbose_name="Owner")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="Apartments",
                                 verbose_name="Category", db_index=True)
    title = models.CharField(max_length=255, verbose_name="Apartments title")
    description = models.TextField(max_length=2000, validators=[MinLengthValidator(40)],
                                   verbose_name="Apartments description")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    number_of_rooms = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)],
                                                  verbose_name="Number of rooms")
    placement_area = models.FloatField(blank=False, null=False, default=0)
    number_of_beds = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(10), MinValueValidator(1)],
                                                 verbose_name="Number of beds")
    single_bed = models.IntegerField(default=1, validators=[MaxValueValidator(15), MinValueValidator(0)],
                                     verbose_name="Number of single bed")
    double_bed = models.IntegerField(default=0, validators=[MaxValueValidator(15), MinValueValidator(0)],
                                     verbose_name="Number of double bed")

    created_at = models.DateField(auto_now_add=True, verbose_name="Date created")
    updated_at = models.DateField(auto_now=True, verbose_name="Date updated")

    is_active = models.BooleanField(default=True, verbose_name="Is active")
    is_deleted = models.BooleanField(default=False, verbose_name="Is deleted")

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

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save()
