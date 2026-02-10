from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import Q

if TYPE_CHECKING:
    from properties.models import User
from rest_framework.exceptions import PermissionDenied

from properties.models import LandlordProfile, CompanyMembership
from properties.utils.choices.landlord_profile import LandlordType, CompanyRole
from properties.utils.error_messages.permission import PERMISSION_ERRORS


class CheckLandlordProfilePermission:
    """
    Utility class for validating whether a user has access to a specific
    `LandlordProfile` identified by its `hash_id`.

    This class performs permission checks without loading full database objects.
    It relies on efficient `EXISTS` queries to determine whether
    the user is allowed to access or change the given landlord profile.

    Access rules for reading/updating:

        - Individual landlord or company owner:
          The profile must be created by the user.

        - Company member:
          The user must have an active membership in the company profile.

    Access rules for profile update:

        - Only individual landlords or company owners can update their profiles.
        - Company members cannot update profiles, even if they have access.

    If the user does not satisfy the corresponding rule, a `PermissionDenied`
    exception is raised.

    Attributes:
        user (User): The user whose access is being validated.
        hash_id (str): The unique hash identifier of the `LandlordProfile`.
    """

    def __init__(self, user: User, hash_id: str):
        self.user = user
        self.hash_id = hash_id

    def _check_permissions(self) -> None:
        """
        Internal method that performs the permission check.

        This method executes database `EXISTS` queries to verify whether
        the user has access to the specified `LandlordProfile`.

        It does not return any value — it either completes successfully
        (meaning access is granted) or raises an exception.

        Raises:
            PermissionDenied:
                - If the user is not the creator of the profile (for individual or company landlords).
                - If the user does not have an active company membership (for company members).
                - If the user type is not recognized.
        """
        if self.user.landlord_type in [LandlordType.INDIVIDUAL.value[0], LandlordType.COMPANY.value[0]]:
            if not LandlordProfile.objects.not_deleted(created_by_id=self.user.pk, hash_id=self.hash_id).exists():
                raise PermissionDenied(PERMISSION_ERRORS)
            return

        if self.user.landlord_type == LandlordType.COMPANY_MEMBER.value[0]:
            if not CompanyMembership.objects.not_deleted(
                    company__hash_id=self.hash_id, user_id=self.user.pk, is_active=True
            ).exists():
                raise PermissionDenied(PERMISSION_ERRORS)
            return

        raise PermissionDenied(PERMISSION_ERRORS)

    def _check_update_permissions(self) -> None:
        """
        Internal method that performs update permission checks.

        Only individual landlords or company owners can update their profiles.
        Company members or other user types are not allowed to update.

        Raises:
            PermissionDenied:
                - If the user is not an individual landlord or company owner.
                - If the profile does not exist or was not created by the user.
        """
        if self.user.landlord_type not in [LandlordType.INDIVIDUAL.value[0], LandlordType.COMPANY.value[0]]:
            raise PermissionDenied(PERMISSION_ERRORS)

        if not LandlordProfile.objects.not_deleted(created_by_id=self.user.pk, hash_id=self.hash_id).exists():
            raise PermissionDenied(PERMISSION_ERRORS)

    def execute_check(self) -> None:
        """
         Public entry point for performing the permission check.

         This method delegates to `_check_permissions()` and propagates
         any `PermissionDenied` exception if access is not allowed.

         Returns:
             None

         Raises:
             PermissionDenied: If the user does not have access to the specified profile.
         """
        self._check_permissions()

    def execute_update(self) -> None:
        """
        Public entry point for performing update permission checks.

        Delegates to `_check_delete_permissions()` and propagates any
        `PermissionDenied` exception if update is not allowed.

        Returns:
            None

        Raises:
            PermissionDenied: If the user does not have permission to update the profile.
        """
        self._check_update_permissions()


