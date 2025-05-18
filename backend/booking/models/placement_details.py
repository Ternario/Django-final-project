from django.db import models

from booking.managers.placement import FilterPlacementRelatedManager
from django.utils.translation import gettext_lazy as _


class PlacementDetails(models.Model):
    objects = FilterPlacementRelatedManager()

    placement = models.OneToOneField('Placement', on_delete=models.CASCADE, related_name='placement_details',
                                     verbose_name=_('Placement'))
    pets = models.BooleanField(default=False, verbose_name=_('Pets friendly'))
    free_wifi = models.BooleanField(default=False, verbose_name=_('Free wifi'))
    smoking = models.BooleanField(default=False, verbose_name=_('Smoking allowed'))
    parking = models.BooleanField(default=False, verbose_name=_('Parking space'))
    room_service = models.BooleanField(default=False, verbose_name=_('Room service'))
    front_desk_allowed_24 = models.BooleanField(default=False, verbose_name=_('24-hour front desk'))
    free_cancellation = models.BooleanField(default=False, verbose_name=_('Free cancellation'))
    balcony = models.BooleanField(default=False, verbose_name=_('Balcony'))
    air_conditioning = models.BooleanField(default=False, verbose_name=_('Air conditioning'))
    washing_machine = models.BooleanField(default=False, verbose_name=_('Washing machine'))
    kitchenette = models.BooleanField(default=False, verbose_name=_('Kitchenette'))
    tv = models.BooleanField(default=False, verbose_name=_('Tv'))
    coffee_tee_maker = models.BooleanField(default=False, verbose_name=_('Coffee/Tea maker'))

    created_at = models.DateField(auto_now_add=True, verbose_name=_('Date created'))
    updated_at = models.DateField(auto_now=True, verbose_name=_('Date updated'))

    def __str__(self):
        return self.placement

    class Meta:
        verbose_name = _('Placement Detail')
        verbose_name_plural = _('Placement Details')
