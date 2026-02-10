from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User, Property, CompanyMembership

from rest_framework.exceptions import PermissionDenied, NotFound

from properties.models import LandlordProfile
from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.error_messages.permission import PERMISSION_ERRORS


class CheckBookingCreatePermission:
    """
    Utility class for validating whether a user is allowed to create
    a booking for a specific `Property`.

    This class encapsulates the access rules applied before a booking
    can be created. The validation logic ensures:

        - Individual landlords cannot create bookings for their own properties.
        - The target property must exist and be active.
        - If the property does not exist or is not active, a `NotFound` exception is raised.

    If the user violates any rule, a `PermissionDenied` exception is raised.

    Attributes:
        user (User): The user attempting to create the booking.
        prop_id (int): The ID of the target `Property`.
    """

    def __init__(self, user: User, prop_id: int) -> None:
        self.user = user
        self.prop_id = prop_id

    def _check_create_permission(self) -> Property:
        """
        Internal method to validate booking creation permissions
        and retrieve the target property.

        Returns:
            Property: The active property for which the booking
            is being created.

        Raises:
            PermissionDenied: If an individual landlord attempts
            to book their own property.
            NotFound: If the property does not exist or is not active.
        """
        if self.user.is_landlord and self.user.landlord_type == LandlordType.INDIVIDUAL.value[0]:
            if Property.objects.filter(id=self.prop_id, owner__created_by_id=self.user.pk).exists():
                raise PermissionDenied(PERMISSION_ERRORS)

        prop: Property = Property.objects.active(id=self.prop_id).first()

        if not prop:
            raise NotFound(detail='Property not found.')

        return prop

    def check_and_get_property(self) -> Property:
        """
        Public method to validate permissions and safely retrieve
        the target property.

        Returns:
            Property: The validated active property instance.

        Raises:
            PermissionDenied: If the user is not allowed to create
            a booking for this property.
            NotFound: If the property does not exist or is not active.
        """
        return self._check_create_permission()


class CheckBookingPermission:
    """
    Utility class for validating whether a user has access to a specific
    `LandlordProfile` in the context of booking-related operations.

    This class encapsulates permission checks based on the user's landlord type
    and company membership. The validation rules are:

        - The user must have one of the allowed landlord types:
          INDIVIDUAL, COMPANY, or COMPANY_MEMBER.
        - INDIVIDUAL or COMPANY:
          The `LandlordProfile` must belong to the user.
        - COMPANY_MEMBER:
          The user must have an active (not deleted) membership
          in the target company profile.

    If the user does not satisfy the corresponding rule,
    a `PermissionDenied` exception is raised.

    Attributes:
        user (User): The user whose access is being validated.
        hash_id (str): The unique hash identifier of the `LandlordProfile`.
    """

    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, user: User, hash_id: str):
        self.user = user
        self.hash_id = hash_id

    def _check_permissions(self) -> None:
        """
        Internal method that validates access to the specified `LandlordProfile`.

        Validation rules:

        - User must have landlord type: INDIVIDUAL, COMPANY, or COMPANY_MEMBER.
        - INDIVIDUAL and COMPANY users must own the profile.
        - User must have an active company membership linked to the profile.

        Raises:
            PermissionDenied: If any of the validation checks fail.
        """
        if self.user.landlord_type not in [self._INDIVIDUAL, self._COMPANY, self._COMPANY_MEMBER]:
            raise PermissionDenied(PERMISSION_ERRORS)

        if self.user.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            if not LandlordProfile.objects.filter(created_by_id=self.user.pk, hash_id=self.hash_id).exists():
                raise PermissionDenied(PERMISSION_ERRORS)

        if not CompanyMembership.objects.not_deleted(
                user_id=self.user.pk, company__hash_id=self.hash_id, is_active=True
        ):
            raise PermissionDenied(PERMISSION_ERRORS)

    def execute(self) -> None:
        """
        Public method that triggers the permission validation.

        This method delegates the logic to `_check_permissions()`.

        Raises:
            PermissionDenied: If the user does not have access
            to the specified `LandlordProfile`.
        """
        self._check_permissions()