class CheckCompanyMembershipPermissions:
    """
    Utility class for validating whether a user has access to a specific
    `CompanyMembership` object within a `LandlordProfile`.

    This class performs permission checks efficiently using `EXISTS` queries
    and avoids loading unnecessary database fields.

    Access rules for reading a membership (SAFE_METHODS):

        - LandlordProfile owner:
          Can access all memberships in the company.

        - Company admin:
          Can access all memberships in the company.

        - Membership owner (regular employee, not admin):
          Can only access their own membership object or see a limited
          list of admin memberships.

    Access rules for modifying or deleting a membership (unsafe methods):

        - LandlordProfile owner:
          Full access to modify or delete any membership in the company.

        - Company admin:
          Full access to modify or delete any membership in the company.

        - Membership owner (regular employee, not admin):
          Cannot modify or delete other memberships.

    If the user does not satisfy the corresponding rule, a `PermissionDenied`
    exception is raised.

    Attributes:
        user (User): The user whose access is being validated.
        hash_id (str): The unique hash identifier of the `LandlordProfile`.
    """

    def __init__(self, user: User, hash_id: str):
        self.user = user
        self.hash_id = hash_id

    def _check_landlord_type(self) -> None:
        """
        Internal helper to validate that the user has a landlord type that
        allows company membership access.

        Raises:
            PermissionDenied: If the user's landlord type is not COMPANY or COMPANY_MEMBER.
        """
        if self.user.landlord_type not in [LandlordType.COMPANY.value[0], LandlordType.COMPANY_MEMBER.value[0]]:
            raise PermissionDenied(PERMISSION_ERRORS)

    def _check_permissions(self) -> bool:
        """
        Internal method to check general access permissions for the user.

        Returns:
            bool: True if the user is the company owner or a company admin, False if the user is regular company member.

        Raises:
            PermissionDenied: If the user does not have access.
        """
        self._check_landlord_type()

        if self.user.landlord_type == LandlordType.COMPANY.value[0]:
            if not LandlordProfile.objects.not_deleted(created_by_id=self.user.pk, hash_id=self.hash_id).exists():
                raise PermissionDenied(PERMISSION_ERRORS)
            return True

        company_member: CompanyMembership = CompanyMembership.objects.not_deleted(
            company__hash_id=self.hash_id, user_id=self.user.pk, is_active=True
        ).first()

        if not company_member:
            raise PermissionDenied(PERMISSION_ERRORS)

        if company_member.role == CompanyRole.ADMIN.value[0]:
            return True

        return False

    def _check_create_permission(self) -> LandlordProfile:
        """
        Internal method to check general access to company memberships (non-object-specific).

        Returns:
            LandlordProfile: The landlord profile if access is granted.

        Raises:
            PermissionDenied: If the user does not have permission.
        """

        self._check_landlord_type()

        landlord_profile: LandlordProfile = LandlordProfile.objects.get(hash_id=self.hash_id)

        if self.user.pk == landlord_profile.created_by_id:
            return landlord_profile

        if CompanyMembership.objects.not_deleted(
                company_id=landlord_profile.pk, user_id=self.user.pk, role=CompanyRole.ADMIN.value[0], is_active=True
        ).exists():
            return landlord_profile

        raise PermissionDenied(PERMISSION_ERRORS)

    def _check_instance_permissions(self, member_id: int):
        """
        Internal method to check object-level access to a specific CompanyMembership.

        Raises:
            PermissionDenied: If the user is not the company owner, not the membership owner,
            and not a company admin.
        """
        self._check_landlord_type()

        if self.user.landlord_type == LandlordType.COMPANY.value[0]:
            if not LandlordProfile.objects.not_deleted(
                    created_by_id=self.user.pk, hash_id=self.hash_id,
                    company_memberships__user_id=member_id
            ).exists():
                raise PermissionDenied(PERMISSION_ERRORS)
            return

        if not CompanyMembership.objects.not_deleted(
                company__hash_id=self.hash_id, user_id=self.user.pk, is_active=True
        ).filter(
            Q(id=member_id) | Q(role=CompanyRole.ADMIN.value[0])
        ).exists():
            raise PermissionDenied(PERMISSION_ERRORS)
        return

    def access_by_role(self) -> bool:
        """
        Public method to check general access to company memberships.

        Returns:
            bool: True if access is granted, False if access is not granted.

        Raises:
            PermissionDenied: If the user does not have permission.
        """

        return self._check_permissions()

    def access_create(self) -> LandlordProfile:
        """
        Public method to check access to create company memberships.

        Returns:
            LandlordProfile: LandlordProfile if access is granted.

        Raises:
            PermissionDenied: If the user does not have permission
            or if the profile does not exist.
        """
        try:
            return self._check_create_permission()
        except LandlordProfile.DoesNotExist:
            raise PermissionDenied(PERMISSION_ERRORS)

    def access_instance(self, member_id: int) -> None:
        """
        Public method to check object-level access to a specific membership.

        Args:
            member_id (int): The ID of the CompanyMembership to check access for.

        Raises:
            PermissionDenied: If the user does not have access to the object
            or if the associated LandlordProfile does not exist.
        """
        self._check_instance_permissions(member_id)

    def access_update_instance(self) -> None:
        """
        Public method to check permissions for updating any membership in the company.

        Note: Unlike `access_instance()`, this method does not accept a specific
        membership ID because regular employees (non-admins) cannot update any
        membership at all, even their own.

        Raises:
            PermissionDenied: If the user is not a company owner or admin.
        """
        if not self._check_permissions():
            raise PermissionDenied(PERMISSION_ERRORS)
