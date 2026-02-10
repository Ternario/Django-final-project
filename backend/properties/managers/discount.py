from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from properties.models import Discount

from django.db.models import Manager, QuerySet

from properties.utils.choices.discount import DiscountStatus


class CustomDiscountManager(Manager):
    """
    Custom manager for the Discount model that provides helper methods
    to filter discounts based on their current status.

    Supports:
        - Retrieving active discounts.
        - Retrieving inactive discounts (expired or disabled).

    Methods:
        active(**kwargs) -> QuerySet[Discount]
            Returns all discounts with status ACTIVE.
        inactive(**kwargs) -> QuerySet[Discount]
            Returns all discounts with status EXPIRED or DISABLED.
    """

    def active(self, **kwargs: Any) -> QuerySet[Discount]:
        """
        Retrieve all active discounts.

        Returns:
            QuerySet[Discount]: QuerySet containing discounts where `status` is ACTIVE.
        """
        return self.filter(status__in=[DiscountStatus.ACTIVE.value[0], DiscountStatus.SCHEDULED.value[0]], **kwargs)

    def inactive(self, **kwargs: Any) -> QuerySet[Discount]:
        """
        Retrieve all inactive discounts (expired or disabled).

        Returns:
            QuerySet[Discount]: QuerySet containing discounts where `status` is EXPIRED or DISABLED.
        """
        return self.filter(status__in=[DiscountStatus.EXPIRED.value[0], DiscountStatus.DISABLED.value[0]], **kwargs)
