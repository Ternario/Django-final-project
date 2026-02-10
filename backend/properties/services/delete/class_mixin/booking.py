from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from properties.models import LandlordProfile

import logging

from properties.models import Booking, Property

logger = logging.getLogger(__name__)


class BookingCheckMixin:
    """
    A mixin providing reusable methods to check for active bookings related to a user.

    This class centralizes logic for retrieving landlord profiles and determining
    active bookings either made by the user (as a guest) or associated with their
    landlord or company properties.

    It is intended to be used in deletion or privacy workflows to prevent removal
    of users, landlords, companies, or properties that still have active bookings.

    Methods:
        _get_landlord_profile():
            Retrieve the landlord profile(s) (individual or company) for the user.
        _get_active_bookings():
            Retrieve active bookings where the user is the guest.
        _get_active_property_booking():
            Retrieve active bookings linked to a specific landlord profile's properties.
        _get_active_property_list_booking():
            Retrieve active bookings across all properties for individual or company landlords.
    """

    def _get_landlord_profile(self) -> LandlordProfile | List[LandlordProfile] | None:
        """
        Retrieve the user's landlord profile(s) based on their landlord type.

        Returns:
            LandlordProfile | List[LandlordProfile] | None:
                - LandlordProfile if the user has an individual landlord profile.
                - List[LandlordProfile] if the user has company profiles.
                - None if no landlord profile exists.

        Raises:
            RuntimeError: If the user is expected to have a company profile but none exists.
        """
        if not self.target_model.landlord_type:
            return None

        landlord_profile: List[LandlordProfile] = self.target_model.landlord_profiles.all()

        if not landlord_profile:
            raise RuntimeError(
                f'Missing Company Profile for user {self.target_model.pk}'
            )
        return landlord_profile

    def _get_active_bookings(self) -> List[Booking]:
        """
        Retrieve all active bookings for the user.

        Returns:
            List[Booking]: A list of active bookings where the user is the guest.
        """
        return list(Booking.objects.active(guest=self.target_model))

    @staticmethod
    def _get_active_property_booking(landlord_profile: LandlordProfile) -> List[Booking]:
        """
        Retrieve all active bookings associated with properties of the given landlord profile.

        Args:
            landlord_profile (LandlordProfile):
                The landlord profile (individual or company) whose properties are being checked.

        Returns:
            List[Booking]: A list of active bookings associated with the landlord's properties.
        """
        properties_list: List[Property] = Property.objects.active(owner=landlord_profile)

        if not properties_list:
            return []

        return list(Booking.objects.active(property_ref__in=properties_list))

    def _get_active_property_list_booking(self) -> List[Booking]:
        """
        Retrieve all active bookings across properties for all landlord profiles of the user.

        If the user has an individual landlord profile, returns bookings for those properties.
        If the user has company landlord profiles, aggregates bookings across all companies.

        Returns:
            List[Booking]: A list of active bookings associated with the user's landlord properties.
        """
        if isinstance(self.landlord_profile, list):
            properties_bookings: List[Booking] = []

            for company in self.landlord_profile:
                company_prop_list: List[Booking] = self._get_active_property_booking(company)
                properties_bookings.extend(company_prop_list)
        else:
            properties_bookings: List[Booking] = self._get_active_property_booking(self.landlord_profile)

        return properties_bookings
