from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple

if TYPE_CHECKING:
    from properties.models import LandlordProfile, User
    from mypy.typeshed.stdlib.datetime import datetime

import logging
from django.utils.timezone import now

from base_config import settings
from properties.models import Booking, Property

logger = logging.getLogger(__name__)


class EmailResponseMixin:
    """
    A mixin providing helper methods for formatting and sending email messages.

    This class contains reusable logic shared between different response classes
    (e.g., SoftAdminResponse, SoftUserResponse). It is responsible for extracting
    model-specific data, formatting email message templates, generating booking
    links, and appending timestamps for logging and notifications.

    Typical usage involves extending this mixin in response classes to standardize
    email content generation.

    Methods:
        _get_landlord_profile_data(): Extract landlord/company details for properties.
        _get_profile_owner_data(): Retrieve owner information for landlord or company profiles.
        _set_message_data(): Format messages dynamically with model-specific context.
        _build_bookings_list(): Construct booking URLs for admin or user contexts.
        _get_message_datetime(): Provide formatted timestamp for error or log emails.
    """

    def _get_landlord_profile_data(self) -> Tuple[str, str, int]:
        """
        Extract profile details for a landlord associated with a property.

        Returns:
            Tuple[str, str, int]: A tuple containing:
                - str: Label ("Landlord profile").
                - str: Name of the landlord .
                - int: Primary key of the landlord or company profile.
        """
        model: Property = self.target_model

        by_profile: str = model.owner.type.lover()
        name: str = model.owner.name
        pk: int = model.owner.pk

        return by_profile, name, pk

    def _get_profile_owner_data(self) -> Tuple[str, str, int]:
        """
        Retrieve identifying information about the owner of a landlord profile.

        Returns:
            Tuple[str, str, int]: A tuple containing:
                - str: Owner's full name.
                - str: Owner's email address.
                - int: Primary key of the user who owns the profile.
        """
        model: LandlordProfile = self.target_model

        name: str = model.name
        email: str = model.created_by.email
        user_pk: int = model.created_by.pk

        return name, email, user_pk

    def _set_message_data(self, message: str) -> str:
        """
        Format an email message with model-specific data.

        Dynamically populates placeholders in the message template based on
        the type of target model (User, Property, LandlordProfile).

        Args:
            message (str): Message template containing placeholders.

        Returns:
            str: The fully formatted message string ready for sending.
        """
        if isinstance(self.target_model, User):
            context: Dict[str, str | int] = {
                'email': self.target_model.email,
                'pk': self.target_model.pk,
            }
        elif isinstance(self.target_model, Property):
            result: Tuple[str, str, int] = self._get_landlord_profile_data()
            by_profile, name, pk = result

            context: Dict[str, str | int] = {
                'title': self.target_model.title,
                'pk': self.target_model.pk,
                'by_profile': by_profile,
                'name': name,
                'profile_pk': pk
            }
        else:
            result_owner: Tuple[str, str, int] = self._get_profile_owner_data()
            name, email, user_pk = result_owner

            context: Dict[str, str | int] = {
                'name': name,
                'pk': self.target_model.pk,
                'email': email,
                'user_pk': user_pk
            }

        formatted_message: str = message.format(**context)
        return formatted_message

    @staticmethod
    def _build_bookings_list(bookings: List[Booking], same_user: bool, role: str | None = None) -> List[str]:
        """
        Build booking URLs based on the context (user or admin).

        Args:
            bookings (List[Booking]): List of Booking instances to generate URLs for.
            same_user (bool): True if the request was made by the booking owner, False if by an admin.
            role (str | None): The user role to include in API endpoints when same_user is True.

        Returns:
            List[str]: A list of booking URLs accessible by either user or admin.
        """
        if not same_user:
            return [f'{settings.SITE_URL}/admin/properties/booking/{booking.pk}/change/' for booking in bookings]
        else:
            return [f'{settings.SITE_URL}/api/v1/booking/{role}/{booking.pk}/' for booking in bookings]

    @staticmethod
    def _get_message_datetime() -> str:
        """
        Get the current timestamp formatted for inclusion in email messages.

        Returns:
            str: A string containing the occurrence time in the format "dd-mm-YYYY HH:MM:SS".
        """
        date_time_format: str = '%d-%m-%Y %H:%M:%S'
        time: datetime = now()
        return f'\nOccurrence time: {time.strftime(date_time_format)}'
