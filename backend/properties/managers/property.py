from __future__ import annotations
from typing import TYPE_CHECKING, List, Any

if TYPE_CHECKING:
    from properties.models import Property, PropertyDetails, PropertyImage

from django.db import models
from django.db.models import QuerySet

from properties.utils.choices.property import PropertyAvailabilityStatus


class CustomPropertyManager(models.Manager):
    """
    Custom manager for the Property model that provides utility methods
    to filter properties based on their deletion status and availability.

    Supports:
        - Retrieving active properties.
        - Retrieving inactive properties (including under maintenance).
        - Retrieving deleted properties.
        - Retrieving all non-deleted properties.

    Methods:
        active() -> QuerySet[Property]
            Returns all active, non-deleted properties.
        inactive() -> QuerySet[Property]
            Returns all inactive or under-maintenance, non-deleted properties.
        deleted() -> QuerySet[Property]
            Returns all deleted properties.
        not_deleted() -> QuerySet[Property]
            Returns all properties that are not marked as deleted.
    """

    def active(self, **kwargs: Any) -> QuerySet[Property]:
        """
        Retrieve all active, non-deleted properties.

        Returns:
            QuerySet[Property]: QuerySet containing properties with `is_deleted=False`
            and status equal to `PropertyAvailabilityStatus.ACTIVE`.
        """
        return self.filter(is_deleted=False, status=PropertyAvailabilityStatus.ACTIVE.value[0], **kwargs)

    def inactive(self, **kwargs: Any) -> QuerySet[Property]:
        """
        Retrieve all inactive or under-maintenance, non-deleted properties.

        Returns:
            QuerySet[Property]: QuerySet containing properties with `is_deleted=False`
            and status in `[INACTIVE, UNDER_MAINTENANCE]`.
        """
        return self.filter(
            is_deleted=False,
            status__in=[
                PropertyAvailabilityStatus.INACTIVE.value[0],
                PropertyAvailabilityStatus.UNDER_MAINTENANCE.value[0]
            ],
            **kwargs
        )

    def deleted(self, **kwargs: Any) -> QuerySet[Property]:
        """
        Retrieve all deleted properties.

        Returns:
            QuerySet[Property]: QuerySet containing properties with `is_deleted=True`
            and status equal to `PropertyAvailabilityStatus.DELETED`.
        """
        return self.filter(is_deleted=True, status=PropertyAvailabilityStatus.DELETED.value[0], **kwargs)

    def not_deleted(self, **kwargs: Any) -> QuerySet[Property]:
        """
        Retrieve all properties that are not marked as deleted.

        Returns:
            QuerySet[Property]: QuerySet containing properties with `is_deleted=False`.
        """
        return self.filter(is_deleted=False, **kwargs)
