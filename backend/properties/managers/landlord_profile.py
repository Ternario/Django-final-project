from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import LandlordProfile, CompanyMembership
    from django.db.models import QuerySet

from django.db.models import Manager


class CustomLandlordProfileManager(Manager):
    """
    Custom manager for the LandlordProfile model that provides utility methods
    for filtering profiles based on their deletion status.

    Supports:
        - Filtering out soft-deleted profiles using the `not_deleted` method.

    Methods:
        not_deleted(kwargs: Any) -> QuerySet[LandlordProfile]
            Returns all LandlordProfile instances that are not marked as deleted,
            optionally applying additional filters passed via kwargs.
    """

    def not_deleted(self, **kwargs: Any) -> QuerySet[LandlordProfile]:
        """
        Retrieve all LandlordProfile instances that are not soft-deleted.

        This method filters the queryset to exclude any profiles where
        'is_deleted' is True, while allowing additional filtering
        through kwargs.

        Args:
            kwargs (Any): Additional filter parameters to apply.

        Returns:
            QuerySet[LandlordProfile]: QuerySet containing all non-deleted LandlordProfile instances
            that match the additional filters.
        """
        return self.filter(is_deleted=False, **kwargs)


class CustomCompanyMembershipManager(Manager):
    """
    Custom manager for the CompanyMembership model that provides utility methods
    for filtering profiles based on their deletion status.

    Supports:
        - Filtering out soft-deleted profiles using the `not_deleted` method.

    Methods:
        not_deleted(kwargs: Any) -> QuerySet[CompanyMembership]
            Returns all CompanyMembership instances that are not marked as deleted,
            optionally applying additional filters passed via kwargs.
    """

    def not_deleted(self, **kwargs: Any) -> QuerySet[CompanyMembership]:
        """
        Retrieve all CompanyMembership instances that are not soft-deleted.

        This method filters the queryset to exclude any profiles where
        'is_deleted' is True, while allowing additional filtering
        through kwargs.

        Args:
            kwargs (Any): Additional filter parameters to apply.

        Returns:
            QuerySet[CompanyMembership]: QuerySet containing all non-deleted CompanyMembership instances
            that match the additional filters.
        """
        return self.filter(is_deleted=False, **kwargs)
