from decimal import Decimal
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import Property

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q, F

from django.utils.translation import gettext_lazy as _

from properties.models import Property
from properties.utils.choices.details_access import DetailsAccess
from properties.utils.choices.time import CheckInTime, CheckOutTime
from properties.utils.choices.property import PropertyType
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.error_messages.property_details import PROPERTY_DETAILS_ERRORS


class PropertyDetail(models.Model):
    property_ref = models.OneToOneField('Property', on_delete=models.CASCADE, related_name='detail',
                                        verbose_name=_('Property'))
    property_area = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'),
                                        validators=[MinValueValidator(Decimal('15.00')),
                                                    MaxValueValidator(Decimal('2000.00'))],
                                        verbose_name=_('Total property area'))
    floor = models.SmallIntegerField(default=1, validators=[MinValueValidator(-1)], verbose_name=_('Floor'))
    total_floors = models.PositiveSmallIntegerField(verbose_name=_('Total floor'))
    number_of_rooms = models.PositiveSmallIntegerField(default=1,
                                                       validators=[MinValueValidator(1), MaxValueValidator(6)],
                                                       verbose_name=_('Number of rooms'))
    total_beds = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(15), MinValueValidator(1)],
                                                  verbose_name=_('Total beds'))
    single_beds = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(15)],
                                                   verbose_name=_('Number of single beds'))
    double_beds = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(15)],
                                                   verbose_name=_('Number of double beds'))
    sofa_beds = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(15)],
                                                 verbose_name=_('Number of sofa beds'))
    number_of_bathrooms = models.PositiveSmallIntegerField(default=0,
                                                           validators=[MinValueValidator(0), MaxValueValidator(6)],
                                                           verbose_name=_('Number of bathrooms'))
    shower = models.BooleanField(default=False, verbose_name=_('Shower'))
    bathtub = models.BooleanField(default=False, verbose_name=_('Bathtub'))
    toilet = models.BooleanField(default=False, verbose_name=_('Toilet'))
    bathroom_access = models.CharField(max_length=10, choices=DetailsAccess.choices(),
                                       default=DetailsAccess.PRIVATE.value[0],
                                       verbose_name=_('Bathroom access'))
    kitchen = models.BooleanField(default=False, verbose_name=_('Kitchen'))
    kitchen_access = models.CharField(max_length=10, choices=DetailsAccess.choices(),
                                      default=DetailsAccess.PRIVATE.value[0], verbose_name=_('Kitchen access'))
    num_balcony = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(4)],
                                                   verbose_name=_('Num balcony'))
    terrace = models.BooleanField(default=False, verbose_name=_('Terrace'))
    terrace_access = models.CharField(max_length=10, choices=DetailsAccess.choices(),
                                      default=DetailsAccess.PRIVATE.value[0], verbose_name=_('Terrace access'))
    garden = models.BooleanField(default=False, verbose_name=_('Garden'))
    garden_access = models.CharField(max_length=10, choices=DetailsAccess.choices(),
                                     default=DetailsAccess.PRIVATE.value[0], verbose_name=_('Garden access'))

    check_in_from = models.TimeField(choices=CheckInTime.choices(), default=CheckInTime.default(),
                                     verbose_name=_('Check in from'))
    check_out_until = models.TimeField(choices=CheckOutTime.choices(), default=CheckOutTime.default(),
                                       verbose_name=_('Check out until'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Details to property: {self.property_ref}, id: {self.pk}.'

    class Meta:
        verbose_name = _('Property Detail')
        verbose_name_plural = _('Property Details')

        constraints = [
            models.CheckConstraint(
                condition=~(Q(single_beds=0) & Q(double_beds=0) & Q(sofa_beds=0)),
                name='all_beds_fields_cannot_be_zero'
            ),
            models.CheckConstraint(
                condition=Q(total_beds=F('single_beds') + F('double_beds') + F('sofa_beds')),
                name='all_bed_fields_must_be_equal_to_the_total_beds'
            ),
            models.CheckConstraint(
                check=Q(floor__gte=-1) & Q(floor__lte=F('total_floors')),
                name='valid_floor_value'
            )
        ]

    def clean(self) -> None:
        super().clean()

        if not self.property_ref_id:
            raise ValidationError({'property_ref': NOT_NULL_FIELD})

        property_data: Property = self.property_ref

        non_field_errors: List[str] = []

        if not (self.single_beds or self.double_beds or self.sofa_beds):
            non_field_errors.append(PROPERTY_DETAILS_ERRORS['beds'])

        if self.total_beds != (self.single_beds + self.double_beds + self.sofa_beds):
            non_field_errors.append(PROPERTY_DETAILS_ERRORS['total_beds'])

        if property_data.property_type not in [PropertyType.HOUSE.value[0], PropertyType.VILLA.value[0]]:
            if not self.floor or not self.total_floors:
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['empty_floors'])
            elif self.floor < -1 or self.floor > self.total_floors:
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['floor'].format(total_floors=self.total_floors))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})
