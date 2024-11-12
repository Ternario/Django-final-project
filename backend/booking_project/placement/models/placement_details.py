from django.db import models

from booking_project.placement.models.placement import Placement


class PlacementDetails(models.Model):
    objects = models.Manager()

    placement_id = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_details')
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
    updated_at = models.DateField(auto_now=True, verbose_name="Date updated")
