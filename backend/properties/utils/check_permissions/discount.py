from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Tuple

from django.db.models import QuerySet

if TYPE_CHECKING:
    from properties.models import User

from rest_framework.exceptions import PermissionDenied

from properties.models import Discount, LandlordProfile, Booking

from properties.utils.choices.landlord_profile import LandlordType, CompanyRole
from properties.utils.error_messages.permission import PERMISSION_ERRORS


class CheckDiscountPermission:
    """
    Base permission checker for discount-related actions.

    This utility class encapsulates common access validation logic
    for operations related to discounts and landlord profiles.

    It is responsible for:
    - Validating that the user has a supported landlord type
    - Verifying access to a LandlordProfile identified by `hash_id`
    - Restricting update operations to owners or company admins only

    The class does NOT perform any business logic or object mutations.
    It only validates access and, when required, returns verified objects.

    Attributes:
        user (User): The user performing the request.
        hash_id (str): Hash identifier of the target LandlordProfile.
    """

    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, user: User, hash_id: str) -> None:
        self.user = user
        self.hash_id = hash_id

    def _queryset_to_check(self, is_admin: bool = False) -> QuerySet[LandlordProfile]:
        """
        Build a base queryset for landlord profile access validation.

        The queryset is constructed based on:
        - The user's landlord type
        - Ownership of the landlord profile (for INDIVIDUAL / COMPANY)
        - Active company membership (for COMPANY_MEMBER)
        - Admin role requirement (if `is_admin=True`)

        Args:
            is_admin (bool): Whether admin-level access is required.
                             When True, COMPANY_MEMBER must have ADMIN role.

        Returns:
            QuerySet[LandlordProfile]: Queryset used for permission checks.

        Raises:
            PermissionDenied: If the user's landlord type is unsupported.
        """

        if self.user.landlord_type not in [self._INDIVIDUAL, self._COMPANY, self._COMPANY_MEMBER]:
            raise PermissionDenied(PERMISSION_ERRORS)

        if self.user.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            return LandlordProfile.objects.not_deleted(created_by_id=self.user.pk, hash_id=self.hash_id)
        else:
            filters: Dict[str, Any] = {
                'hash_id': self.hash_id,
                'company_memberships__user_id': self.user.pk,
                'company_memberships__is_active': True
            }

            if is_admin:
                filters['company_memberships__role'] = CompanyRole.ADMIN.value[0]

            return LandlordProfile.objects.not_deleted(**filters)

    def base_access(self) -> None:
        """
        Validate basic access to the landlord profile.

        This check is intended for read-only operations
        (e.g. listing discounts).

        Raises:
            PermissionDenied: If the user has no access to the profile.
        """
        if not self._queryset_to_check().exists():
            raise PermissionDenied(PERMISSION_ERRORS)

    def update_access(self) -> None:
        """
        Validate admin-level access to the landlord profile.

        This check is intended for mutating operations
        (e.g. create / update / delete discounts).

        Raises:
            PermissionDenied: If the user is not an owner or company admin.
        """
        if not self._queryset_to_check(is_admin=True).exists():
            raise PermissionDenied(PERMISSION_ERRORS)

    def get_landlord_profile(self) -> LandlordProfile:
        """
        Validate admin-level access and return the landlord profile.

        This method should be used when a verified LandlordProfile
        instance is required for further processing (e.g. serializer).

        Returns:
            LandlordProfile: Verified landlord profile instance.

        Raises:
            PermissionDenied: If access is denied.
        """
        landlord_profile: LandlordProfile = self._queryset_to_check(is_admin=True).first()

        if not landlord_profile:
            raise PermissionDenied(PERMISSION_ERRORS)

        return landlord_profile


class CheckDiscountPropertyPermission(CheckDiscountPermission):
    """
    Permission checker for DiscountProperty-related operations.

    Extends base discount permissions by additionally validating
    that a specific Discount exists and belongs to the verified
    landlord profile.

    This class is intended for create/update actions on
    DiscountProperty entities.
    """

    def get_landlord_profile_and_discount(self, discount_id: int) -> Tuple[LandlordProfile, Discount]:
        """
        Validate access and return landlord profile with discount.

        The method ensures that:
        - The user has admin-level access to the landlord profile
        - The discount exists and belongs to that profile
        - The discount is active

        Args:
            discount_id (int): Identifier of the discount.

        Returns:
            tuple[LandlordProfile, Discount]: Verified objects.

        Raises:
            PermissionDenied: If access rules are violated or objects do not exist.
        """
        landlord_profile: LandlordProfile = self.get_landlord_profile()

        discount: Discount = Discount.objects.active(
            id=discount_id, landlord_profile_id=landlord_profile.pk
        ).first()

        if not discount:
            raise PermissionDenied(PERMISSION_ERRORS)

        return landlord_profile, discount


class CheckDiscountUserPermission(CheckDiscountPermission):
    """
    Permission checker for applying discounts to users/bookings.

    Extends base discount permissions by validating:
    - Access to the landlord profile
    - Existence of the discount
    - Optional linkage to a booking owned by the landlord
    """

    def get_landlord_profile_discount_booking(self, discount_id: int, booking_number: str | None) -> Tuple[
        LandlordProfile, Discount, Booking
    ]:
        """
        Validate access and return landlord profile, discount and booking.

        The method ensures that:
        - The user has admin-level access to the landlord profile
        - The discount exists and belongs to that profile
        - If booking_number is provided, the booking exists
          and is owned by the landlord profile

        Args:
            discount_id (int): Identifier of the discount.
            booking_number (str | None): Optional booking reference.

        Returns:
            tuple[LandlordProfile, Discount, Booking | None]: Verified objects.

        Raises:
            PermissionDenied: If any validation step fails.
        """
        landlord_profile: LandlordProfile = self.get_landlord_profile()

        discount: Discount = Discount.objects.active(
            id=discount_id, landlord_profile_id=landlord_profile.pk
        ).first()

        if not discount:
            raise PermissionDenied(PERMISSION_ERRORS)

        booking: QuerySet[Booking] | None = None

        if booking_number:
            booking = Booking.objects.filter(
                booking_number=booking_number, property_ref__owner_id=landlord_profile.pk
            )

            if not booking:
                # raise ValidationError({'booking': DISCOUNT_USER_ERRORS['booking']})
                raise PermissionDenied(PERMISSION_ERRORS)

        return landlord_profile, discount, booking
