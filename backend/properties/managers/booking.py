from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from django.db.models import QuerySet
    from properties.models import Booking

import uuid

from django.db import models
from django.utils import timezone


class CustomManager(models.Manager):
    """
    Custom manager for the Booking model that provides utility methods
    for creating bookings with automatic booking number generation
    and filtering based on their active status.

    Supports:
        - Automatic generation of unique booking numbers if not provided.
        - Filtering bookings by active or inactive status.

    Methods:
        create(**kwargs)
            Creates a new Booking instance with optional automatic booking number.
        active() -> QuerySet[Booking]
            Returns all bookings that are currently active.
        inactive() -> QuerySet[Booking]
            Returns all bookings that are currently inactive.
    """

    def create(self, **kwargs: Any) -> Booking:
        """
        Create a new Booking instance with an optional automatic booking number.

        If 'booking_number' is not supplied in kwargs, this method generates
        a unique booking number using the current date and a random 6-character
        hexadecimal string, in the format:
            'BN<year>-<month><day>-<6_hex_chars>'

        Args:
            **kwargs: Fields to set on the Booking instance.

        Returns:
            Booking: The newly created Booking instance.
        """
        if not kwargs.get('booking_number'):
            now: datetime = timezone.now()
            kwargs['booking_number'] = f'BN{now.year}-{now.month:02d}{now.day:02d}-{uuid.uuid4().hex[:6].upper()}'

        return super().create(**kwargs)

    def active(self, **kwargs: Any) -> QuerySet[Booking]:
        """
        Retrieve all active bookings.

        Active bookings are those where the 'is_active' field is True.

        Returns:
            QuerySet[Booking]: QuerySet containing all active Booking instances.
        """
        return self.filter(is_active=True, **kwargs)

    def inactive(self, **kwargs: Any) -> QuerySet[Booking]:
        """
        Retrieve all inactive bookings.

        Inactive bookings are those where the 'is_active' field is False.

        Returns:
            QuerySet[Booking]: QuerySet containing all inactive Booking instances.
        """
        return self.filter(is_active=False, **kwargs)
