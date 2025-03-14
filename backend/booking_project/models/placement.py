from decimal import Decimal

from django.db import models
from django.db.models import Q, F
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator, MaxLengthValidator

from booking_project.models.user import User
from booking_project.models.category import Category
from booking_project.utils.placement_manager import (
    FilterActiveManager, FilterNotActiveManager, FilterDeletedManagers, FilterNotDeletedManager
)


class Placement(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Owner', verbose_name='Owner')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='Apartments',
                                 verbose_name='Category', db_index=True)
    title = models.CharField(max_length=255, unique=True, blank=False, null=False, verbose_name='Apartments title')
    description = models.TextField(validators=[MinLengthValidator(40), MaxLengthValidator(2000)], blank=False,
                                   null=False,
                                   verbose_name='Apartments description')

    price = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('10.00'))],
                                blank=False,
                                null=False, verbose_name='Price')
    number_of_rooms = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(6), MinValueValidator(1)],
                                                  verbose_name='Number of rooms')
    placement_area = models.DecimalField(max_digits=5, decimal_places=2,
                                         validators=[MinValueValidator(Decimal('15.00')),
                                                     MaxValueValidator(Decimal('500.00'))],
                                         blank=False,
                                         null=False, default=0)
    total_beds = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(15), MinValueValidator(1)],
                                             verbose_name='Total beds')
    single_bed = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(15)],
                                             verbose_name='Number of single bed')
    double_bed = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(15)],
                                             verbose_name='Number of double bed')

    created_at = models.DateField(auto_now_add=True, verbose_name='Date created')
    updated_at = models.DateField(auto_now=True, verbose_name='Date updated')

    is_active = models.BooleanField(default=False, verbose_name='Is active')
    is_deleted = models.BooleanField(default=False, verbose_name='Is deleted')

    objects = FilterActiveManager()
    inactive_objects = FilterNotActiveManager()
    deleted_objects = FilterDeletedManagers()
    all_objects = FilterNotDeletedManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=~(Q(single_bed=0) & Q(double_bed=0)),
                name='Both bed fields can\'t be zero.'
            ),
            models.CheckConstraint(
                condition=Q(total_beds=F('single_bed') + F('double_bed')),
                name='Both bed fields must be equal to the total beds.'
            ),
        ]

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save()
