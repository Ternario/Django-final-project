from __future__ import annotations
from typing import List

import logging

from properties.models import Booking, Property, LandlordProfile, DeletionLog, CompanyMembership

logger = logging.getLogger(__name__)


class CascadeActionsMixin:
    """
    A mixin providing reusable methods to check for active bookings related to a user.

    This class centralizes logic for retrieving landlord profiles and determining
    active bookings either made by the user (as a guest) or associated with
    properties owned by their landlord profile(s).

    It is intended to be used in deletion or privacy workflows to prevent removal
    of users that still have active bookings linked either directly or through
    landlord-owned properties.

    Methods:
        _manage_if_landlord():
            Retrieve landlord profile(s) if the user has a landlord role.
        _check_active_bookings():
            Aggregate active bookings related to the user or their properties.
        _get_active_property_booking():
            Retrieve active bookings linked to properties owned by a specific landlord profile.
        _get_active_property_list_booking():
            Retrieve active bookings across all landlord profiles associated with the user.
        _handle_company_membership():
            Log company membership records linked to the user.
    """
    def _manage_if_landlord(self) -> List[LandlordProfile]:
        """
        Determine and retrieve landlord profile(s) if the user is a landlord.

        Returns:
            List[LandlordProfile]:
                - Landlord profile(s) created by the user if the user has a landlord
                  role with type INDIVIDUAL or COMPANY.
                - Empty list if the user is not a landlord or does not match
                  supported landlord types.
        """
        if self.is_landlord and self.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            return list(LandlordProfile.objects.filter(created_by=self.target_model.pk))
        return []

    def _check_active_bookings(self) -> List[Booking]:
        """
        Aggregate all active bookings related to the user.

        Includes:
            - Bookings where the user is a guest.
            - Bookings linked to properties owned by the user's landlord profile(s),
              if the user is a landlord.

        Returns:
            List[Booking]: Active bookings that may prevent depersonalization.
        """
        active_bookings: List[Booking] = list(Booking.objects.active(guest_id=self.target_model.pk))

        if self.is_landlord and self.landlord_profile:
            properties_bookings: List[Booking] = self._get_active_property_list_booking()

            if properties_bookings:
                active_bookings.extend(properties_bookings)

        return active_bookings

    @staticmethod
    def _get_active_property_booking(landlord_profile: LandlordProfile) -> List[Booking]:
        """
        Retrieve active bookings associated with properties owned by a landlord profile.

        Args:
            landlord_profile (LandlordProfile):
                The landlord profile whose properties are checked for active bookings.

        Returns:
            List[Booking]: Active bookings associated with the landlord's properties.
        """
        properties_list: List[Property] = Property.objects.active(owner_id=landlord_profile.pk)

        if not properties_list:
            return []

        return list(Booking.objects.active(property_ref__in=properties_list))

    def _get_active_property_list_booking(self) -> List[Booking]:
        """
        Retrieve active bookings across properties for all landlord profiles of the user.

        If the user has multiple landlord profiles (e.g. company-related profiles),
        bookings are aggregated across all profiles.

        Returns:
            List[Booking]: Active bookings linked to properties owned by the user's landlord profiles.
        """
        if len(self.landlord_profile) > 1:
            properties_bookings: List[Booking] = []

            for company in self.landlord_profile:
                company_prop_list: List[Booking] = self._get_active_property_booking(company)
                properties_bookings.extend(company_prop_list)
        else:
            properties_bookings: List[Booking] = self._get_active_property_booking(self.landlord_profile[0])

        return properties_bookings

    def _handle_company_membership(self, parent_log: DeletionLog) -> None:
        """
        Log all company membership records associated with the user.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach company membership logs to.
        """
        membership_list: List[CompanyMembership] = CompanyMembership.objects.filter(user_id=self.target_model.pk)

        if membership_list:
            self.log_model.list_handler(membership_list, parent_log)
